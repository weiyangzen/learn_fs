# subset-b-000807 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas.c

Purpose: pSeries/PowerVM VAS backend for user-space NX GZIP copy/paste windows. It discovers hypervisor VAS capabilities, registers the VAS coprocessor API, opens/closes per-process windows, handles NX fault interrupts, and reconfigures windows during CPU DLPAR and live partition migration.

Important APIs/types/functions: exported `h_query_vas_capabilities()`, `vas_register_api_pseries()`, `vas_unregister_api_pseries()`, `vas_reconfig_capabilties()`, `pseries_vas_dlpar_cpu()`, and `vas_migration_handler()`. Core helpers are `h_allocate_vas_window()`, `h_deallocate_vas_window()`, `h_modify_vas_window()`, `h_get_nx_fault()`, `allocate_setup_window()`, `vas_allocate_window()`, `vas_deallocate_window()`, `reconfig_open_windows()`, `reconfig_close_windows()`, and `pseries_vas_init()`.

Control flow: init requires radix page tables, queries overall `H_QUERY_VAS_CAPABILITIES`, initializes sysfs capability state, then queries QoS/default GZIP feature capabilities and registers an OF reconfig notifier on LPAR firmware. Opening a window checks the requested credit class, reserves one credit atomically, optionally asks `H_HOME_NODE_ASSOCIATIVITY` for local VAS placement, allocates the HV window, creates a fault IRQ mapping, requests a threaded IRQ, modifies the window with the LPAR PID, records task/mm references, and links the window into the feature list. Fault IRQs increment `pending_faults`; the thread drains pending faults with `H_GET_NX_FAULT`, dumps the CRB, and updates the CSB/signals via common VAS helpers. Closing removes mappings and task references after hypervisor deallocation unless the window was already closed for migration or lost credits.

State and persistence: state is in global capability arrays, credit atomics, per-feature open-window lists, `vas_pseries_mutex`, `migration_in_progress`, per-window IRQ/name/status fields, and task/mm references used for mmap paste remapping. Hypervisor window IDs, paste addresses, and IRQs are transient but must stay synchronized with Linux list/status accounting. Sysfs capability files expose persistent runtime observations until reboot.

Dependencies and integration points: depends on PAPR hypercalls, `asm/vas.h` user-window infrastructure, pSeries machine initcalls, OF reconfiguration notifiers, LPAR/shared processor state, VPHN associativity, IRQ mapping, mm VMA zap/remap helpers, and NX CRB/CSB handling. It integrates with migration code through `vas_migration_handler()` and with lparcfg/DLPAR through `pseries_vas_dlpar_cpu()`.

Risks: credit accounting and window status transitions are race-sensitive across open, close, DLPAR, and migration. IRQs must remain installed until hypervisor close drains outstanding NX faults. Error paths decrement credits and `nr_open_wins_progress`; missed decrements could permanently block windows. Migration cannot always be aborted, so suspend errors are intentionally ignored, leaving resume recovery as the main safety path.

Test signals: useful signals are VAS sysfs capability values, successful user-space NX GZIP open/mmap/paste/close, injected NX fault CSB updates, DLPAR CPU add/remove causing window close/reopen and paste remap behavior, LPM suspend/resume closing and restoring windows, and absence of leaked IRQ mappings or stuck credits after failed HCALLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas.h

Purpose: private pSeries VAS definitions shared by the pSeries VAS implementation and related sysfs/migration code.

Important APIs/types/functions: defines `VAS_MOD_WIN_*` hypervisor modify flags, window status values, user-mode capability bits, GZIP capability descriptors, `enum vas_migrate_action`, `enum vas_cop_feat_type`, hypervisor wire structs `hv_vas_cop_feat_caps` and `hv_vas_win_lpar`, internal `vas_cop_feat_caps`, `vas_caps`, `pseries_vas_window`, and prototypes for sysfs/reconfiguration/migration helpers.

Control flow: this header does not execute logic, but it shapes how `vas.c` interprets capability buffers, tracks credit counters, and records per-window state used by open, close, DLPAR, and LPM flows. Inline stubs return success for migration/DLPAR hooks when `CONFIG_PPC_VAS` is disabled.

State and persistence: the main state model is feature-scoped capability/credit accounting plus a list of open windows. `pseries_vas_window` persists the hypervisor-provided window ID, paste address, fault/completion IRQs, PID, domain, list node, IRQ name, virtual IRQ, and pending fault count for the lifetime of an open file/window.

Dependencies and integration points: includes common `asm/vas.h`, mutex and stringify support, and is consumed by pSeries VAS code and platform migration/DLPAR code. Packed/aligned hypervisor structures are part of the PAPR ABI and must match HCALL buffer layout.

Risks: bit definitions and struct layout are ABI-sensitive. The constants for `VAS_WIN_NO_CRED_CLOSE` and `VAS_WIN_MIGRATE_CLOSE` are not defined here but are expected from common VAS headers; status bit interactions must remain compatible with `vas.c`. Any change to packed structs can break hypervisor communication.

Test signals: compile coverage under `CONFIG_PPC_VAS` and without it, capability query decoding, sysfs output matching hypervisor values, and DLPAR/LPM paths correctly observing the status/credit fields validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vio.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vio.c

Purpose: implements the pSeries virtual I/O bus. It registers VIO and platform-facilities devices from the device tree, provides driver matching/probe/remove/shutdown, builds VIO IOMMU tables, supports PFO `H_COP` operations, manages VIO interrupt signaling, and optionally enforces cooperative memory overcommitment (CMO) DMA entitlement accounting.

Important APIs/types/functions: exported `__vio_register_driver()`, `vio_unregister_driver()`, `vio_register_device_node()`, `vio_unregister_device()`, `vio_get_attribute()`, `vio_find_node()`, `vio_enable_interrupts()`, `vio_disable_interrupts()`, `vio_h_cop_sync()`, `vio_cmo_entitlement_update()`, and `vio_cmo_set_dev_desired()`. Key internal paths are `vio_cmo_alloc/dealloc/balance/bus_probe/bus_remove/bus_init`, VIO DMA ops, `vio_build_iommu_table()`, `vio_bus_probe/remove/shutdown/match`, `vio_bus_init()`, and `vio_device_init()`.

Control flow: postcore init registers the VIO bus and fake parent device, initializes CMO if firmware advertises it, then device init scans `/vdevice` and `/ibm,platform-facilities`. `vio_register_device_node()` classifies nodes as VDEVICE or PFO, derives names/type/resource IDs/IRQs, installs DMA ops and IOMMU tables when `ibm,my-dma-window` exists, and registers the device. Driver probe matches by VIO type and OF compatible, runs CMO entitlement setup first when enabled, then calls the driver. DMA mappings under CMO reserve entitlement before calling IOMMU mapping and release entitlement on unmap. PFO synchronous operations loop on busy/resource hypervisor returns until success, error, or timeout.

State and persistence: persistent runtime state includes the bus type, fake parent device, registered `vio_dev` objects, OF node references, IOMMU table refs, CMO global pools (`entitled`, `reserve`, `excess`, `spare`, `min`, `desired`, `curr`, `high`), per-device CMO desired/entitled/allocated counters, and delayed balancing work. Sysfs exposes device identity and CMO counters when `CONFIG_PPC_SMLPAR` is enabled.

Dependencies and integration points: depends on pSeries machine initcall ordering, OF nodes/properties, hypervisor calls `h_get_mpp`, `h_vio_signal`, and `H_COP`, pSeries/LAPR IOMMU table ops, `asm/vio.h` driver contracts, DMA mapping infrastructure, kexec state, and sysfs bus/device attribute groups.

Risks: CMO accounting has many invariants; underflow/overcommit bugs can panic or deny DMA. Probe failure must unwind CMO list entries. Kexec shutdown can call remove when drivers lack shutdown hooks. `vio_find_node()` relies on the exact kobject naming rules used during registration. `vio_h_cop_sync()` timeout handling uses jiffies and may exceed the nominal timeout while an operation is in progress.

Test signals: VIO devices appearing under `/sys/bus/vio`, module autoload modalias values, successful driver probe/remove cycles, VIO DMA map/unmap under CMO with correct sysfs counters, entitlement updates via `vio_cmo_entitlement_update()`, successful PFO operations and timeout/error mapping, and interrupt enable/disable HCALL results are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vphn.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vphn.c

Purpose: converts virtual processor home node associativity data returned by the pSeries hypervisor into the standard `ibm,associativity` property cell format.

Important APIs/types/functions: `vphn_unpack_associativity()` decodes packed 16-bit/32-bit fields, and kernel-only `hcall_vphn()` invokes `H_HOME_NODE_ASSOCIATIVITY` and fills a `__be32` associativity buffer. Constants `VPHN_FIELD_UNUSED`, `VPHN_FIELD_MSB`, and `VPHN_FIELD_MASK` describe the packed field encoding.

Control flow: the unpacker first converts `plpar_hcall9()` long return registers to big-endian 64-bit slots, then walks the 16-bit field stream. A high-bit field encodes a 15-bit domain, a low-bit field starts a 31-bit domain completed by the next 16-bit field, and `0xffff` terminates the list. The output cell zero stores the number of associativity domains.

State and persistence: the file has no global mutable state. It transforms a bounded hypervisor return buffer into a caller-provided output buffer.

Dependencies and integration points: uses `asm/vphn.h` constants and `plpar_hcall9()` in kernel builds. The file is also included by a selftest and is intentionally usable from userspace for unpacking validation.

Risks: malformed field streams ending while `is_32bit` is true are not explicitly reported; the current contract trusts the hypervisor buffer shape. Endianness conversion is central because HCALL returns longs while the OF-style output expects big-endian cells.

Test signals: selftests for 15-bit values, 31-bit combined values, terminators, maximum buffer length, and HCALL success paths should validate both unpacking and the `hcall_vphn()` wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vphn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/purgatory/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/purgatory/Makefile

Purpose: builds the PowerPC kexec purgatory object that is embedded into the kernel and used as the transition trampoline for kexec/kdump.

Important APIs/types/functions: targets `trampoline_$(BITS).o`, `purgatory.ro`, and `kexec-purgatory.o`; `LDFLAGS_purgatory.ro` sets entry point `purgatory_start`, relocatable link, and `--no-undefined`; `KBUILD_CFLAGS` filters out PGO flags.

Control flow: the trampoline object is linked into `purgatory.ro`; `kexec-purgatory.o` depends on that binary and embeds it through `kexec-purgatory.S`; `obj-y` includes the final wrapper object in the kernel build.

State and persistence: no runtime state. The artifact is a read-only relocatable blob consumed by kexec setup code.

Dependencies and integration points: integrates with Kbuild target tracking and the PowerPC purgatory assembly sources. The PGO filter avoids LLVM producing overlapping text sections that kexec cannot handle.

Risks: entry point or link flag changes can make the purgatory blob unusable by kexec. Toolchain flags that alter section layout are sensitive because the blob is copied and patched by kexec code.

Test signals: successful `kexec_file_load`/kexec boot on ppc64, objdump/readelf showing `purgatory_start` entry and no undefineds, and builds with PGO enabled confirm this Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/purgatory/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/purgatory/kexec-purgatory.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/purgatory/kexec-purgatory.S

Purpose: embeds the linked purgatory trampoline binary into the kernel as read-only data and exports its address and size.

Important APIs/types/functions: global symbols `kexec_purgatory` and `kexec_purgatory_size`; `.incbin "arch/powerpc/purgatory/purgatory.ro"` includes the built blob.

Control flow: there is no executable logic in this wrapper. It lays out the blob at 8-byte alignment, records the end label, and emits a quad containing blob length.

State and persistence: the embedded blob persists in kernel rodata and is later copied/relocated by kexec setup.

Dependencies and integration points: depends on the Makefile producing `purgatory.ro`. Kexec code consumes the exported symbols to locate and size the blob.

Risks: incorrect alignment or size computation would corrupt kexec payload preparation. The include path is build-layout-sensitive.

Test signals: link success, exported symbol presence, nonzero size, and successful kexec image loading validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/purgatory/kexec-purgatory.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/purgatory/trampoline_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/purgatory/trampoline_64.S

Purpose: 64-bit PowerPC kexec purgatory trampoline. It preserves a backup memory region, patches boot metadata, switches endian mode if needed, and branches into the next kernel.

Important APIs/types/functions: global `purgatory_start`, `run_at_load`, `kernel`, `dt_offset`, `backup_start`, `opal_base`, `opal_entry`, `purgatory_sha256_digest`, and `purgatory_sha_regions`. The first 0x100 bytes are ABI-controlled and replaced by setup code.

Control flow: execution branches from `purgatory_start` to `master`, saves CPU ID and physical address registers, computes the current PC, optionally copies `BACKUP_SRC_SIZE` bytes from `BACKUP_SRC_START` to `backup_start`, delays for secondary threads, updates the device-tree boot CPU field for v2+ flattened trees, loads OPAL and kernel addresses, patches the target kernel's `run_at_load` flag, restores the device-tree pointer in r3, clears r5, then either branches directly for big-endian or uses SRR0/SRR1 and `rfid` to clear MSR_LE before entering the kernel.

State and persistence: mutable fields are patched by kexec before execution: target kernel address, device tree offset, backup destination, OPAL base/entry, run-at-load flag, digest, and SHA region list. No normal kernel state survives except what the trampoline deliberately copies and passes in registers.

Dependencies and integration points: depends on PowerPC kexec ABI offsets, crashdump constants, flattened device tree layout, OPAL handoff conventions, and the generic kexec purgatory integrity machinery.

Risks: fixed `.org` ABI offsets are brittle. Copy loop assumes 8-byte granularity. Endian transition must clear only MSR_LE while preserving valid MSR bits. Device-tree version offsets must match the flattened tree ABI.

Test signals: ppc64 kexec and crash-kexec boots, little-endian-to-big-endian transition coverage, backup region verification, correct boot CPU in the FDT, and purgatory SHA validation are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/purgatory/trampoline_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/6xx-suspend.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/6xx-suspend.S

Purpose: low-level standby entry/return routine for Book3S 32-bit 6xx-style processors whose HID0 sleep state resumes without reset.

Important APIs/types/functions: global `mpc6xx_enter_standby` and local `ret_from_standby`. It manipulates `SPRN_HID0`, MSR `EE` and `POW`, thread-info local flags, and the link register.

Control flow: saves LR, clears HID0 doze/nap, sets HID0 sleep, points LR at `ret_from_standby`, marks `_TLF_SLEEPING`, enables interrupts and power management in MSR, syncs, writes MSR, and spins. On interrupt wake, execution resumes at `ret_from_standby`, clears HID0 sleep, restores LR, and returns.

State and persistence: persists sleep intent in HID0 and thread local flags while the CPU sleeps. No memory allocation or device state is touched.

Dependencies and integration points: built only for suspend on `PPC_BOOK3S_32`. It depends on assembly offsets for `TI_LOCAL_FLAGS`, HID0 bit definitions, and platform suspend code calling the symbol.

Risks: incorrect MSR/HID0 ordering can leave the CPU awake, stuck asleep, or with interrupts misconfigured. The infinite loop is expected to be escaped only by the processor wake path.

Test signals: standby/resume on 6xx-compatible systems, HID0 sleep bit clearing after wake, and no corruption of LR/thread flags validate the path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/6xx-suspend.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/Kconfig

Purpose: declares selected PowerPC sysdev configuration symbols and includes interrupt-controller Kconfig fragments.

Important APIs/types/functions: symbols `PPC4xx_PCI_EXPRESS`, `PPC4xx_HSTA_MSI`, `PPC_MSI_BITMAP`, `GE_FPGA`, and `FSL_CORENET_RCPM`; includes `xics/Kconfig` and `xive/Kconfig`.

Control flow: Kconfig dependency resolution enables hidden support symbols based on PCI/MSI/platform selections. `PPC_MSI_BITMAP` defaults to yes for MPIC, FSL PCI, or PowerNV with PCI MSI.

State and persistence: build-time configuration only. Resulting `.config` controls which sysdev objects are compiled.

Dependencies and integration points: feeds the sysdev Makefile and platform code. `FSL_CORENET_RCPM` enables Run Control/Power Management support, while XICS/XIVE includes expose interrupt controller options.

Risks: hidden bools without prompts rely on other platform Kconfig selecting them correctly. Missing defaults can silently omit support such as MSI bitmap allocation.

Test signals: expected objects appearing in `arch/powerpc/sysdev/` build output for representative configs and `allyesconfig`/platform defconfig coverage are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/Makefile

Purpose: selects and groups PowerPC sysdev object files according to Kconfig symbols.

Important APIs/types/functions: object assignments for MPIC/MSI/MSGR, ePAPR HV PIC, DART, Freescale SoC/PCI/PMC/RCPM/LBC/GTM/RIO, CPM/CPM2/GPIO, DCR, XICS/XIVE subdirectories, and suspend-only `6xx-suspend.o`.

Control flow: Kbuild expands `obj-$(CONFIG_*)` and helper variables such as `mpic-msi-obj-*` and `fsl-msi-obj-*` to compile the correct platform support set. The file includes MPIC twice, once for base/MSI and once with message registers, relying on Kbuild duplicate handling.

State and persistence: build graph only. It determines which runtime drivers and low-level assembly helpers exist in a kernel image.

Dependencies and integration points: consumes symbols from sysdev Kconfig and broader arch/platform Kconfig. Subdirectory entries hand off to XICS/XIVE/GE FPGA Makefiles.

Risks: duplicate or missing object selections can cause link omissions or redundant object references. Conditional suspend object selection must match symbols exported by platform suspend code.

Test signals: build coverage across pSeries, PowerNV, FSL BookE, 4xx, CPM, and suspend configs; link success; and expected module/builtin object presence validate this Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2.c

Purpose: common CPM2 global management support for mapping CPM registers, issuing CPM commands, configuring baud-rate generators, setting CPM mux clocks, and configuring CPM2 pins.

Important APIs/types/functions: globals `cpmp` and exported `cpm2_immr`; functions `cpm2_reset()`, exported `cpm_command()`, exported `__cpm2_setbrg()`, `cpm2_clk_setup()`, `cpm2_smc_clk_setup()`, and `cpm2_set_pin()`.

Control flow: `cpm2_reset()` maps IMMR/CPM register space, initializes the CPM pointer, and optionally issues CPM reset. `cpm_command()` serializes command register writes with a spinlock, writes command/opcode/flag, and polls until CPM clears the flag or times out. Clock setup functions map target/clock pairs to mux bits and update CPM mux registers. Pin setup toggles direction, peripheral/GPIO, secondary option, and open-drain bits.

State and persistence: persistent state is the ioremapped CPM register block and global `cpmp` pointer. CPM command and mux/pin register writes persist in hardware until reset or reconfiguration.

Dependencies and integration points: depends on SoC IMMR base discovery, CPM2 register definitions, `asm/cpm2.h`, endian MMIO helpers, and consumers such as serial, Ethernet, and GPIO drivers that need BRG, clock, or pin setup.

Risks: CPM command polling can fail if hardware is wedged. Clock map tables are static and invalid target/clock pairs return `-EINVAL` after still writing zero bits if not checked carefully by callers. Pin indexing assumes valid port/pin arguments.

Test signals: CPM reset success, BRG output frequency, serial/network channels receiving expected clocks, command timeout logs absent, and GPIO/pin mux behavior on CPM2 boards validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2_pic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2_pic.c

Purpose: interrupt controller driver for the CPM2 internal SIU interrupt controller.

Important APIs/types/functions: exported-by-header `cpm2_get_irq()` and `cpm2_pic_init()`, IRQ chip callbacks `cpm2_mask_irq()`, `cpm2_unmask_irq()`, `cpm2_ack()`, `cpm2_end_irq()`, `cpm2_set_irq_type()`, mapping tables `irq_to_siureg`/`irq_to_siubit`, and irqdomain ops `cpm2_pic_host_map()`.

Control flow: init masks all interrupts, acknowledges pending bits, reads the vector register, resets priority registers, and creates a linear irqdomain for 64 sources. Mapping installs the CPM2 chip with a level handler by default. `cpm2_get_irq()` reads `ic_sivec`, extracts the vector, and maps it to a Linux IRQ. Type setting validates allowed senses for external and Port C IRQs, selects edge/level handlers, and updates SIEXR edge-detect bits.

State and persistence: global state includes the MMIO pointer, irqdomain, and cached mask words mirrored to SIMRH/SIMRL. Hardware mask, pending, priority, and sense registers persist until changed.

Dependencies and integration points: depends on `cpm2_immr` having been mapped by CPM2 setup, Linux irqdomain/irqchip APIs, device tree interrupt translation, and platform interrupt dispatch calling `cpm2_get_irq()`.

Risks: IRQ numbers do not map linearly to mask bits, so table mistakes break specific sources. External/Port C sense programming is constrained; unsupported high/rising levels are rejected. `cpm2_end_irq()` uses a memory barrier to avoid known spurious IRQ behavior on 82xx systems.

Test signals: boot IRQ discovery, timer/serial/network CPM interrupts, edge-vs-level trigger tests for external and Port C lines, no interrupt storms after EOI, and correct `/proc/interrupts` accounting validate the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2_pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2_pic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2_pic.h

Purpose: small public header for CPM2 interrupt-controller setup and dispatch.

Important APIs/types/functions: declarations for `cpm2_get_irq()` and `cpm2_pic_init(struct device_node *)`.

Control flow: no executable logic; platforms include this header to initialize the CPM2 PIC and retrieve pending IRQs.

State and persistence: no state. It exposes access to state owned by `cpm2_pic.c`.

Dependencies and integration points: depends on `struct device_node` from the OF subsystem. Integrated by CPM2 platform setup code.

Risks: minimal; mismatch between prototypes and implementation would break platform builds.

Test signals: compile coverage for CPM2 platforms and successful platform interrupt dispatch through these declarations validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2_pic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm_common.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm_common.c

Purpose: shared CPM support for MURAM initialization, optional early debug console output through CPM, and CPM/8xx GPIO chip registration helpers.

Important APIs/types/functions: `cpm_init()`, early-debug `udbg_init_cpm()`/`udbg_putc_cpm()`, GPIO structure `cpm2_gpio32_chip`, helper `cpm2_gpiochip_add32()`, and GPIO callbacks for get/set/direction.

Control flow: subsystem init looks for `fsl,cpm1` or `fsl,cpm2` and initializes CPM MURAM. Early debug maps the CPM transmit descriptor/buffer, optionally sets a BAT on CPM2, and installs `udbg_putc`. GPIO add allocates a gpiochip, maps the OF register bank, snapshots output data, and registers 32 GPIOs with locked data/direction operations.

State and persistence: early debug stores static descriptor/buffer pointers. GPIO state includes the mapped bank registers, a spinlock, and a shadow `cpdata` value used to update output bits safely. MURAM allocator state is initialized outside this file.

Dependencies and integration points: depends on OF compatible nodes, CPM MURAM, `asm/udbg.h`, fixmap/BAT helpers, GPIO subsystem, devm mapping/allocation, and CPM1/CPM2 register layouts.

Risks: early debug busy-waits on descriptor ownership and assumes valid firmware-provided descriptor addresses. GPIO shadow state can go stale if other code writes the same data register. CPM2 and 8xx layouts are conditionally shared, so compatible data must choose the right add function.

Test signals: CPM MURAM users probing successfully, early boot console output over CPM, GPIO direction/value operations through gpiolib, and no register corruption during concurrent GPIO updates validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm_gpio.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm_gpio.c

Purpose: platform driver wrapper that binds CPM GPIO OF nodes to the appropriate CPM1 or CPM2 gpiochip registration helper.

Important APIs/types/functions: `cpm_gpio_probe()`, OF match table `cpm_gpio_match`, `cpm_gpio_driver`, and `cpm_gpio_init()`.

Control flow: arch init registers the platform driver. Probe retrieves the function pointer stored in match data and invokes it for the device. Match entries select CPM1 16/32-bit helpers for 8xx banks and `cpm2_gpiochip_add32()` for CPM2/port-E style banks.

State and persistence: the wrapper has no runtime state beyond the registered platform driver. Per-bank state is allocated by the selected helper.

Dependencies and integration points: integrates OF platform matching, CPM GPIO helpers from `asm/cpm.h`/`asm/cpm1.h`, and gpiolib registration.

Risks: match data must remain accurate for each bank layout. A missing helper under config guards results in the compatible not being available.

Test signals: platform driver binding to CPM GPIO nodes, gpiochip registration for each bank, and working GPIO line operations through sysfs/gpiod consumers validate this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm_gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dart.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dart.h

Purpose: register and table bit definitions for Apple/IBM U3/U4 DART IOMMU support.

Important APIs/types/functions: DART register offsets `DART_CNTL`, `DART_EXCP_*`, `DART_TAGS_*`, U4 base/size offsets, control bits for enable/flush/one-entry invalidate/idle/parity, table entry bits `DARTMAP_VALID` and `DARTMAP_RPNMASK`, and page constants `DART_PAGE_SHIFT/SIZE`.

Control flow: no executable logic; macros are consumed by `dart_iommu.c` to program the hardware.

State and persistence: no state. The macros describe persistent hardware register fields and DART table entry format.

Dependencies and integration points: tightly coupled to `dart_iommu.c` and U3/U4 chipset manuals. `DART_REG`, `DART_IN`, and `DART_OUT` assume a file-scope `dart` MMIO pointer.

Risks: register offsets and masks are hardware ABI. Incorrect values can corrupt DMA translations or hang TLB invalidation.

Test signals: DART initialization, DMA mapping/unmapping on U3/U4 systems, and successful suspend restore validate the definitions indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dart_iommu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dart_iommu.c

Purpose: dynamic DMA mapping support for Apple U3/U4 and IBM CPC925 DART IOMMUs.

Important APIs/types/functions: early entry `iommu_init_early_dart()`, optional restore `iommu_dart_restore()`, IOMMU table ops `dart_build()`, `dart_free()`, `dart_flush()`, hardware helpers `dart_tlb_invalidate_all()`, `dart_tlb_invalidate_one()`, `dart_cache_sync()`, `allocate_dart()`, `dart_init()`, and PCI setup hooks `pci_dma_bus_setup_dart()`, `pci_dma_dev_setup_dart()`, `iommu_bypass_supported_dart()`.

Control flow: early init finds `u3-dart` or `u4-dart`, skips if IOMMU is disabled or not needed for small memory without force, maps registers, allocates a 16 MiB-aligned table below 2 GiB plus a dummy page, fills invalid entries with the dummy mapping, writes table base/size/control registers, flushes DART TLB, installs PCI controller DMA setup hooks, and switches PCI DMA ops to IOMMU. Mapping writes valid RPN entries, cache-syncs them, then invalidates per-entry on U4 or marks U3 dirty for later full flush. Freeing writes dummy entries and cache-syncs. U4 PCIe devices with sufficient masks can bypass through a 40-bit offset.

State and persistence: global MMIO pointer, table base/size, dummy invalid value, `iommu_table_dart`, initialized/dirty flags, and U4 flag persist for the life of the kernel. DART table contents represent active DMA mappings.

Dependencies and integration points: depends on memblock early allocation, OF address discovery, PCI controller ops, common PowerPC IOMMU code, cache flush primitives, PCI DMA ops, suspend `ppc_md.iommu_restore`, and command-line IOMMU policy.

Risks: DART hardware is cache-incoherent, so missing `dart_cache_sync()` can cause stale translations. TLB flush loops can panic on stuck hardware. The dummy page workaround avoids HT bridge prefetch corruption; removing it risks data corruption. Bypass support must be limited to U4 PCIe devices with a large enough DMA mask.

Test signals: boot logs showing DART initialized, PCI devices DMAing correctly above 1 GiB, IOMMU map/free stress, U4 bypass for 40-bit devices, suspend/resume DMA after restore, and no DART TLB flush panics validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dart_iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dcr-low.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dcr-low.S

Purpose: native assembly implementation for indirect access to PowerPC Device Control Registers by register number.

Important APIs/types/functions: exported `__mfdcr` and `__mtdcr`, macro `DCR_ACCESS_PROLOG`, and generated jump tables `__mfdcr_table`/`__mtdcr_table` covering DCR numbers 0 through 1023.

Control flow: the prolog bounds-checks r3 against 1024, scales it to a table entry, branches through CTR to the selected `mfdcr` or `mtdcr` instruction, traps and emits a bug entry for out-of-range access, then returns. The `.rept` block emits paired read/write snippets for every DCR index.

State and persistence: no memory state. It reads or writes processor DCR state directly.

Dependencies and integration points: depends on PowerPC assembler support for DCR instructions, bug table emission, and callers in the DCR subsystem.

Risks: the generated table is large and instruction-address sensitive. Out-of-range DCR numbers deliberately trap. Caller register conventions must match r3 for DCR number and r4 for write value.

Test signals: DCR users reading/writing known registers, invalid-number bug handling, and successful link/export of `__mfdcr`/`__mtdcr` validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dcr-low.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dcr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dcr.c

Purpose: OF helper support for DCR resources plus a shared lock for indirect DCR access.

Important APIs/types/functions: exported `dcr_resource_start()`, `dcr_resource_len()`, and `dcr_ind_lock`.

Control flow: helpers fetch the `dcr-reg` property, validate property presence, even cell count, and index range, then return the start or length cell for the requested resource.

State and persistence: no per-device state. `dcr_ind_lock` is a global spinlock used by indirect DCR access paths elsewhere.

Dependencies and integration points: depends on OF properties and `asm/dcr.h`. Drivers use these helpers to parse DCR resources from device tree nodes.

Risks: invalid `dcr-reg` properties return 0, which can be ambiguous if a real DCR resource starts at 0. Callers must handle missing/invalid resources carefully.

Test signals: drivers parsing DCR resources from representative device trees and serialized indirect access under concurrency validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ehv_pic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ehv_pic.c

Purpose: IRQ controller driver for the ePAPR Embedded Hypervisor PIC, including support for direct MPIC EOI mode.

Important APIs/types/functions: `ehv_pic_init()`, `ehv_pic_get_irq()`, IRQ chip callbacks for mask/unmask/EOI/affinity/type, domain ops `ehv_pic_host_match()`, `ehv_pic_host_map()`, `ehv_pic_host_xlate()`, global `global_ehv_pic`, `hwirq_intspec`, and optional `mpic_percpu_base_vaddr`.

Control flow: init locates `epapr,hv-pic`, allocates an `ehv_pic`, creates a linear domain, optionally maps `fsl,hv-mpic-per-cpu`, sets affinity support, records core-interrupt mode from `has-external-proxy`, and installs the domain as default. IRQ dispatch reads EPR in coreint mode or uses `ev_int_iack()`, maps 0xffff to no IRQ, otherwise finds the Linux IRQ. Mapping selects normal hypervisor EOI or direct MPIC EOI based on interrupt spec flags, installs `handle_fasteoi_irq`, and applies default type.

State and persistence: persistent global state includes the IRQ domain, copied irq_chip, direct EOI MMIO mapping, per-hwirq intspec flags, and default-domain registration.

Dependencies and integration points: depends on ePAPR/FSL hypervisor interrupt calls, OF interrupt specs, Linux irqdomain/chip APIs, SMP affinity selection, and optional MPIC per-CPU EOI registers.

Risks: `hwirq_intspec` is indexed by firmware-provided hwirq and assumes it is within `NR_EHV_PIC_INTS`. Direct EOI requires a valid MPIC mapping. Type conversion uses a compact firmware encoding and must preserve polarity/sense bits.

Test signals: interrupt delivery in legacy and coreint modes, affinity changes, OF trigger-type mapping, direct MPIC EOI interrupts, and no default-domain conflicts validate the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ehv_pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_gtm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_gtm.c

Purpose: Freescale general-purpose 16-bit timer support, exporting a small allocation/configuration API for other drivers.

Important APIs/types/functions: exported `gtm_get_timer16()`, `gtm_get_specific_timer16()`, `gtm_put_timer16()`, `gtm_set_timer16()`, `gtm_set_exact_timer16()`, `gtm_stop_timer16()`, `gtm_ack_timer16()`, plus `gtm_set_ref_timer16()`, `gtm_set_shortcuts()`, and `fsl_gtm_init()`.

Control flow: arch init scans `fsl,gtm` nodes, allocates one `gtm` per node, reads `clock-frequency`, maps four IRQs, maps registers, assigns per-timer register shortcuts, stores the `gtm` in `np->data`, and links it globally. Consumers reserve any or a specific timer, configure interval/reload by computing prescaler settings, reset/stop the timer, program mode/reference/event registers under a spinlock, and release it after stopping.

State and persistence: state is a global list of GTM blocks and per-timer `requested` flags, IRQ numbers, register pointers, and parent pointer. Hardware timer mode, prescale, counter, reference, and event registers persist while programmed.

Dependencies and integration points: depends on OF timers with `clock-frequency`, four interrupts per block, endian MMIO helpers, the exported `asm/fsl_gtm.h` API, and consumers that request IRQs separately using `timer->irq`.

Risks: timer allocation is global and non-devm; no module removal exists. Prescaler math rejects intervals beyond hardware capacity and reduces precision in `gtm_set_timer16()`. CPM2 GTMs lack primary prescalers, narrowing the supported range.

Test signals: successful GTM discovery, reservation/release behavior, timer IRQ firing at approximate/exact intervals, reload vs free-run behavior, and event acknowledgment in interrupt handlers validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_gtm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_lbc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_lbc.c

Purpose: Freescale local bus controller and UPM support, including bank lookup, UPM pattern execution, event/error interrupt handling, and suspend register save/restore.

Important APIs/types/functions: exported `fsl_lbc_ctrl_dev`, `fsl_lbc_addr()`, `fsl_lbc_find()`, `fsl_upm_find()`, `fsl_upm_run_pattern()`, internal `fsl_lbc_ctrl_init()`, `fsl_lbc_ctrl_irq()`, `fsl_lbc_ctrl_probe()`, suspend `fsl_lbc_syscore_suspend/resume()`, and init `fsl_lbc_init()`.

Control flow: platform probe allocates the singleton controller, maps registers, maps one or two IRQs, clears/enables event registers, applies the eLBC monitor timeout workaround, requests IRQ handlers, and enables event interrupts. Bank helpers read BR/OR registers to match a physical base and derive UPM register pointer/width. UPM pattern execution writes MAR then performs a dummy bus write of the correct width. The IRQ handler reads/clears LTESR/LTEATR/LTEAR, records status, logs known errors, and wakes waiters for command completion, timeout, parity/ECC, or completion bits. Syscore suspend copies the whole register block and resume restores it.

State and persistence: global singleton `fsl_lbc_ctrl_dev`, mapped registers, IRQ numbers, waitqueue, last `irq_status`, and optional saved register image. Hardware bank, UPM, error, and interrupt-enable registers persist across normal runtime and are restored after suspend.

Dependencies and integration points: depends on OF platform matching (`fsl,elbc`, `fsl,pq*-localbus`), `asm/fsl_lbc.h`, NAND/UPM/localbus consumers, IRQ subsystem, and syscore suspend hooks.

Risks: singleton design assumes one controller. Error paths need to unmap/free partial resources; second IRQ setup failure frees the first. Full-register save/restore may include volatile or write-1-clear fields, but matches existing hardware expectations. UPM pattern execution must hold the shared lock around MAR and dummy access.

Test signals: localbus NAND/flash access, UPM devices executing patterns, LTESR error injection/logging, waitqueue wake on completion/error bits, and suspend/resume preserving localbus configuration validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_lbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_mpic_err.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_mpic_err.c

Purpose: support Freescale MPIC error interrupt banks as cascaded Linux IRQs.

Important APIs/types/functions: `mpic_setup_error_int()`, `mpic_map_error_int()`, `mpic_err_int_init()`, cascade handler `fsl_error_int_handler()`, IRQ chip callbacks `fsl_mpic_mask_err()` and `fsl_mpic_unmask_err()`, and chip `fsl_mpic_err_chip`.

Control flow: setup maps MPIC error registers, copies the chip, marks the MPIC as having EIMR, and assigns a contiguous set of hardware vectors for error sources. Domain mapping recognizes those vectors, installs the error chip and level handler, and stores MPIC chip data. Init maps the parent error IRQ, masks all error sources, and requests a no-thread cascade handler. The handler reads EISR/EIMR, ignores fully masked status, and dispatches each unmasked set bit through the MPIC irqdomain; dispatch failures cause that error bit to be masked.

State and persistence: error register MMIO, `mpic->err_int_vecs`, `mpic->hc_err`, and EIMR mask state persist in the MPIC structure/hardware.

Dependencies and integration points: depends on core MPIC structures and irqdomain, Freescale MPIC register layout, and platform MPIC init calling these helpers.

Risks: bit order uses `31 - src` and `__builtin_clz`, so vector-to-bit mapping must remain consistent. Secondary MPICs are warned against for error interrupts. Dispatch errors are handled by masking to avoid storms.

Test signals: MPIC error interrupt registration, per-error masking/unmasking, injected error bits causing child IRQ handlers, and no IRQ storms on unmapped errors validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_mpic_err.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_mpic_timer_wakeup.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_mpic_timer_wakeup.c

Purpose: module exposing an MPIC global timer as a sysfs-programmable wakeup timer.

Important APIs/types/functions: `struct fsl_mpic_timer_wakeup`, global `fsl_wakeup`, sysfs attribute `timer_wakeup`, `fsl_timer_wakeup_show()`, `fsl_timer_wakeup_store()`, IRQ handler `fsl_mpic_timer_irq()`, deferred cleanup `fsl_free_resource()`, and module init/exit.

Control flow: module init allocates state, initializes cleanup work, gets the MPIC bus root device, and creates `timer_wakeup`. Writing zero cancels/free any existing timer. Writing a positive interval requests an MPIC timer with the file's IRQ handler, enables IRQ wake, starts it, and stores it. IRQ handling schedules work, which disables wake and frees the timer under the sysfs mutex. Reading returns remaining time plus one when a timer exists or zero otherwise.

State and persistence: global module state holds one active timer and cleanup work. Sysfs file state is global to the MPIC subsystem root.

Dependencies and integration points: depends on MPIC timer APIs, `mpic_subsys`, IRQ wake support, sysfs device files, workqueues, and module lifecycle.

Risks: the IRQ handler checks `wakeup->timer` after scheduling work; concurrent sysfs writes are serialized by the mutex in store/free work, but IRQ/work ordering is subtle. Exit frees the state while holding the mutex after removing sysfs; pending work should be considered in module unload testing.

Test signals: creating/removing `/sys/.../timer_wakeup`, programming a timer, seeing remaining-time reads decrease, system wake from suspend, timer auto-free after IRQ, and cancellation via writing zero validate the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_mpic_timer_wakeup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_msi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_msi.c

Purpose: Freescale MSI controller driver for MPIC, IPIC, and virtual MPIC MSI blocks, wiring PCI MSI/MSI-X allocation to hardware MSI status registers and cascaded interrupts.

Important APIs/types/functions: platform driver `fsl_of_msi_driver`, probe/remove `fsl_of_msi_probe()`/`fsl_of_msi_remove()`, PCI ops `fsl_setup_msi_irqs()` and `fsl_teardown_msi_irqs()`, message composer `fsl_compose_msi_msg()`, cascade handler `fsl_msi_cascade()`, allocator `fsl_msi_init_allocator()`, hwirq setup `fsl_msi_setup_hwirq()`, irqdomain map `fsl_msi_host_map()`, and feature descriptors for MPIC/IPIC/VMPIC.

Control flow: probe creates a linear MSI irqdomain, maps hardware registers unless using VMPIC hypercalls, computes the MSIIR offset, marks MPIC v2.0 endian erratum, initializes a bitmap with all hwirqs reserved, parses available ranges or v4.3 implicit registers, maps each cascade IRQ, requests cascade handlers, and frees corresponding hwirqs into the bitmap. It then installs MSI setup/teardown ops on all PCI host bridges unless another MSI driver is present. PCI setup rejects plain MSI on PIC1 erratum hardware, honors an `fsl,msi` phandle on the PCI controller, allocates one hwirq per MSI desc, creates a virq, attaches the MSI desc, composes the MSI address/data, and writes it to PCI config. Cascades read MSIR bits from MPIC/IPIC registers or VMPIC hypercall and dispatch each set bit through the MSI irqdomain.

State and persistence: global `msi_head` tracks all MSI banks. Each `fsl_msi` stores irqdomain, register mapping, feature bits, MSIIR shifts/offset, cascade data per MSIR, bitmap allocator, and phandle. PCI devices persist assigned virqs/hwirqs until teardown.

Dependencies and integration points: depends on PCI MSI core, PowerPC PCI controller ops, irqdomain, OF address/IRQ/phandle properties, `msi_bitmap`, MPIC version queries, Freescale hypervisor calls for VMPIC, and `fsl_pci_immrbar_base()` for MSIIR address composition.

Risks: allocator starts fully reserved and only releases ranges with valid cascade IRQs; malformed `msi-available-ranges` disables probe. Error unwind calls remove on partially initialized structures. The MPIC v2.0 endian erratum blocks MSI but allows MSI-X with data byte swapping. Installing ops across all host bridges can conflict with another MSI backend.

Test signals: MSI/MSI-X enablement on FSL PCI devices, `/proc/interrupts` chip names including cascade virqs, range parsing, `fsl,msi` phandle restriction, teardown freeing hwirqs, cascade dispatch from MSIR bits, VMPIC hypercall paths, and erratum behavior validate the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_msi.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_msi.h

Purpose: private Freescale MSI controller definitions shared by the MSI implementation.

Important APIs/types/functions: constants for MSIIR/MSIIR1 register counts, interrupts per MSIR, maximum hwirqs, PIC type feature bits, endian erratum flag, forward `fsl_msi_cascade_data`, and `struct fsl_msi`.

Control flow: no executable logic. The constants define hwirq geometry and feature decoding used by `fsl_msi.c`.

State and persistence: `struct fsl_msi` models one MSI controller's persistent runtime state: irqdomain, cascade IRQ, MSIIR offset/bit shifts, MMIO registers, feature flags, cascade data array, bitmap allocator, global list node, and OF phandle.

Dependencies and integration points: depends on OF phandles and the PowerPC `msi_bitmap` allocator. Used by Freescale PCI/MSI code.

Risks: changing register counts or bit shifts without matching hardware support can make hwirq composition collide or exceed bitmap size. The maximum is based on MSIIR1 geometry and must cover all supported variants.

Test signals: compile coverage and runtime MSI allocation across MPIC, IPIC, and v4.3 MSIIR1-compatible controllers validate the definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_msi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pci.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pci.c

Purpose: Freescale MPC83xx/85xx/86xx PCI and PCIe host controller support, including bridge creation, config-space access quirks, ATMU window programming, DMA window setup, primary bridge selection, machine-check recovery, PME suspend hooks, and EDAC companion registration.

Important APIs/types/functions: exported/platform functions `fsl_pcibios_fixup_bus()`, `fsl_pcibios_fixup_phb()`, `mpc83xx_add_bridge()`, `fsl_pci_immrbar_base()`, `fsl_pci_mcheck_exception()`, `fsl_pci_assign_primary()`, static `fsl_add_bridge()`, `setup_pci_atmu()`, `setup_one_atmu()`, `fsl_pcie_check_link()`, `fsl_indirect_read_config()`, MPC83xx-specific config ops, PME syscore handlers, and platform driver `fsl_pci_driver`.

Control flow: early PCI fixup normalizes Freescale PCIe root bridge class codes. Bridge setup maps controller registers, allocates a `pci_controller`, sets indirect or MPC83xx config ops, validates PCIe link/host mode or PCI agent mode, enables command bits, applies controller errata, processes OF ranges, programs outbound and inbound ATMU windows, and enables SWIOTLB/device DMA setup when needed. `setup_pci_atmu()` disables windows, maps MEM/IO resources outwards, positions PCICSRBAR, creates inbound DMA windows sized to DRAM and optionally a 64-bit window, and handles kdump by avoiding inbound-window teardown. MPC83xx PCIe remaps type0/type1 config windows dynamically. Machine-check recovery recognizes loads from PCI memory space and synthesizes all-ones load results while advancing NIP. PM code sends PME turn-off/exit-L2 messages and reprograms ATMUs after resume.

State and persistence: global flags track FSL PCIe bus fixup and MPC83xx mode, `pci64_dma_offset` and `ppc_md.dma_set_mask` support 64-bit inbound DMA, `fsl_pci_primary` records the selected primary PHB, and each hose stores MMIO mappings, ranges, DMA window limits, and private data. Hardware ATMU, command, class-code, PME, and link-state registers persist across runtime and are restored/reprogrammed after resume.

Dependencies and integration points: depends on OF platform devices/ranges, PowerPC PCI controller infrastructure, indirect PCI ops, memblock DRAM size, SWIOTLB, EDAC platform device registration, MPIC/PME IRQs, PowerPC instruction decode helpers, and Freescale SoC revision/IMMR helpers.

Risks: ATMU sizing is complex and constrained by power-of-two windows, limited outbound/inbound slots, kdump in-flight DMA, and MSIIR placement. Link-state handling suppresses config access when links are down. Machine-check emulation must only handle safe load instructions from PCI memory. Primary bridge selection retains OF node references and must be coordinated with platform setup.

Test signals: PCI/PCIe enumeration on supported SoCs, link-down config access returning no devices, correct MEM/IO resources behind root bridges, DMA above 4 GiB with and without SWIOTLB, MSI address composition via IMMRBAR, kdump boot with in-flight DMA, PME suspend/resume, and recoverable PCI master-abort machine checks validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pci.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pci.h

Purpose: Freescale PCI/PCIe register layout and exported helper declarations.

Important APIs/types/functions: register constants for BRR1, LTSSM, class-code CSR, inbound/outbound window attributes, PME bits, structures `pci_outbound_window_regs`, `pci_inbound_window_regs`, and large `ccsr_pci`, plus declarations for bus/PHB fixups, `mpc83xx_add_bridge()`, `fsl_pci_immrbar_base()`, `fsl_pci_primary`, `fsl_pci_assign_primary()`, and `fsl_pci_mcheck_exception()`.

Control flow: no runtime logic except config-dependent inline stubs for primary assignment and machine-check handling when PCI/FSL PCI is disabled.

State and persistence: describes the memory-mapped controller state used by `fsl_pci.c`, including config, outbound/inbound ATMUs, error capture, debug, CSR, and PME registers.

Dependencies and integration points: included by Freescale PCI/MSI/EDAC-related code and depends on kernel-only build context plus `struct pci_bus`, `pci_controller`, and `pt_regs` declarations from included headers.

Risks: structure padding and offsets must match hardware. Incorrect masks or bit definitions can program invalid ATMU or PME state.

Test signals: compile-time offset-sensitive users, successful PCI bridge setup, ATMU programming, and PME operations validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pmc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pmc.c

Purpose: simple Freescale PMC standby suspend support for MPC8548/MPC8641D-style power management controllers.

Important APIs/types/functions: `struct pmc_regs`, globals `pmc_dev` and `pmc_regs`, suspend callbacks `pmc_suspend_valid()` and `pmc_suspend_enter()`, `pmc_probe()`, OF match table `pmc_ids`, and `pmc_driver`.

Control flow: platform probe maps PMC registers and installs `platform_suspend_ops`. Only `PM_SUSPEND_STANDBY` is accepted. Enter sets `PMCSR_SLP`, relies on hardware to sleep the CPU, then on resume polls until the sleep bit clears or times out.

State and persistence: global mapped PMC registers and device pointer persist after probe. The PMCSR sleep bit is transient hardware state across standby.

Dependencies and integration points: depends on OF platform matching, PM core `suspend_set_ops()`, endian MMIO bit helpers, and compatible PMC hardware.

Risks: singleton globals assume only one PMC. Timeout after resume indicates hardware/firmware failed to clear sleep state. Probe does not provide remove/unmap because this is builtin platform support.

Test signals: `/sys/power/state` standby entering/resuming on matching systems, PMCSR sleep bit clearing, and timeout/error logging for failed wake validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rcpm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rcpm.c

Purpose: QorIQ Run Control/Power Management support for CPU idle/offline, platform sleep, IP block power control, interrupt masking, and time-base freeze across RCPM v1/v2 hardware.

Important APIs/types/functions: init `fsl_rcpm_init()`, ops tables `qoriq_rcpm_v1_ops` and `qoriq_rcpm_v2_ops`, IRQ mask/unmask helpers, CPU enter/exit/up/die helpers, platform sleep helpers, `rcpm_*_set_ip_power()`, `rcpm_*_freeze_time_base()`, `rcpm_get_pm_modes()`, and `qoriq_pm_ops` assignment.

Control flow: init finds a compatible RCPM node, maps registers, sets supported modes to sleep, and publishes the matching v1/v2 ops table. CPU PM callbacks set or clear per-CPU/thread PH10/PH15/PH20/PH30 request/clear registers. Offline for v2 may disable one thread or place a whole core into PH20 depending on thread sibling state. Platform sleep sets the sleep/LPM20 request bit and polls for status clear after resume. IRQ callbacks mask/unmask interrupt classes per hardware CPU. Time-base freeze snapshots enabled bits, clears them, then restores them on unfreeze.

State and persistence: global v1/v2 register pointers alias the same mapped base, `fsl_supported_pm_modes`, and a static time-base mask in `rcpm_common_freeze_time_base()`. Hardware PM request/mask/power/time-base registers persist until changed.

Dependencies and integration points: depends on OF matching, QorIQ GUTS register definitions, `asm/fsl_pm.h`, CPU threading helpers, Book3E thread stop on PPC64, and platform PM/CPU hotplug code consuming `qoriq_pm_ops`.

Risks: hard CPU IDs and thread/core indexes differ; wrong mask calculations can affect the wrong CPU or thread. The static time-base mask is shared across v1/v2 calls and assumes serialized freeze/unfreeze. Sleep polling failures return `-ETIMEDOUT`.

Test signals: CPU hotplug/offline on QorIQ, idle state entry/exit, suspend-to-sleep/LPM20, IP power gating, time-base freeze/resume, and interrupt delivery after mask/unmask validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rcpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rio.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rio.c

Purpose: Freescale MPC85xx/MPC86xx Serial RapidIO master-port support, including local/maintenance config access, inbound memory windows, machine-check recovery, port error clearing, RMU doorbell/port-write/message integration, and mport registration.

Important APIs/types/functions: platform setup `fsl_rio_setup()` and `fsl_of_rio_rpn_probe()`, config ops `fsl_local_config_read/write()` and `fsl_rio_config_read/write()`, inbound mapping ops `fsl_map_inb_mem()` and `fsl_unmap_inb_mem()`, `fsl_rio_port_error_handler()`, optional exported `fsl_rio_mcheck_exception()`, global `rio_regs_win`, `rmu_regs_win`, `rio_law_start`, `dbell`, and `pw`.

Control flow: probe maps SRIO and RMU registers, allocates `rio_ops`, locates message/doorbell/port-write nodes, allocates doorbell and port-write state, then iterates child port nodes. For each port it reads `cell-index` and LAW range, allocates and initializes a `rio_mport` plus private data, reserves the IO resource, checks/restarts port training if needed, reports link width/status, configures host/master flags, sets ATMU pointers, accepts all destination IDs, programs the maintenance window, maps it, initializes RMU and inbound ATMUs, stores mport pointers in doorbell/port-write structures, and registers the mport. Config reads/writes serialize access to a single maintenance ATMU window and validate offset/length alignment; reads use exception-table protected loads. Inbound mapping validates power-of-two size, alignment, overlap, and free ATMU availability before programming translation registers.

State and persistence: global SRIO/RMU MMIO windows, LAW start, doorbell and port-write singleton state, per-mport resources, `rio_priv` register/window pointers, and hardware ATMU/port status registers persist while the driver is active.

Dependencies and integration points: depends on RapidIO core, OF nodes/properties for SRIO/RMU/message/doorbell/port-write units, DMA/resource APIs, exception tables for fault-tolerant maintenance reads, FSL RMU helper functions declared in `fsl_rio.h`, and optional PPC_E500 machine-check path.

Risks: single global RMU/doorbell/port-write state assumes one SRIO complex. Maintenance window access is serialized globally because the ATMU target is reprogrammed per transaction. Error cleanup frees only some partially registered per-port resources. Inbound overlap checks use hardware window fields and must match size encoding. Port restart is heuristic and may fail on bad links.

Test signals: SRIO mport registration, config read/write to local and remote devices, maintenance read fault recovery, doorbell and port-write interrupts, inbound memory map/unmap validation, link restart logs, and RapidIO enumeration over active ports validate this driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rio.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rio.h

Purpose: shared Freescale RapidIO constants, register structures, private state structures, globals, and RMU helper declarations.

Important APIs/types/functions: macros for register windows and ATMU offsets, doorbell ROWAR flags, maximum message/port counts, structures `rio_atmu_regs`, `rio_inb_atmu_regs`, `rio_dbell_ring`, `rio_port_write_msg`, `fsl_rio_dbell`, `fsl_rio_pw`, `rio_priv`, extern globals `rio_regs_win`, `rmu_regs_win`, `rio_law_start`, `dbell`, `pw`, and declarations for RMU/doorbell/message/port-write functions.

Control flow: no executable logic. The structures define how `fsl_rio.c` and RMU support files share controller state and hardware register mappings.

State and persistence: the declared structures persist per controller or RMU unit: mport arrays, device pointers, MMIO register pointers, DMA rings/messages, IRQ numbers, work and FIFO state, maintenance windows, and message manager handles.

Dependencies and integration points: depends on Linux RapidIO core, kfifo, DMA address types, and companion RMU implementation files (`fsl_rmu.c` and related helpers). Used directly by `fsl_rio.c`.

Risks: register structure fields are raw 32-bit hardware registers and must remain offset-compatible. Global externs constrain the driver toward singleton hardware.

Test signals: successful build/link with RMU helpers, correct doorbell/port-write/message-unit operation, and valid register programming through `fsl_rio.c` validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rio.h -->
