# Research: subset-b-001293

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp.c -->
## sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp.c

Purpose: this file is the Linux firmware transport and exported helper layer for Xilinx/AMD ZynqMP, Versal, and Versal Net platform-management firmware. It selects the firmware conduit from device tree (`method = "smc"` or `"hvc"`), wraps SMCCC calls, translates firmware status values to Linux errno, exposes many `zynqmp_pm_*` APIs to other kernel drivers, and registers the firmware node as an MFD parent plus OF children.

Important APIs, types, and functions: `zynqmp_pm_invoke_fn()` and `zynqmp_pm_invoke_fw_fn()` are the central call packers. They validate argument counts, check API support, pack 32-bit firmware arguments into 64-bit SMCCC registers, and call the selected `do_fw_call` backend. `do_fw_call_smc()` and `do_fw_call_hvc()` perform the actual secure-monitor or hypervisor call and unpack up to seven returned 32-bit words. `zynqmp_pm_feature()` and `zynqmp_pm_is_function_supported()` cache feature-check results in `pm_api_features_map` and maintain IOCTL/QUERY function bitmaps. Exported wrappers cover clocks, PLL fractional settings, SD tap delays, resets, FPGA load/status/config-status, pinctrl, boot mode, power domains, RPU/TCM configuration, notifiers, efuse access, secure register access, SD/GEM config, and PDI loading.

Control flow: probe reads the conduit method, stores platform family match data, obtains SiP service, PM API, and TrustZone versions, enables feature-check mode when firmware supports it, creates `zynqmp_power_controller`, initializes debugfs, optionally registers `xlnx_event_manager` on non-ZynqMP platforms, and populates child OF devices. `sync_state` finalizes firmware power-management ownership after genpd sync for the ZynqMP compatible. Removal tears down MFD/debugfs, frees feature-cache hash entries, and unregisters the event-manager device.

State and persistence: persistent kernel state includes selected conduit function pointer, cached API/TZ/SiP versions, feature-check hash entries, supported IOCTL/QUERY masks, active platform family data, and sysfs-selected shutdown scope. Firmware-backed GGS and PGGS sysfs files read/write global storage registers, with PGGS intended to persist across reset domains as defined by firmware. Feature config sysfs stores a selected config ID in `struct zynqmp_devinfo` and then gets/sets its value through firmware.

Dependencies and integration points: the driver depends on ARM SMCCC, OF platform data, MFD, PM domains, Xilinx firmware headers, and Xilinx event/debug helpers. Other drivers integrate through the exported `zynqmp_pm_*` symbols, especially FPGA managers (`zynqmp_pm_fpga_load()`), clocks/resets/pinctrl, and power-domain providers. The firmware node uses compatible strings for ZynqMP, Versal, and Versal Net, each carrying a family code.

Risks: `do_feature_check_call()` allocates with `GFP_ATOMIC` and updates a global hash without an explicit lock, so concurrent first-time feature checks could race if callers arrive before probe-time serialization is complete. Many wrappers trust firmware payload layout and write output pointers after invocation; callers must pass valid output storage. `zynqmp_pm_get_rpu_mode()` compares the already-normalized Linux return code with `XST_PM_SUCCESS`, which is zero today but is easy to misread. Sysfs GGS/PGGS stores return `-EFAULT` for parse or firmware failures instead of the original errno. Probe panics on too-old firmware versions, making version compatibility a hard boot gate.

Test signals: useful checks include booting DT nodes with both SMC and HVC methods, verifying exported wrapper failures when firmware reports unsupported APIs, checking feature-check cache behavior for PM/TF-A/non-PM module IDs, exercising GGS/PGGS/sysfs feature-config reads and writes, and validating FPGA load/status wrappers with full and partial bitstreams. Probe tests should cover missing/invalid `method`, unsupported firmware versions, MFD registration failure, and event-manager registration on Versal-family matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/fpga/Kconfig

Purpose: this Kconfig file defines the FPGA framework build surface: the core manager framework, manager drivers, bridge drivers, regions, Device Feature List support, PCI/NIOS/MAX10 support, and vendor-specific programming drivers.

Important configuration APIs: `menuconfig FPGA` gates the whole framework. `FPGA_BRIDGE`, `FPGA_REGION`, and `OF_FPGA_REGION` layer higher-level reconfiguration abstractions on top of managers. `FPGA_DFL` selects bridge and region support and enables DFL enumeration infrastructure. `FPGA_DFL_FME`, `FPGA_DFL_FME_MGR`, `FPGA_DFL_FME_BRIDGE`, `FPGA_DFL_FME_REGION`, and `FPGA_DFL_AFU` split Intel DFL support into management engine, partial-reconfiguration manager/bridge/region, and user AFU port pieces.

Control flow and integration: each symbol controls object inclusion in `drivers/fpga/Makefile`. Dependencies encode platform and subsystem requirements: SPI-backed managers depend on `SPI`, syscon/regmap users select or depend on `REGMAP_MMIO`, DFL FME requires `HWMON` and `PERF_EVENTS`, and ZynqMP FPGA manager depends on `ZYNQMP_FIRMWARE` except under compile testing. The structure lets a kernel include only the core FPGA class, add bridge/region orchestration, or pull in vendor drivers as needed.

State and persistence behavior: Kconfig itself has no runtime state, but it determines ABI availability. Enabling DFL AFU or FME creates char-device ioctls and sysfs groups at runtime; enabling manager and bridge drivers creates firmware-loading and bridge-control surfaces. Choice of built-in versus module affects probe ordering and whether platform firmware dependencies must be present during early boot.

Dependencies and risks: dependencies are mostly explicit, but cross-symbol behavior matters. `FPGA_DFL` selects `FPGA_BRIDGE` and `FPGA_REGION`, but the FME manager/bridge/region subdrivers remain separately selectable. `FPGA_DFL_FME` requiring both `HWMON` and `PERF_EVENTS` means minimal systems without those frameworks cannot build FME even if they only need header or PR management. Incorrect config combinations can leave DFL PR management present without the child manager/bridge/region drivers that users expect.

Test signals: build coverage should include `allmodconfig`, `COMPILE_TEST`, DFL built-in versus module permutations, and platform-specific configs for Xilinx firmware-backed managers, Altera SoCFPGA bridges, SPI managers, and MAX10 secure update. Runtime tests should confirm expected module aliases and that selecting a feature pulls in all required framework classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/Makefile -->
## sources/distributed-fs/ceph-client/drivers/fpga/Makefile

Purpose: this Makefile maps FPGA Kconfig symbols to kernel objects and composes the multi-object Intel DFL FME and AFU drivers.

Important build entries: `obj-$(CONFIG_FPGA)` builds `fpga-mgr.o`; manager drivers include Altera CvP/passive-serial/SoCFPGA, Xilinx core/selectmap/SPI/Zynq/ZynqMP/Versal, Lattice, Microchip, TS73xx, and PR-IP core objects. Bridge entries build `fpga-bridge.o`, SoCFPGA bridges, freeze bridge, and Xilinx PR decoupler. Region entries build `fpga-region.o` and `of-fpga-region.o`. DFL entries build `dfl.o`, FME child drivers, AFU, PCI, N3000 Nios, and tests.

Control flow and integration: the object list mirrors the layered FPGA framework: core manager class, concrete managers, bridge class, bridge drivers, region class, DFL enumeration, then DFL feature devices. `dfl-fme-objs` aggregates `dfl-fme-main.o`, `dfl-fme-pr.o`, `dfl-fme-error.o`, and `dfl-fme-perf.o` into the FME module. `dfl-afu-objs` aggregates AFU main, MMIO region, DMA region, and error reporting into one AFU module.

State and persistence behavior: the file has no runtime state, but object composition defines symbol visibility and module init order. Splitting DFL FME into one compound object means PR, error, thermal/power, perf, and header feature operations are registered together by the FME platform driver, while manager/bridge/region helper drivers are separate modules.

Dependencies and risks: the Makefile assumes Kconfig dependencies prevent missing-framework builds. If a new DFL subfeature source is added without updating compound object lists, it will silently be omitted from the module. Conversely, adding an object under the wrong config can expose symbols or module aliases when the associated framework is unavailable.

Test signals: verify `make drivers/fpga/` with modular and built-in DFL combinations, inspect generated modules for expected aliases (`dfl-fme`, `dfl-port`, `dfl-fme-mgr`, `dfl-fme-bridge`, `dfl-fme-region`), and confirm KUnit test object inclusion only under `CONFIG_FPGA_KUNIT_TESTS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-cvp.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/altera-cvp.c

Purpose: this is an FPGA manager driver for Intel/Altera Configuration via Protocol over PCIe. It programs full RBF bitstreams through the device's PCI Vendor Specific Extended Capability and, when available, BAR0 memory writes.

Important APIs and functions: `struct altera_cvp_conf` stores the PCI device, mapped BAR, VSEC offset, selected write method, manager name, packet counters, and version-specific operations. `struct cvp_priv` distinguishes V1 and V2 behavior: V1 uses dummy writes and 4-byte blocks, while V2 uses a credit register and 4 KiB blocks. FPGA manager callbacks are `altera_cvp_state()`, `altera_cvp_write_init()`, `altera_cvp_write()`, and `altera_cvp_write_complete()`. The driver also exposes a driver sysfs attribute `chkcfg` to enable optional configuration-error checks.

Control flow: probe finds the Altera VSEC ID, verifies CvP enablement, enables PCI memory space directly through the command register, requests BAR0, selects BAR MMIO writes or config-space writes as a fallback, selects V1/V2 private ops, and registers an FPGA manager. Programming rejects partial reconfiguration, derives `numclks` from compressed/encrypted flags, switches clock and mode bits, clears stale state, sets `CVP_CONFIG`, waits for `CFG_RDY`, starts transfer, streams blocks while respecting credits, tears down control bits, checks latched errors, clears CvP mode, and waits for user mode.

State and persistence: runtime state includes global `altera_cvp_chkcfg`, per-device sent packet count, `numclks`, VSEC offset, BAR mapping, and selected write path. Hardware state is held in VSEC status/control/error registers and may survive failed programming until teardown or `clear_state()` runs.

Dependencies and integration: it integrates with PCI core, the FPGA manager framework, PCI config-space VSEC accessors, optional BAR IO mapping, and module init/exit for both PCI driver registration and driver sysfs attribute lifetime.

Risks: the PCI ID table matches any Altera vendor device, so VSEC validation is critical. Directly enabling/disabling PCI memory space bypasses `pci_enable_device()` to handle unassigned large BARs, but removal clears the memory bit even if it was enabled before probe. Buffer casts to `u32 *` assume data alignment tolerated by architecture. V2 credit accounting stores `sent_packets` in `u32` but compares with an 8-bit credit value, relying on wrap behavior. Optional error checking is global across all devices.

Test signals: test VSEC-missing and CvP-disabled probe failures, BAR mapping fallback to config-space writes, V1 and V2 devices, compressed/encrypted clock ratio flags, large images crossing multiple credit windows, latched error paths, usermode timeout, and `chkcfg` sysfs toggling during programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-cvp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-fpga2sdram.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/altera-fpga2sdram.c

Purpose: this bridge driver controls the Altera SoCFPGA FPGA-to-SDRAM bridge. It does not reconfigure SDRAM port layout; it only enables or disables the port-reset mask captured by pre-Linux handoff.

Important APIs and functions: `struct alt_fpga2sdram_data` holds the SDR controller regmap and active port mask. `alt_fpga2sdram_enable_show()` reads `ALT_SDR_CTL_FPGAPORTRST_OFST` and reports whether all configured mask bits are set. `_alt_fpga2sdram_enable_set()` updates only the handoff mask bits. The registered `fpga_bridge_ops` provide `enable_set` and `enable_show`.

Control flow: probe allocates private data, looks up `altr,sdr-ctl` and `altr,sys-mgr` syscon regmaps, reads `SYSMGR_ISWGRP_HANDOFF3` for the FPGA-to-SDRAM mask, registers an FPGA bridge named `fpga2sdram`, and optionally applies the `bridge-enable` DT property. Remove unregisters the bridge.

State and persistence: the mask comes from a system-manager handoff register populated by firmware or bootloader and is treated as the persistent SDRAM port configuration. Runtime bridge state is the SDR controller reset bits. No local software shadow is used.

Dependencies and integration: it depends on syscon/regmap, OF compatible `altr,socfpga-fpga2sdram-bridge`, and the FPGA bridge framework. FPGA regions use it to stop FPGA-originated SDRAM traffic before reprogramming.

Risks: if boot firmware provides a stale or zero handoff mask, Linux will expose a bridge that controls the wrong ports or no ports. `bridge-enable` values greater than one are warned and ignored, so board DT mistakes may leave hardware in firmware-provided state. The driver assumes syscon compatibles are globally unique and accessible.

Test signals: verify probe with valid and missing syscon nodes, correct mask load from handoff register, `bridge-enable = <0>` and `<1>` behavior, sysfs bridge enable state, and safe disable/enable around FPGA reconfiguration while SDRAM accesses are quiesced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-fpga2sdram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-freeze-bridge.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/altera-freeze-bridge.c

Purpose: this FPGA bridge driver controls an Altera freeze bridge in FPGA fabric, isolating a reconfigurable region from buses during partial reconfiguration.

Important APIs and functions: `struct altera_freeze_br_data` tracks MMIO base and cached enable state. `altera_freeze_br_do_freeze()` issues `FREEZE_REQ`, waits for `FREEZE_REQ_DONE`, then asserts `RESET_REQ`. `altera_freeze_br_do_unfreeze()` clears control, issues `UNFREEZE_REQ`, and waits for `UNFREEZE_REQ_DONE`. `altera_freeze_br_req_ack()` polls status and illegal-request registers. `altera_freeze_br_enable_set()` maps FPGA bridge enable semantics to freeze/unfreeze operations and uses image-info timeouts when present.

Control flow: probe requires an OF node, maps resource 0, validates bridge CSR version against supported or official values, initializes cached enable state from status, registers an FPGA bridge named `freeze`, and stores it as driver data. Remove unregisters the bridge.

State and persistence: hardware state lives in the CSR status/control/illegal-request registers. The cached `enable` boolean is updated only after successful operations and is returned by `enable_show()`. Illegal request status is cleared by writing one to the illegal-request register.

Dependencies and integration: it depends on MMIO, platform devices, OF compatible `altr,freeze-bridge-controller`, and the FPGA bridge framework. It participates in `fpga_region` bridge lists during partial reconfiguration.

Risks: timeout defaults to zero if no `fpga_image_info` is attached, resulting in only one poll iteration. `enable_show()` returns cached state, not a fresh CSR read after probe. Illegal-request clearing assumes write-one behavior and only logs if clearing fails. The driver rejects unexpected versions, so compatible hardware revisions require updates.

Test signals: validate freeze/unfreeze from all legal starting states, illegal-request reporting and clearing, timeout behavior with image-specific enable/disable timeouts, revision rejection, and bridge state after failed operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-freeze-bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-hps2fpga.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/altera-hps2fpga.c

Purpose: this driver manages Altera SoCFPGA bridges between the host processor system and FPGA fabric: HPS-to-FPGA, lightweight HPS-to-FPGA, and FPGA-to-HPS. It enables/disables bridges by reset control and, for HPS-visible bridges, updates L3 remap visibility bits.

Important APIs and functions: `struct altera_hps2fpga_data` carries bridge name, reset control, optional L3 regmap and remap mask, and clock. `_alt_hps2fpga_enable_set()` asserts or deasserts bridge reset and updates the write-only L3 remap register through a global shadow protected by `l3_remap_lock`. FPGA bridge callbacks are `alt_hps2fpga_enable_set()` and `alt_hps2fpga_enable_show()`.

Control flow: OF match data provides one of three static bridge templates. Probe obtains an exclusive reset control, optional `altr,l3regs` syscon for remapped bridges, a clock, enables the clock, optionally applies `bridge-enable`, registers the FPGA bridge, and stores it as driver data. Remove unregisters the bridge and disables the clock.

State and persistence: bridge state is mostly hardware reset state plus `l3_remap_shadow` because the L3 remap register is write-only. The static match-data structures are mutated per probed device, so each compatible effectively shares template storage.

Dependencies and integration: it integrates with reset controller, clock framework, syscon/regmap, OF property APIs, and FPGA bridge framework. FPGA regions rely on these bridges to isolate fabric from HPS traffic before reconfiguration.

Risks: static match-data mutation can be fragile if multiple devices of the same compatible exist, because fields such as reset, regmap, and clock are shared. `enable_show()` returns `reset_control_status()`, whose semantics may be reset-asserted rather than bridge-enabled depending on reset provider. L3 shadow starts at zero and may not reflect bootloader state until a bridge operation occurs. Missing `bridge-enable` leaves hardware in its existing state.

Test signals: cover all three compatibles, clock/reset failure unwinds, remap shadow updates under concurrent bridge toggles, `bridge-enable` application, and repeated enable/disable cycles while checking L3 visibility and reset status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-hps2fpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-pr-ip-core-plat.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/altera-pr-ip-core-plat.c

Purpose: this small platform driver binds the generic Altera Partial Reconfiguration IP core implementation to OF-described MMIO devices.

Important APIs and functions: `alt_pr_platform_probe()` maps resource 0 with `devm_platform_ioremap_resource()` and passes the base address to `alt_pr_register()`. The OF table matches `altr,a10-pr-ip`.

Control flow: once a matching platform device probes, the driver maps the first MMIO resource and lets `altera-pr-ip-core.c` allocate private state and register an FPGA manager. There is no explicit remove path because all allocations and registration are devm-managed by the core register helper.

State and persistence: this wrapper has no independent runtime state. The associated FPGA manager state is stored by the core driver and hardware CSR registers.

Dependencies and integration: it depends on platform devices, OF matching, MMIO resource mapping, and the exported `alt_pr_register()` API from the core PR IP driver. Kconfig requires `ALTERA_PR_IP_CORE`, `OF`, and `HAS_IOMEM`.

Risks: the driver assumes the first resource is the PR IP CSR/data aperture. DT mistakes map directly into wrong MMIO access. It does not validate register revision or status before registration beyond the debug read performed in the core.

Test signals: test probe with missing resource, valid `altr,a10-pr-ip` DT node, deferred or failed MMIO mapping, and successful FPGA manager registration visible under the FPGA manager class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-pr-ip-core-plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-pr-ip-core.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/altera-pr-ip-core.c

Purpose: this file implements the FPGA manager operations for the Altera Arria 10 Partial Reconfiguration IP core. It streams partial bitstreams into a data register and monitors a CSR status field.

Important APIs and functions: `struct alt_pr_priv` stores the MMIO base. `alt_pr_fpga_state()` maps CSR status codes to FPGA manager states and logs error statuses. `alt_pr_fpga_write_init()` requires `FPGA_MGR_PARTIAL_RECONFIG`, rejects already-started PR, and sets `PR_START`. `alt_pr_fpga_write()` writes 32-bit chunks plus masked trailing bytes to `ALT_PR_DATA_OFST` and checks for write errors. `alt_pr_fpga_write_complete()` polls until operating or timeout. `alt_pr_register()` registers a devm FPGA manager and is exported for bus wrappers.

Control flow: registration allocates private state, records the base, reads CSR for debug, and registers manager ops. Programming starts by asserting `PR_START`, streams the buffer to the data register, then loops with 1 microsecond delays until the CSR reports success, error, or `config_complete_timeout_us` expires.

State and persistence: hardware state is entirely in the PR IP CSR and data registers. The driver has no software buffering and no persistent state beyond MMIO base. FPGA manager state is derived from the live CSR each time.

Dependencies and integration: it integrates with the FPGA manager framework and is exported to `altera-pr-ip-core-plat.c` or any other bus-specific wrapper. Image info flags and timeouts are supplied by the FPGA manager/region users.

Risks: `buf` is cast to `u32 *`, so unaligned bitstreams can be a problem on strict-alignment architectures. Partial trailing-byte handling reads from the next `u32` slot after the full chunks, which assumes the buffer has readable padding. The code does not clear `PR_START` after completion; hardware is expected to manage state. It accepts any nonzero count less than four as a valid final partial word.

Test signals: test missing partial-reconfig flag, already-started CSR bit, all CSR error codes, odd-sized buffers, timeout behavior, and successful PR with manager state transitioning to operating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-pr-ip-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-ps-spi.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/altera-ps-spi.c

Purpose: this FPGA manager programs Altera FPGAs over passive-serial SPI using `nconfig`, `nstat`, and optional `confd` GPIOs. It supports Cyclone V compatible timing and Arria 10 timing.

Important APIs and functions: `struct altera_ps_data` captures per-family timing values. `struct altera_ps_conf` stores GPIO descriptors, SPI device, selected timing data, image flags, and manager name. Manager callbacks are `altera_ps_state()`, `altera_ps_write_init()`, `altera_ps_write()`, and `altera_ps_write_complete()`. `rev_buf()` bit-reverses firmware data unless the image is already LSB-first.

Control flow: probe selects match data, acquires `nconfig` output, `nstat` input, optional `confd` input, and registers a devm FPGA manager. Programming rejects partial reconfiguration, pulses `nconfig`, waits for `nstat` to indicate reset and then readiness, delays for timing requirements, streams the bitstream over SPI in 4 KiB chunks with bit reversal when needed, checks `nstat` and optional `confd`, and sends one dummy byte to provide extra DCLK edges for user mode entry.

State and persistence: software state includes last image flags and static per-family timing. Hardware state is represented by GPIO lines and FPGA configuration state. The write path mutates the firmware buffer in-place during bit reversal.

Dependencies and integration: it depends on SPI, GPIO descriptors, OF/SPI device IDs, `BITREVERSE`, and the FPGA manager framework. Firmware images are expected in binary RBF format.

Risks: in-place bit reversal means a shared or reused firmware buffer is modified. `altera_ps_state()` only distinguishes reset when `nstat` is high, otherwise unknown. Timing loops depend on board GPIO polarity conventions matching descriptor names. Optional `confd` absence is only a warning, reducing final configuration confidence.

Test signals: exercise Cyclone/Stratix-compatible and Arria 10 timing paths, partial-reconfig rejection, `nstat` stuck-high/stuck-low failures, optional `confd` failure, SPI write errors, LSB-first and bit-reversed image flags, and odd chunk sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/altera-ps-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-dma-region.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-dma-region.c

Purpose: this file implements AFU userspace DMA mapping support for Intel DFL ports. It pins userspace pages, requires physical contiguity, maps them for DMA, tracks mappings in an RB tree, and unmaps them on ioctl or final device release.

Important APIs and functions: `afu_dma_region_init()` initializes the RB root. `afu_dma_map_region()` validates page alignment and overflow, allocates `struct dfl_afu_dma_region`, pins pages with `pin_user_pages_fast(FOLL_WRITE)`, verifies contiguous PFNs, maps the first page with `dma_map_page()`, inserts the region with `afu_dma_region_add()`, and returns the IOVA. `afu_dma_unmap_region()` finds by IOVA, rejects `in_use`, removes from the tree, unmaps DMA, unpins pages, and frees memory. `afu_dma_region_find()` searches for exact-start or containing regions.

Control flow: mapping does all expensive pin/map work before acquiring `fdata->lock`, then inserts the region under lock. Failure paths unwind in reverse order. Destroy walks the RB tree and releases all residual regions, intended for last close or device teardown.

State and persistence: `struct dfl_afu` owns the RB tree. Each region persists until explicit unmap or `afu_dma_region_destroy()`. The process locked-VM accounting is incremented when pages are pinned and decremented when unpinned.

Dependencies and integration: it depends on the AFU private data from `dfl-afu.h`, Linux DMA mapping API, user page pinning, current process `mm`, and the parent device returned by `dfl_fpga_fdata_to_parent()`. AFU ioctls in `dfl-afu-main.c` expose the map/unmap ABI.

Risks: it only supports physically contiguous user pages, which can fail for otherwise valid user memory. Locked-VM accounting is charged to `current->mm` on map and uncharged using `current->mm` on unmap/destroy; if cleanup occurs from a different task context, accounting assumptions can be delicate. `dma_region_check_iova()` uses addition that should be considered for overflow in future changes. Destroy erases a node and then calls `rb_next(node)`, which is a fragile ordering pattern because the node has already been erased.

Test signals: test unaligned addresses/lengths, zero length, overflow, non-contiguous pages, pin failures, DMA mapping errors, duplicate/overlapping IOVA insertion, unmap while `in_use`, last-close cleanup, and memlock-limit enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-dma-region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-error.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-error.c

Purpose: this file implements AFU port error reporting and interrupt ioctls for the DFL port error subfeature.

Important APIs and functions: `__afu_port_err_mask()` writes the port error mask register. `afu_port_err_clear()` performs the required clear sequence: reject AP6 power state, disable the port, mask errors, verify the user-supplied error value matches current errors, clear `PORT_ERROR` and `PORT_FIRST_ERROR`, unmask errors, and re-enable the port. Sysfs attributes under `errors/` expose `errors`, `first_error`, and `first_malformed_req`. `port_err_ioctl()` handles error IRQ number and trigger setup ioctls.

Control flow: feature init unmasks port errors, and uninit masks them. The `errors` sysfs store is the destructive clear operation and must receive the exact current error value. Visibility is conditional on the `PORT_FEATURE_ID_ERROR` feature being enumerated.

State and persistence: error state is hardware register state. The driver masks errors on feature teardown to avoid stale interrupt delivery. Clear operations temporarily alter port reset state and error masks under `fdata->lock`.

Dependencies and integration: it depends on AFU reset helpers from `dfl-afu-main.c`, DFL feature lookup, DFL IRQ helper ioctls, and the port header power-state register. It is included in the AFU compound object and referenced by `dfl-afu.h`.

Risks: clearing errors resets the port, so userspace can disrupt AFU work if it clears during active operations. The exact-match clear ABI can race with newly arriving errors and return `-EINVAL`. If re-enable fails after masking/clearing, the return prioritizes enable failure and the port may remain disabled. AP6 prevents clearing, leaving errors until power state changes.

Test signals: verify sysfs visibility only when the error feature exists, exact-match clear success and mismatch failure, AP6 rejection, disable/enable timeout handling, IRQ ioctl dispatch, and masking behavior on init/uninit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-main.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-main.c

Purpose: this is the main Intel DFL Accelerated Function Unit port driver. It provides the DFL port char-device ABI, port reset/enable control, sysfs attributes, MMIO region setup, DMA map/unmap ioctls, mmap support, and subfeature ioctl dispatch.

Important APIs and functions: `__afu_port_enable()` and `__afu_port_disable()` manage the port soft-reset bit with a nested `disable_count` and poll `PORT_CTRL_SFTRST_ACK`. `port_reset()` disables then enables the port. Header sysfs attributes expose port ID, latency tolerance reporting, AP1/AP2 events, power state, and revision-zero user clock command/status registers. AFU sysfs exposes `afu_id`. File operations implement exclusive/shared open tracking, release cleanup, ioctls for API version, region info, DMA map/unmap, port reset, AFU/error/user interrupt subfeatures, and `mmap()`.

Control flow: probe allocates `struct dfl_afu`, initializes MMIO/DMA region containers, initializes all enumerated port features, and registers file operations. The header feature resets the port during init. AFU and STP features add mmap-capable MMIO regions based on platform resources. Open increments DFL use count and can honor `O_EXCL`; release decrements it and, on last close, clears IRQ triggers, resets the port, and destroys DMA regions.

State and persistence: AFU private state stores MMIO region list, current file offset allocation, DMA RB tree, region count, and user-message count. `disable_count` lives in shared `dfl_feature_dev_data`. MMIO region metadata persists for device lifetime; DMA mappings persist per device until unmapped or last close. Hardware reset and status registers are mutated through sysfs/ioctl/release paths.

Dependencies and integration: it relies on DFL feature-device infrastructure, AFU helper files, DFL IRQ helpers, Linux char-device/mmap APIs, and parent resource layout. It registers `dfl_fpga_port_ops` so FME bridges can enable/disable a port during PR.

Risks: any final close resets the port and destroys all DMA regions, so multi-process users must coordinate carefully. `mmap()` allows noncached physical mappings for regions marked by feature init; incorrect resource indexes can expose wrong MMIO. User clock sysfs is hidden for feature revisions greater than zero, so ABI depends on hardware revision. DMA map/unmap is delegated to a physically contiguous implementation.

Test signals: test shared versus exclusive opens, reset ioctl argument validation, sysfs attribute visibility by feature/revision, AFU/STP region info and mmap permissions, DMA map/unmap ioctl copy failure unwinds, IRQ trigger cleanup on last release, and FME bridge enable/disable calls through registered port ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-region.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-region.c

Purpose: this file manages AFU MMIO region metadata used by the DFL AFU char-device ioctls and mmap path.

Important APIs and functions: `afu_mmio_region_init()` initializes the region list. `afu_mmio_region_add()` allocates a `struct dfl_afu_mmio_region`, checks for duplicate index, assigns a page-aligned file offset from `region_cur_offset`, appends the region, and increments `num_regions`. `afu_mmio_region_get_by_index()` returns metadata for `DFL_FPGA_PORT_GET_REGION_INFO`. `afu_mmio_region_get_by_offset()` finds the region containing a requested mmap file offset and size. `afu_mmio_region_destroy()` frees all devm-allocated region nodes.

Control flow: feature init in `dfl-afu-main.c` calls add for AFU and STP resources. Userspace first queries region count/info, then uses returned offsets for mmap. All list mutations and lookups hold `fdata->lock`.

State and persistence: `struct dfl_afu` owns a linked list of regions, current synthetic file offset, and region count. Regions persist for the AFU device lifetime and are not affected by individual file closes.

Dependencies and integration: it depends on `dfl-afu.h`, DFL feature private data, platform resource sizes, and AFU mmap/ioctl callers. Region flags determine read/write/mmap permissions in `afu_mmap()`.

Risks: `region->size` stores the original resource size while offset advancement uses `PAGE_ALIGN(region_size)`. Containment checks use the unaligned size, so mapping the padding area is rejected, which is intentional but must match userspace expectations. Duplicate index failure frees the devm allocation manually; future changes must avoid double-free patterns. Offset addition should be guarded if very large region sizes are introduced.

Test signals: add duplicate regions, query invalid indexes, mmap exact and out-of-range offsets, verify read/write permission flags, and check that reported offsets remain stable across opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu.h -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu.h

Purpose: this header defines shared private data structures and helper prototypes for the DFL AFU compound driver.

Important types and APIs: `struct dfl_afu_mmio_region` describes a userspace-visible MMIO window with index, flags, size, synthetic file offset, physical address, and list node. `struct dfl_afu_dma_region` describes a pinned DMA mapping with user VA, length, IOVA, page array, RB node, and `in_use` flag. `struct dfl_afu` is the per-port private object containing MMIO offset/count state, region list, DMA RB root, and user-message count. Prototypes cover port enable/disable, MMIO region management, DMA region management, and exported port error feature ops/groups.

Control flow and integration: `dfl-afu-main.c` owns `struct dfl_afu` allocation and lifecycle, while `dfl-afu-region.c`, `dfl-afu-dma-region.c`, and `dfl-afu-error.c` operate through these shared definitions. The explicit comment requires callers to hold `fdata->lock` for low-level port enable/disable helpers.

State and persistence: this header defines but does not instantiate state. The structures clarify which AFU state persists for device lifetime (MMIO regions), per mapping (DMA regions), and per hardware port (`dfl_afu` private pointer).

Dependencies and risks: it depends on `dfl.h` and Linux MM types. Because helpers share mutable `struct dfl_afu`, lock discipline is an important contract not enforced by the compiler. The `in_use` flag is present for consumers outside the DMA file but must be managed consistently by future AFU operations.

Test signals: compile all AFU objects together, validate lockdep coverage for helper callers, and ensure structure fields stay ABI-internal and are not assumed by userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-br.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-br.c

Purpose: this platform driver adapts a DFL AFU port into an FPGA bridge used by FME partial reconfiguration regions.

Important APIs and functions: `struct fme_br_priv` stores platform data, cached port ops, and cached port feature data. `fme_bridge_enable_set()` lazily finds the target port by ID in the DFL container, obtains `dfl_fpga_port_ops`, and calls its `enable_set()` callback. Probe registers an FPGA bridge named `DFL FPGA FME Bridge`.

Control flow: the PR management feature creates one bridge platform device per implemented port. When the FPGA region disables or enables bridges, this driver resolves the DFL port and delegates to the AFU driver's reset-based enable implementation. Remove unregisters the bridge and releases the port ops reference if acquired.

State and persistence: cached `port_fdata` and `port_ops` persist after first bridge use. The actual bridge state is the AFU port reset state managed by the port driver.

Dependencies and integration: it depends on DFL container port lookup, AFU `dfl_fpga_port_ops`, FPGA bridge framework, and platform data from `dfl-fme-pr.c`.

Risks: lazy lookup means probe can succeed even if the target port is not yet available; first enable may return `-ENODEV` or `-ENOENT`. Cached `port_fdata` lifetime depends on DFL container lifetime. `enable_show` is not implemented, so users cannot read state through bridge ops.

Test signals: test bridge enable before/after AFU port driver registration, missing port ID, missing `enable_set`, PR flows disabling and re-enabling ports, and remove after lazy ops acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-br.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-error.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-error.c

Purpose: this file implements global error reporting, masking, clearing, injection, and IRQ ioctls for the Intel DFL FPGA Management Engine.

Important APIs and functions: sysfs attributes under `errors/` expose PCIe0/PCIe1 errors, nonfatal and catastrophic RAS errors, error injection bits, FME errors, first error, and next error. Store handlers for PCIe and FME errors mask the relevant group, require the written value to match current hardware error bits, clear by writeback, then unmask. `fme_err_mask()` masks or unmasks all error groups and applies a revision-zero workaround that keeps `MBP_ERROR` masked. `fme_global_error_ioctl()` handles FME error IRQ num/set ioctls.

Control flow: feature init unmasks global errors, feature uninit masks them. Sysfs visibility depends on `FME_FEATURE_ID_GLOBAL_ERR` being enumerated. Injection writes update only `INJECT_ERROR_MASK` bits in `RAS_ERROR_INJECT`.

State and persistence: all error state lives in FME hardware registers. The only software state is lock-protected access through `fdata->lock`; masking state is programmed into hardware and persists until changed or device reset.

Dependencies and integration: it depends on DFL feature lookup, DFL IRQ helpers, `dfl-fme.h` declarations, and FME feature revision checks. The attribute group is registered by `dfl-fme-main.c`.

Risks: exact-match clearing can race with new hardware errors. Nonfatal and catastrophic RAS attributes are read-only here, so clearing may require other mechanisms or reset. Error injection is writable through sysfs and must be permission-controlled by sysfs mode and device ownership. The revision-zero MBP workaround changes mask semantics and should be preserved in future refactors.

Test signals: verify sysfs group visibility, clear success and mismatch failure for PCIe/FME groups, MBP mask behavior for revision zero versus later revisions, injection mask validation, IRQ ioctl dispatch, and masking on init/uninit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-main.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-main.c

Purpose: this is the main Intel DFL FPGA Management Engine driver. It exposes FME header sysfs, char-device ioctls, thermal and power hwmon devices, global error sysfs, PR/perf feature integration, and DFL port assign/release operations.

Important APIs and functions: header sysfs exposes `ports_num`, `bitstream_id`, `bitstream_metadata`, `cache_size`, `fabric_version`, and `socket_id`. Header ioctls dispatch `DFL_FPGA_FME_PORT_RELEASE` and `DFL_FPGA_FME_PORT_ASSIGN` to DFL container helpers. Thermal init registers `dfl_fme_thermal` hwmon with temperature input, thresholds, alarms, and `temp1_max_policy` when throttling is supported. Power init registers `dfl_fme_power` hwmon with input, writable max/crit thresholds, alarms, and read-only Xeon/FPGA limits plus latency tolerance. The file operation layer supports API version, extension check, and subfeature ioctl dispatch.

Control flow: probe allocates `struct dfl_fme`, initializes enumerated subfeatures from `fme_feature_drvs`, then registers char-device ops. Subfeatures include header, PR management, global errors, thermal, power, and perf. Open/release use DFL use counting and clear IRQ triggers on final close. Remove unregisters ops, uninitializes features, and clears private data.

State and persistence: FME private data tracks PR-created manager/region/bridge lists through `struct dfl_fme`. HWMON readings and thresholds are direct hardware register accesses; power threshold writes persist in FME registers. Use count and IRQ triggers are maintained by DFL common data.

Dependencies and integration: it depends on DFL core infrastructure, hwmon, perf feature declarations, FPGA PR helpers, global error helpers, and Linux units conversion. It is the parent feature driver that wires together FME-specific subfeature files.

Risks: `FPGA_DFL_FME` depends on both hwmon and perf even if deployments do not use monitoring. Power threshold writes clamp from microwatts to watts with `PWR_THRESHOLD_MAX`, which can surprise users expecting exact values. Thermal visibility depends on hardware throttle capability. Subfeature ioctl dispatch returns `-EINVAL` if no subfeature handles a command, while subfeatures use `-ENODEV` as "not mine".

Test signals: test header sysfs against known capability registers, port assign/release ioctls, hwmon registration and unit conversions, writable power thresholds, final-close IRQ cleanup, subfeature init failure unwinds, and module removal after PR/perf/error initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-mgr.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-mgr.c

Purpose: this FPGA manager driver programs DFL FME partial reconfiguration hardware. It is the manager used by FME FPGA regions created per AFU port.

Important APIs and functions: `struct fme_mgr_priv` stores PR MMIO base and last PR error bits. `fme_mgr_write_init()` requires `FPGA_MGR_PARTIAL_RECONFIG`, resets the PR engine, waits for reset ack and idle status, clears previous errors, and writes the target region ID. `fme_mgr_write()` asserts `PR_START`, polls credit, and writes 32-bit bitstream words into `FME_PR_DATA`. `fme_mgr_write_complete()` asserts `PR_COMPLETE`, waits for hardware to clear `PR_START`, checks errors, and returns success or `-EIO`. `fme_mgr_status()` maps PR error bits to FPGA manager status flags.

Control flow: probe receives MMIO through platform data from PR management or maps resource 0, reads compatibility ID registers into `fpga_compat_id`, and registers a full FPGA manager. Programming is credit-driven and uses a long microsecond timeout for reset, idle, credit, and completion.

State and persistence: software persists only the MMIO base and most recent PR error value. Hardware PR control/status/error registers carry operation state. The manager's compatibility ID is fixed at probe and shared with regions for bitstream compatibility checks.

Dependencies and integration: it depends on the FPGA manager framework, DFL FME PR platform data, non-atomic 64-bit IO helpers, and the region/bridge platform devices created by `dfl-fme-pr.c`.

Risks: bitstream size must be a multiple of four; smaller trailing fragments fail. Credit polling uses a simple delay counter rather than elapsed time. If `fme_mgr_pr_error_handle()` sees status clean, it does not read/clear error bits. The write path casts buffer to `u32 *`, so alignment matters. Region ID is taken from image info and must match the port.

Test signals: test missing partial flag, PR reset ack timeout, idle timeout, stale error clearing, invalid non-multiple-of-four image sizes, credit timeout, completion timeout, each PR error bit mapping, and compatibility ID propagation to regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-perf.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-perf.c

Purpose: this file registers a perf PMU for DFL FME global performance counters. It exposes basic clock, cache, fabric, VT-d, and VT-d SIP events depending on whether the hardware feature is global IPERF or DPERF.

Important APIs and functions: `struct fme_perf_priv` stores device, MMIO base, PMU, feature ID, fabric mode state, active CPU, and CPU hotplug node. Event config fields are `event`, `evtype`, and `portid`. Event init functions validate per-counter constraints: basic clock is root-only, cache and VT-d/SIP are IPERF-only, fabric allows root or one port and filters unavailable DPERF events. Read functions program the event selector and poll counter event tags before reading. PMU callbacks implement init, add, del, start, stop, read, and destroy.

Control flow: feature init allocates private state, binds to the current CPU, sets up a dynamic CPU hotplug state, registers an instance, initializes fabric mode from hardware, registers a PMU named `dfl_fme<id>`, and stores private data on the feature. On CPU offline, the PMU context migrates to another online CPU. Uinit unregisters PMU and hotplug state.

State and persistence: PMU state includes active CPU and fabric counter mode. Fabric counters can operate in either root or one-port mode; `fab_users`, `fab_port_id`, and `fab_lock` prevent conflicting simultaneous fabric events. Hardware counters are free-running or selected through control registers. Perf event counts use deltas from previous hardware readings.

Dependencies and integration: it depends on Linux perf PMU APIs, CPU hotplug, DFL feature lifecycle, and FME MMIO. `dfl-fme-main.c` includes this feature ops table in the FME driver.

Risks: PMU supports only system-wide counting on the selected CPU; per-task and sampling events are rejected. Fabric mode sharing can reject otherwise valid events when another fabric event uses a different port mode. `PERF_MAX_PORT_NUM` is one, so multi-port hardware would need updates. Counter read helpers return zero on event-tag timeout, which can hide hardware failures as low counts. CPU hotplug state is dynamically allocated per feature instance.

Test signals: verify PMU sysfs format/events/cpumask, IPERF versus DPERF event visibility, per-task and sampling rejection, wrong CPU rejection, fabric root/port conflict handling, CPU offline migration, counter tag timeout logging, and event count deltas across repeated reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-pr.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-pr.c

Purpose: this file implements DFL FME partial-reconfiguration orchestration. It creates child FPGA manager, bridge, and region devices for each implemented port and exposes the `DFL_FPGA_FME_PORT_PR` ioctl to program a port region from a userspace buffer.

Important APIs and functions: `fme_pr()` copies a `struct dfl_fpga_fme_port_pr`, validates args and port ID, aligns buffer length to 4 bytes, copies the bitstream with `vmalloc()`, creates `fpga_image_info`, finds the target `fpga_region`, sets partial-reconfig flags and region ID, calls `fpga_region_program_fpga()`, and releases bridge references afterward. `pr_mgmt_init()` creates one FME manager plus bridge/region platform devices for implemented ports based on `FME_HDR_CAP` and port offset registers. Destroy helpers unregister child devices and maintain FME lists.

Control flow: PR management feature init initializes region and bridge lists, creates the manager from the PR feature MMIO, iterates implemented ports, creates bridge devices tied to DFL port IDs, and creates matching FPGA region devices. The ioctl path later uses those lists to find the target region and invokes the generic FPGA region programming flow, which disables bridges, calls the FME manager, and re-enables bridges.

State and persistence: `struct dfl_fme` holds child manager, bridge list, and region list. Each `struct dfl_fme_region` maps a port ID to a region platform device. During an ioctl, the image buffer and info are transient; `region->info` is replaced and later the local buffer is freed after programming returns.

Dependencies and integration: it depends on FPGA manager/bridge/region frameworks, DFL FME header registers, FME child drivers (`dfl-fme-mgr`, `dfl-fme-br`, `dfl-fme-region`), and userspace DFL ioctl ABI.

Risks: the aligned `vmalloc(length)` buffer is not explicitly zeroed beyond `buffer_size`, so padded bytes may contain uninitialized data, although comments state hardware ignores padding. The code frees `buf` after `fpga_region_program_fpga()` while assigning it into `region->info`; this relies on programming being synchronous and no later consumer using the stale pointer. Holding `fdata->lock` across `fpga_region_program_fpga()` can serialize PR but may interact with bridge operations that call back into DFL port ops. Region platform data includes `region_id` in the header but creation does not set it.

Test signals: test invalid argsz/flags, out-of-range port IDs, missing region, copy-from-user failures, non-multiple-of-four buffer sizes, manager/bridge/region creation unwinds, implemented versus unimplemented port offsets, PR success path bridge release, and concurrent PR ioctl serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-pr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-pr.h -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-pr.h

Purpose: this header defines platform data and list node structures shared by FME partial-reconfiguration orchestration, manager, bridge, and region child drivers.

Important types and APIs: `struct dfl_fme_region` links a region platform device to a port ID. `struct dfl_fme_region_pdata` passes the manager and bridge platform devices to the region driver and reserves a `region_id` field. `struct dfl_fme_bridge` tracks bridge platform devices in the FME list. `struct dfl_fme_br_pdata` passes the DFL container and port ID to bridge devices. `struct dfl_fme_mgr_pdata` passes the PR MMIO address to the manager. String macros define platform driver names for manager, bridge, and region.

Control flow and integration: `dfl-fme-pr.c` creates platform devices using these payloads. `dfl-fme-mgr.c`, `dfl-fme-br.c`, and `dfl-fme-region.c` consume the payloads during probe. The names are also used as module aliases and Kconfig-selected driver identities.

State and persistence: the structures define runtime topology rather than hardware state. They persist for the lifetime of child platform devices and connect a single FME manager to multiple port-specific bridge/region pairs.

Dependencies and risks: it depends on platform-device declarations and DFL container types via included headers in consumers. The `region_id` field is documented but not set by current region creation, so consumers should not rely on it unless fixed. Lifetime is tied to platform device data copies and devm allocations in the creator.

Test signals: compile child drivers independently, verify platform data sizes and copies, check module aliases match macros, and validate region/bridge topology for each implemented port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-pr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-region.c -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-region.c

Purpose: this platform driver registers FPGA regions for DFL FME ports. Each region connects the FME FPGA manager with the port bridge used for PR isolation.

Important APIs and functions: `fme_region_get_bridges()` converts platform data bridge device into a bridge list entry with `fpga_bridge_get_to_list()`. `fme_region_probe()` gets the manager from platform data, fills `fpga_region_info` with manager, compatibility ID, bridge callback, and private platform data, then registers a full FPGA region. Remove unregisters the region and puts the manager reference.

Control flow: PR management creates one region platform device per implemented port. Region probe may defer until the manager is available. During programming, the FPGA region framework calls `get_bridges`, disables bridge(s), invokes the manager, and then handles bridge release/re-enable according to region flow.

State and persistence: `struct fpga_region` registered by the framework persists for the platform device lifetime. It holds a reference to the manager and uses manager compatibility ID for bitstream compatibility checks.

Dependencies and integration: it depends on FPGA manager and region frameworks, bridge framework indirectly, and platform data from `dfl-fme-pr.c`. It is one of the child drivers selected by `FPGA_DFL_FME_REGION`.

Risks: if the manager is absent, probe returns `-EPROBE_DEFER`; missing bridge devices cause programming-time bridge acquisition failures. Region private data points to platform data copied into the platform device, so creator and consumer layouts must remain synchronized. Only one bridge device is added per region.

Test signals: test probe deferral until manager driver loads, successful region registration with compatibility ID, bridge acquisition failure, remove ordering relative to manager, and PR programming through the region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme.h -->
## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme.h

Purpose: this header defines the main private state for the DFL FME compound driver and declares shared FME subfeature operation tables.

Important types and APIs: `struct dfl_fme` stores the FME manager platform device and linked lists of FME FPGA regions and bridges. External declarations expose PR management ops and IDs, global error ops/IDs/sysfs group, and performance ops/IDs to `dfl-fme-main.c`.

Control flow and integration: `dfl-fme-main.c` allocates `struct dfl_fme` and stores it in DFL feature private data. `dfl-fme-pr.c` fills `mgr`, `region_list`, and `bridge_list` during PR feature init. Error and perf feature files provide ops tables declared here so the main feature driver can register all FME subfeatures as one module.

State and persistence: this header defines state that persists for the FME device lifetime. The manager and child lists are initialized and destroyed with the PR management feature, while the containing private object is allocated and cleared by FME probe/remove.

Dependencies and risks: the header relies on consumers including platform and list definitions through surrounding includes. Cross-file external declarations mean mismatched object composition in the Makefile would cause link failures. Child-list access requires `fdata->lock` discipline established in PR management.

Test signals: compile FME compound objects, probe with and without PR/global-error/perf features, validate child list initialization before use, and remove with populated and empty child lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme.h -->
