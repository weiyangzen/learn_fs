# Research: subset-b-004255

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5261.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5261.c

Purpose: implements the Realtek RTS5261 PCIe card-reader chip policy layer used by the common `rtsx_pcr.c` PCI driver. It fills a `struct pcr_ops` table with RTS5261-specific power, clock, voltage, ASPM, LED, and over-current-protection operations, and initializes `struct rtsx_pcr` defaults in `rts5261_init_params()`.

Important APIs, types, and functions: `rts5261_init_params()` is the exported chip initializer called from the common PCI probe path. `rts5261_pci_switch_clock()` is the chip-specific clock programming routine used through `rtsx_pci_switch_clock()`. The static `rts5261_pcr_ops` table wires callbacks for `extra_init_hw`, `card_power_on`, `card_power_off`, `switch_output_voltage`, `force_power_down`, `stop_cmd`, `set_aspm`, `set_l1off_cfg_sub_d0`, and OCP helpers. The implementation depends on `struct rtsx_pcr`, `struct rtsx_cr_option`, and `struct rtsx_hw_param` from the Realtek PCI cardreader core.

Control flow: common probe calls `rts5261_init_params()` to set capabilities and callback pointers, then `rtsx_pci_init_hw()` invokes `rts5261_extra_init_hw()`. Extra init enables card-detect resume, applies LTR config, reads efuse/vendor settings through `rts5261_init_from_hw()`, powers down efuse, configures L1 substate/clock/LED/drive registers, handles reverse-socket and CLKREQ policy, and clears RTD3-cold firmware state. Card power-on enables OCP when configured, powers LDO1 and LDO3318, waits 20 ms, enables SD output, resets SD timing registers, and enters SD 3.0 timing mode for SDR50/SDR104. Power-off stops command/DMA, restores 3.3 V signalling, disables LDO rails, clears auto power-down, and disables OCP. Interrupt-time OCP processing reads OCP status, clears it, powers off the SD card, disables SD output, and resets cached status.

State and persistence: persistent hardware-derived state is loaded from efuse or PCI config vendor-setting registers into `pcr->rtd3_en`, `pcr->aspm_en`, `pcr->sd30_drive_sel_1v8`, `pcr->sd30_drive_sel_3v3`, and `pcr->flags`. If settings come from PCI config register 1/2, they are mirrored into internal autoload registers and PCI config register 4/5. Runtime state includes `pcr->cur_clock`, `pcr->aspm_enabled`, `pcr->ocp_stat`, `pcr->extra_caps`, and LTR/OCP fields in `pcr->option` and `pcr->hw_param`.

Dependencies and integration points: this file is tightly coupled to `rtsx_pcr.c` exported register/PHY helpers, `linux/rtsx_pci.h` register definitions, `rts5261.h` constants, PCI config access, and the SD/MMC child driver that calls exported PCI card operations through the MFD handle. It also participates in PCI runtime PM through `force_power_down` and ASPM/L1SS callbacks.

Risks: almost every path writes undocumented hardware registers, so register bit mistakes can cause card-detect loss, power rail sequencing bugs, DMA hangs, or wake/resume failures. `rts5261_init_from_hw()` silently returns on unknown efuse-valid values, leaving defaults active. OCP handling powers off the card from interrupt context through register writes; regressions can look like spontaneous card removal. Clock conversion rejects invalid `n` ranges and updates `pcr->cur_clock`; stale current-clock state can skip needed reprogramming.

Test signals: useful tests include probe/resume/runtime-suspend on RTS5261 hardware, SD card insertion/removal, SDR50/SDR104/SD Express capability exposure, 1.8 V voltage switching, LTR/ASPM toggling under runtime PM, OCP fault injection or rail-short tests, and DMA timeout recovery. Kernel logs from `pcr_dbg()` around efuse/vendor settings and clock switches are strong diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5261.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5261.h -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5261.h

Purpose: provides RTS5261-specific register addresses, bit masks, efuse/vendor-setting decoders, LDO/OCP constants, SSC depth constants, and the `rts5261_pci_switch_clock()` prototype for the RTS5261 cardreader implementation.

Important APIs, types, and functions: the macros `rts5261_vendor_setting_valid()`, `rts5261_reg_to_aspm()`, `rts5261_reg_check_reverse_socket()`, `rts5261_reg_to_sd30_drive_sel_1v8()`, `rts5261_reg_to_sd30_drive_sel_3v3()`, `rts5261_reg_to_rtd3()`, and `rts5261_reg_check_mmc_support()` are the public decode layer used by `rts5261_init_from_hw()`. The header declares `rts5261_pci_switch_clock(struct rtsx_pcr *, unsigned int, u8, bool, bool, bool)`.

Control flow: the header has no executable control flow, but its constants drive RTS5261 initialization, power sequencing, efuse reads, firmware status checks, LDO tuning, OCP threshold selection, force-power-down, SD Express capability detection, and clock spread-spectrum programming in `rts5261.c` and the common PCI core.

State and persistence: the key persistent contract is mapping vendor/efuse bits into runtime `pcr` fields. Register definitions cover autoload configuration (`RTS5261_AUTOLOAD_CFG*`), efuse access, firmware status/control, LDO power/tuning registers, OCP thresholds, and PME force-control state used across suspend/resume.

Dependencies and integration points: included by `rts5261.c` and `rtsx_pcr.c`; depends on `struct rtsx_pcr` being visible through the common Realtek PCI headers. The `DEFAULT_SINGLE`, `SD_LUN`, and `SD_EXPRESS_LUN` macros align with the chip's single-LUN SD/SD Express model.

Risks: duplicate generic-sounding macros such as `FORCE_PM_CONTROL`, `REG_EFUSE_*`, and LUN constants can collide if include ordering changes. Bitfield decode macros assume the vendor-setting register layout; a chip revision with a changed layout would produce wrong ASPM, drive-strength, MMC, or RTD3 policy.

Test signals: compile coverage is important because this header is macro-heavy. Runtime validation comes from confirming efuse/vendor settings in debug output produce expected `pcr` fields, SD Express capability follows `RTS5261_FW_STATUS`, and OCP/LDO threshold constants match hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5261.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5264.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5264.c

Purpose: implements the Realtek RTS5264 PCIe card-reader chip policy layer. It is structurally similar to RTS5261 but adds RTS5264-specific OCP/OVP domains, B-revision efuse/PHY workarounds, CD/WP reverse handling, and chip-specific clock programming.

Important APIs, types, and functions: `rts5264_init_params()` initializes `struct rtsx_pcr` capabilities and installs `rts5264_pcr_ops`; `rts5264_pci_switch_clock()` is the public clock callback; `rts5264_extra_init_hw()` performs chip init after the common PCI engine is configured; `rts5264_optimize_phy()` applies subsystem/revision-specific PHY tuning. OCP helpers include `rts5264_enable_ocp()`, `rts5264_disable_ocp()`, `rts5264_init_ocp()`, `rts5264_get_ocpstat2()`, `rts5264_get_ovpstat()`, `rts5264_clear_ocpstat()`, and `rts5264_process_ocp()`.

Control flow: common probe selects `rts5264_init_params()`, then common hardware init calls `optimize_phy` and `extra_init_hw`. Extra init enables card-detect resume, VREF suspend power, OOBS/LTR policy, efuse/vendor setting extraction, LDO slew-rate and early output-enable settings, memory power-down, PRSNT release, LED setup, drive-strength configuration, CD/WP reverse register programming, CLKREQ force behavior, and RTD3 PME force policy. Power-on enables OCP, powers LDO1 and LDO3318, enables SD output, resets SD state, and configures SD 3.0 timing when UHS capabilities are present. OCP processing checks SD, SDVIO, VDD3, and OVP status domains and powers off the card on any fault.

State and persistence: `rts5264_init_from_hw()` powers efuse, reads efuse validity and length, chooses between PCI setting registers and efuse shadow registers, and stores config into autoload/config registers when using default PCI settings. It updates `pcr->rtd3_en`, `pcr->flags`, `pcr->option.sd_cd_reverse_en`, `pcr->option.sd_wp_reverse_en`, ASPM, drive selections, OCP/OVP status caches, and SD Express capability. Runtime `pcr->cur_clock` prevents redundant clock reprogramming.

Dependencies and integration points: depends on `rtsx_pcr.c` common register, PHY, command, interrupt, PM, and OCP wrappers; `rts5264.h` constants; `linux/rtsx_pci.h`; PCI config and subsystem IDs. The SD/MMC child driver consumes the card operations through the common Realtek PCI MFD device.

Risks: the B-revision efuse workaround writes long tables of magic autoload values and PCI config `0x718`; incorrect revision checks can destabilize link/power behavior. OCP/OVP coverage is broader than RTS5261, so missed clear or enable bits can cause persistent fault latches. `rts5264_pci_switch_clock()` has revision-specific SSC reset behavior; a clock programming bug can break UHS timing. `rts5264_process_ocp()` may power off cards for transient or misread fault status.

Test signals: validate cold probe and resume across RTS5264 revisions A/B/C, especially B-revision PHY and efuse behavior. Exercise SD insertion/removal with normal and reverse CD/WP wiring, SDR50/SDR104/SD Express paths, voltage switching, OCP/OVP interrupts, runtime PM with L1SS, and performance/CRC stability across clock changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5264.h -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5264.h

Purpose: defines the RTS5264 register map and bit-level constants used by `rts5264.c`, including autoload, efuse, firmware, LDO, OCP, OVP, clock, power-cut, and revision identifiers.

Important APIs, types, and functions: vendor-setting decode macros include `rts5264_vendor_setting_valid()`, `rts5264_reg_to_aspm()`, `rts5264_reg_check_reverse_socket()`, `rts5264_reg_check_wp_reverse()`, `rts5264_reg_to_sd30_drive_sel_1v8()`, `rts5264_reg_to_sd30_drive_sel_3v3()`, and `rts5264_reg_to_rtd3()`. It declares `rts5264_pci_switch_clock()`. Revision constants `RTS5264_IC_VER_A`, `RTS5264_IC_VER_B`, and `RTS5264_IC_VER_C` gate workarounds.

Control flow: no executable code is present, but the definitions select control-flow branches in `rts5264.c` for efuse handling, OCP/OVP enable/clear, voltage switching, B-revision clock/PHY behavior, reverse socket/write-protect handling, and SD Express capability detection.

State and persistence: constants describe hardware state persisted in efuse/autoload registers and PCI config shadows. `RTS5264_AUTOLOAD_CFG*`, `RTS5264_EFUSE_*`, `RTS5264_FW_STATUS`, `RTS5264_FW_CTL`, LDO threshold macros, OCP/OVP status/clear bits, and PME force-control bits form the state contract used during probe, runtime PM, and fault handling.

Dependencies and integration points: included by `rts5264.c` and common `rtsx_pcr.c`. The header shares generic names like `FORCE_PM_CONTROL` with other chip headers, so it relies on current include usage. It integrates with `linux/rtsx_pci.h` register conventions and `struct rtsx_pcr` callback prototypes.

Risks: register constants are hardware-specific and mostly not self-verifying. OCP/OVP bit definitions across multiple registers must remain synchronized with process/clear logic. Misdefined revision constants or vendor-setting macros would route init through the wrong workaround path.

Test signals: build coverage across all Realtek cardreader objects, debug-log confirmation of detected IC version, hardware validation of OCP/OVP status bits, and smoke tests of RTS5264 SD/SD Express operation after suspend/resume are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5264.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtsx_pcr.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtsx_pcr.c

Purpose: provides the common PCIe Realtek card-reader driver. It binds supported Realtek PCI IDs, allocates the controller state, maps MMIO and DMA buffers, exposes SD/MMC child devices through MFD, exports register/PHY/command/DMA/card-power helpers, handles interrupts and card-detect work, and implements system/runtime PM.

Important APIs, types, and functions: module parameter `msi_en` controls MSI usage. Exports include `rtsx_pci_start_run()`, `rtsx_pci_write_register()`, `rtsx_pci_read_register()`, `rtsx_pci_write_phy_register()`, `rtsx_pci_read_phy_register()`, `rtsx_pci_stop_cmd()`, `rtsx_pci_add_cmd()`, `rtsx_pci_send_cmd()`, `rtsx_pci_dma_map_sg()`, `rtsx_pci_dma_unmap_sg()`, `rtsx_pci_dma_transfer()`, `rtsx_pci_read_ppbuf()`, `rtsx_pci_write_ppbuf()`, pull-control helpers, card power/exclusive/voltage helpers, and unfinished-transfer completion. `rtsx_pci_probe()`, `rtsx_pci_remove()`, PM callbacks, `rtsx_pci_isr()`, and `rtsx_pci_card_detect()` are the core driver lifecycle.

Control flow: PCI probe enables the device, requests regions, allocates `struct rtsx_pcr` plus `struct pcr_handle`, assigns an IDR id, maps BAR 0 or BAR 1 depending on PID, allocates a coherent command/SG buffer, enables MSI if requested, acquires IRQ, initializes the chip by dispatching to PID-specific `*_init_params()`, then registers MFD children. Hardware init enables bus interrupts, powers SSC, disables ASPM, optionally optimizes PHY, programs common clock/link/card-drive defaults, initializes OCP, enables CLKREQ/L1, calls chip `extra_init_hw`, and initializes `card_exist`. Interrupt flow clears `RTSX_BIPR`, handles OCP/OVP, tracks card insert/remove bits, completes command/DMA waiters, and schedules delayed card-detect work that notifies child slot callbacks. Runtime idle sets idle state, disables LED/blink, applies LTR/L1SS power-saving, enables ASPM, and may schedule RTD3 suspend; runtime resume reinitializes hardware and notifies the SD child.

State and persistence: `struct rtsx_pcr` holds MMIO base, coherent command buffer, SG table, slots, IRQ, MFD handle, card presence, pending insert/remove events, command indices, transfer completion pointer/result, ASPM/LTR/OCP policy, chip ops, runtime state, and removal flag. IDR state gives stable MFD instance IDs. Hardware state is maintained in PCI config space, MMIO registers, PHY registers, interrupt masks, and L1/LTR settings. DMA error count persists between transfers and can lower RTS5227 SDR104 clock.

Dependencies and integration points: depends on Linux PCI, MFD, DMA mapping, interrupts, completions, runtime PM, IDR, `linux/rtsx_pci.h`, and chip-specific initializers from RTS5209/5229/5249/525A/5260/5261/5228/5264 families. The primary consumers are Realtek SD/MMC and MemoryStick child drivers receiving `struct pcr_handle` platform data.

Risks: shared mutable fields such as `pcr->done`, `trans_result`, command indices, and card event flags depend on spinlocks and completion lifetime; races can cause missed completions or use-after-remove. DMA and command paths stop hardware on most errors but must not stop after `-ENODEV`. Probe error unwinding spans IRQ, MSI, DMA, ioremap, IDR, and allocated handles. Runtime PM can conflict with child requests if start/idle transitions are misordered. Hardware register writes are chip-sensitive and branch heavily on PID.

Test signals: PCI probe/remove on all supported IDs, MSI and INTx IRQ modes, MFD child creation, SD card insert/remove notifications, DMA read/write stress, command timeout handling, runtime suspend/resume, system suspend/resume, OCP interrupts, and hot-unplug/removal tests. Dynamic debug for register and clock paths plus child mmc test traffic are high-value signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtsx_pcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtsx_pcr.h -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtsx_pcr.h

Purpose: declares shared private constants, vendor-setting decode macros, chip initializer prototypes, pull-control table macro, and generic helper prototypes for the Realtek PCI cardreader driver family.

Important APIs, types, and functions: prototypes cover low-level PHY access (`__rtsx_pci_write_phy_register()`, `__rtsx_pci_read_phy_register()`), every chip initializer (`rts5209_init_params()` through `rts5264_init_params()`), LTR/L1/OCP helpers, and OOBS polling helpers. `map_sd_drive()` converts a drive-strength index into hardware drive selection. `set_pull_ctrl_tables()` assigns SD/MS pull-control table pointers in `struct rtsx_pcr`.

Control flow: the header determines compile-time call targets used by `rtsx_pcr.c` chip dispatch and by individual chip files. The decode macros shape vendor-setting parsing in older chip implementations outside this work item and the helper prototypes shape generic OCP/PM dispatch.

State and persistence: constants define min/max SSC divider limits, default LTR latencies, default L1 snooze delay, command timeout, SSC stable delay, and OCP threshold defaults. Vendor-setting macros map persistent PCI/efuse config fields into runtime `pcr` policy such as MMC support, RTD3, UHS-II RTD3, ASPM, drive strengths, and reversed socket/CD/WP wiring.

Dependencies and integration points: included by common and chip-specific Realtek PCI cardreader sources. It depends on `linux/rtsx_pci.h` for `struct rtsx_pcr` and register/flag definitions. It is the private coordination point between common driver lifecycle code and chip implementation files.

Risks: macro-only bitfield parsing has no type safety and silently accepts unexpected register layouts. Default latency/threshold constants affect power/performance behavior across multiple chips. Because this is a shared private header, changing generic macros can regress chip files not in this subset.

Test signals: all Realtek cardreader objects should compile after changes. Runtime validation requires checking debug logs for decoded vendor settings and confirming each supported PCI ID still selects the intended initializer and OCP/LTR defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtsx_pcr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtsx_usb.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtsx_usb.c

Purpose: implements the common Realtek USB card-reader parent driver. It binds Realtek USB reader IDs, initializes the USB chip, exposes SD and MemoryStick child devices through MFD hotplug cells, exports register/PPBUF/clock/data-transfer helpers, and handles autosuspend and USB reset coordination.

Important APIs, types, and functions: module parameter `polling_pipe` selects control endpoint versus bulk command polling for card status. Exports include `rtsx_usb_transfer_data()`, `rtsx_usb_read_ppbuf()`, `rtsx_usb_write_ppbuf()`, endpoint-0 register access, command assembly/send/response helpers, `rtsx_usb_get_card_status()`, register access, `rtsx_usb_switch_clock()`, and `rtsx_usb_card_exclusive_check()`. Driver lifecycle functions are `rtsx_usb_probe()`, `rtsx_usb_disconnect()`, PM callbacks, and pre/post-reset locks.

Control flow: probe allocates `struct rtsx_ucr`, command/response buffers, sets USB IDs, initializes the chip with `rtsx_usb_init_chip()`, initializes the SG timeout timer, and registers SD/MS child MFD devices. Chip init clears FSM errors, powers SSC, reads hardware version and package, detects RTS5179 variation, and calls `rtsx_usb_reset_chip()` to program pull control, deglitch, drive, DMA async, interrupt, OCP, and non-crystal PHY settings. Data transfer uses either bulk messages or USB scatter-gather with a timer that cancels timed-out SG transfers. Autosuspend checks card presence while holding `dev_mutex`; if a card exists or an operation is active, suspend is deferred.

State and persistence: `struct rtsx_ucr` stores USB device/interface pointers, vendor/product IDs, buffers, current clock, package and IC variation, SG transfer state, timer, and mutex. Hardware state lives in USB-accessed registers for command buffer, SSC clock, card status, OCP, pull controls, and PHY. No on-disk persistence is involved.

Dependencies and integration points: depends on Linux USB core, MFD hotplug devices, timers, mutexes, scatter-gather USB API, and `linux/rtsx_usb.h`. Child Realtek USB SD/MMC and MemoryStick drivers use the exported helpers through the MFD parent.

Risks: command buffers are shared and require child-driver serialization around `dev_mutex`; misuse can corrupt command streams. SG timeout handling depends on timer deletion semantics. `rtsx_usb_ep0_read_register()` copies a byte even when `usb_control_msg()` returns an error, although the function returns that error. Autosuspend decisions depend on card-status reads that can fail or race with ongoing operations. Clock programming rejects invalid frequencies but stale `ucr->cur_clk` can skip needed reconfiguration.

Test signals: probe/disconnect for USB IDs 0x0129/0x0139/0x0140, child device creation, SD/MS card insertion/removal, bulk and endpoint-0 polling modes, SG and non-SG transfers, clock switching for initial and high-speed modes, USB autosuspend/resume with and without inserted media, and USB reset_resume with active children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtsx_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cb710/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/cb710/Kconfig

Purpose: declares build-time configuration for the ENE CB710/CB720 flash memory card reader core and optional debug support.

Important APIs, types, and functions: `CONFIG_CB710_CORE` is a tristate depending on PCI and builds the `cb710` module/core. `CONFIG_CB710_DEBUG` is a developer-oriented bool depending on the core and enables verbose debug output through `-DDEBUG`. `CONFIG_CB710_DEBUG_ASSUMPTIONS` is a hidden bool defaulting to yes when the core is enabled and gates internal assumption checks in the code.

Control flow: Kconfig choices determine whether `core.o` and `sgbuf2.o` are built and whether `debug.o` plus additional debug assertions are included. Users must separately enable child flash-card format drivers such as MMC/SD or MemoryStick.

State and persistence: no runtime state is stored here; it controls compilation and module availability.

Dependencies and integration points: integrated with the Linux Kconfig system under `drivers/misc`. The core's PCI dependency matches `core.c`; debug settings match `debug.c` and debug assumption blocks in `core.c`.

Risks: enabling debug can create a lot of dmesg output. The hidden default-on assumption checks can turn logical mistakes into BUGs on unusual platform-device lifetimes when debugging assumptions are compiled in.

Test signals: expected build matrix includes `CB710_CORE=m/y/n`, debug on/off, and child media driver combinations. Kconfig dependency checks should prevent non-PCI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cb710/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cb710/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/cb710/Makefile

Purpose: defines object composition for the ENE CB710 cardreader driver.

Important APIs, types, and functions: `ccflags-$(CONFIG_CB710_DEBUG) := -DDEBUG` enables `dev_dbg()` output when debugging is selected. `obj-$(CONFIG_CB710_CORE) += cb710.o` builds the aggregate module. `cb710-y := core.o sgbuf2.o` always includes core PCI/platform-slot logic and SG iterator helpers; `cb710-$(CONFIG_CB710_DEBUG) += debug.o` adds register dumping.

Control flow: no runtime control flow; Kbuild combines objects based on Kconfig.

State and persistence: no runtime state. The Makefile controls compilation products.

Dependencies and integration points: paired with `cb710/Kconfig` and source files in the same directory. Child drivers link against exported symbols from `core.o` and `sgbuf2.o`.

Risks: debug-only `debug.o` means calls to `cb710_dump_regs()` must be guarded or only present when `CONFIG_CB710_DEBUG` exports it. Object composition must stay aligned with exported symbols used by child drivers.

Test signals: verify builds with `CONFIG_CB710_CORE=m`, `CONFIG_CB710_DEBUG=y/n`, and link checks for exported CB710 helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cb710/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cb710/core.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cb710/core.c

Purpose: implements the ENE CB710/CB720 PCI card-reader core. It configures PCI hardware, creates platform devices for detected media slots, routes shared IRQs to child slot handlers, and exports helper functions for child drivers.

Important APIs, types, and functions: `cb710_pci_update_config_reg()` updates a PCI config dword and is exported. `cb710_set_irq_handler()` installs per-slot IRQ callbacks under `chip->irq_lock` and is exported. `cb710_probe()` and `cb710_remove_one()` are the PCI lifecycle. `cb710_register_slot()` and `cb710_unregister_slot()` create/remove platform devices such as `cb710-mmc`, `cb710-ms`, and `cb710-sm`. `cb710_irq_handler()` fans the shared PCI IRQ out across registered slots.

Control flow: probe first applies hardware-specific PCI config writes, reads config register `0x48` to discover enabled slot bits, allocates a variable-sized `struct cb710_chip`, enables the PCI device with managed resources, maps BAR 0, requests the IRQ, allocates a platform id through `ida`, and registers platform slot devices for MMC, MemoryStick, and SmartMedia based on hardware mask bits. Remove unregisters slots in reverse order and frees the ID. Suspend frees the IRQ and resume requests it again.

State and persistence: `struct cb710_chip` holds mapped I/O base, slot array, slot count, slot mask, platform id, IRQ lock, and debug reference counts. `struct cb710_slot` holds per-slot I/O base, platform device, and child IRQ handler. Hardware state is partly persisted in PCI config registers touched by `cb710_pci_configure()`.

Dependencies and integration points: depends on PCI, platform devices, IDA, spinlocks, `linux/cb710.h`, and child slot drivers that bind to the registered platform devices and call `cb710_set_irq_handler()`. IRQ sharing is cooperative: children provide callbacks that return whether they handled an interrupt.

Risks: slot registration error paths unwind only previously registered slots; mistakes can leave platform devices registered or IDs leaked. Shared IRQ dispatch runs under a spinlock, so child IRQ handlers must be fast and cannot sleep. The driver uses magic PCI config values derived from a Windows driver, so hardware variants may be fragile. Debug assumption blocks use `BUG_ON()` for reference mismatches.

Test signals: probe on CB710/CB720 hardware with each slot mask combination, platform child device binding, shared IRQ delivery to MMC/MS/SM handlers, suspend/resume IRQ re-registration, remove/unbind cleanup, and debug-assumption builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cb710/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cb710/debug.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cb710/debug.c

Purpose: provides optional CB710 register dump support for developer debugging.

Important APIs, types, and functions: `cb710_dump_regs(struct cb710_chip *chip, unsigned select)` is exported when this file is built. Macro templates generate 8-bit, 16-bit, and 32-bit register readers and dumpers. The `allow[]` bitmap controls which register offsets are safe to read; `prefix[]` labels 16-byte blocks as MMC, MS, or SM related.

Control flow: `cb710_dump_regs()` normalizes the requested block/access masks, then performs selected reads at requested widths and emits formatted `dev_dbg()` lines. The generated readers skip disallowed offsets and the dumpers print `x` placeholders for skipped registers.

State and persistence: no persistent state is kept; each dump snapshots MMIO registers into stack arrays before logging.

Dependencies and integration points: depends on `linux/cb710.h`, MMIO accessors, and `CONFIG_CB710_DEBUG` object inclusion. It is intended for use by CB710 child/core debug paths.

Risks: reading device registers can have side effects, so the `allow[]` mask is a safety boundary. Incorrect select masks could produce excessive logs. Formatting uses fixed-size stack buffers sized for current dump layouts.

Test signals: debug build should link `cb710_dump_regs()`. Runtime signal is readable, aligned register dumps under `dynamic_debug`/`dev_dbg()` without touching disallowed registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cb710/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cb710/sgbuf2.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cb710/sgbuf2.c

Purpose: exports scatterlist mapping iterator helpers that read and write 32-bit words across possibly unaligned or segment-split SG buffers for CB710 child drivers.

Important APIs, types, and functions: `cb710_sg_dwiter_read_next_block()` returns the next 32-bit word, zero-padding past the end of the buffer. `cb710_sg_dwiter_write_next_block()` writes the next 32-bit word, silently discarding bytes beyond the end. Internal helpers advance `struct sg_mapping_iter`, handle end detection, and choose fast direct access versus slow byte-copy for unaligned or cross-segment words.

Control flow: read/write first tries `sg_dwiter_get_next_block()`; if at least four aligned bytes are available in the current segment, it directly dereferences the word and advances. Otherwise, slow paths copy byte fragments across SG segments using `sg_miter_next()`, update `miter->consumed`, and pad/discard incomplete tails.

State and persistence: state is entirely in the caller-provided `sg_mapping_iter`, especially `addr`, `length`, and `consumed`. No driver-global state exists.

Dependencies and integration points: depends on Linux scatterlist mapping iterators and `linux/cb710.h` exported prototypes. Child drivers can use these helpers to stream FIFO words to/from card-reader hardware while respecting SG layout.

Risks: `sg_dwiter_write_slow()` copies to `miter->addr` rather than `miter->addr + miter->consumed`, which is notable and should be checked against intended kernel version behavior. Direct word dereferences depend on CPU unaligned access support and pointer alignment. Callers must start/stop the SG mapping iterator correctly and obey its context constraints.

Test signals: unit-style SG tests with aligned, unaligned, one-byte, split-at-every-byte, and partial-tail buffers; data round-trip through CB710 child transfers; KASAN/KMSAN for SG boundary issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cb710/sgbuf2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cs5535-mfgpt.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cs5535-mfgpt.c

Purpose: implements a platform driver and exported allocator/control API for AMD Geode CS5535/CS5536 multi-function general purpose timers (MFGPTs).

Important APIs, types, and functions: exported functions are `cs5535_mfgpt_toggle_event()`, `cs5535_mfgpt_set_irq()`, `cs5535_mfgpt_alloc_timer()`, `cs5535_mfgpt_free_timer()`, `cs5535_mfgpt_read()`, and `cs5535_mfgpt_write()`. `struct cs5535_mfgpt_timer` describes an allocated timer and `cs5535_mfgpt_chip` stores global device state. Module parameter `mfgptfix` optionally resets timers during init.

Control flow: platform probe validates `mfgptfix`, reserves the I/O region, initializes global chip state, scans available timers, and marks the chip initialized. `scan_timers()` optionally performs undocumented full reset or soft reset, then reads each timer setup register and marks free timers in a bitmap. Allocation selects a requested or first available timer from the bitmap under a spinlock, allocates a handle, and clears the availability bit. Freeing only returns a timer to the bitmap if its setup bit was never programmed. Event toggling manipulates MSRs for reset, NMI, or IRQ routing. IRQ setup checks shared-twin/VSA constraints, existing/default IRQ selection, LPC routing, and then enables the IRQ event.

State and persistence: the driver has one static global chip with availability bitmap, base I/O address, platform device pointer, lock, and initialized flag. Hardware timer setup, comparator events, IRQ routing, and MSR state persist in chipset registers beyond the lifetime of an allocated handle unless explicitly reset.

Dependencies and integration points: depends on platform devices named `cs5535-mfgpt`, Geode `linux/cs5535.h`, x86 MSR access, inw/outw port I/O, and client drivers that allocate timers for watchdog/clock/event functions.

Risks: the reset modes are intentionally broad and can disturb firmware-owned timers. `soft_reset()` constructs a temporary timer without initializing `.chip`, so calls through `cs5535_mfgpt_toggle_event()` only work because that function uses `timer->nr` and MSRs, not `chip`. IRQ routing can conflict with VSA or other Linux users if forced. Freeing does not reset programmed hardware, so resource reuse is conservative and may surprise callers.

Test signals: probe with valid and invalid `mfgptfix` values, timer allocation/free for requested and automatic timers, IRQ routing success/failure cases, read/write register access, and client-driver behavior on systems with firmware-reserved timers. Hardware/virtual Geode coverage is required for meaningful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cs5535-mfgpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ds1682.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ds1682.c

Purpose: implements an I2C driver for the Dallas/Maxim DS1682 elapsed time recorder, exposing elapsed time, alarm time, event count, and 10 bytes of EEPROM through sysfs and NVMEM.

Important APIs, types, and functions: sysfs handlers `ds1682_show()` and `ds1682_store()` back `elapsed_time`, `alarm_time`, and `event_count`. Binary sysfs handlers `ds1682_eeprom_read()` and `ds1682_eeprom_write()` expose raw EEPROM. NVMEM callbacks `ds1682_nvmem_read()` and `ds1682_nvmem_write()` integrate the EEPROM bytes with NVMEM. `ds1682_probe()` and `ds1682_remove()` manage registration.

Control flow: probe checks SMBus I2C block functionality, registers an NVMEM provider for the 10-byte EEPROM, creates the attribute group, then creates the binary EEPROM file. Reads of the elapsed-time register retry up to five times to avoid returning a torn value when the 1/4-second counter ticks mid-read. 32-bit time values are exposed in milliseconds by multiplying register counts by 250; writes divide input milliseconds by 250 before storing little-endian values.

State and persistence: persistent state is on the DS1682 chip: elapsed counter, alarm threshold, event counter, and EEPROM bytes. The driver stores no private per-device state beyond the I2C client.

Dependencies and integration points: depends on I2C SMBus block access, hwmon sysfs attribute helpers, binary sysfs files, and NVMEM provider support. Matches I2C ID `ds1682` and OF compatible `dallas,ds1682`.

Risks: the driver exposes writable counter and EEPROM registers; write-protected chips will fail writes but write protection cannot be disabled. Time conversion truncates milliseconds to 250 ms units. Binary sysfs reads/writes trust sysfs to bound `off/count` to the attribute size. No explicit locking protects concurrent sysfs/NVMEM writes.

Test signals: I2C probe with and without block functionality, sysfs read/write of elapsed/alarm/event fields, elapsed read stability across ticks, NVMEM read/write of 10 bytes, binary sysfs bounds, write-protected device behavior, and OF/I2C ID matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ds1682.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/dummy-irq.c -->
# sources/distributed-fs/ceph-client/drivers/misc/dummy-irq.c

Purpose: provides a diagnostic module that registers a shared dummy interrupt handler for a user-specified IRQ to help debug spurious interrupts on disabled vectors.

Important APIs, types, and functions: module parameter `irq` is declared with `module_param_hw()`. `dummy_irq_init()` validates and registers the IRQ; `dummy_irq_exit()` frees it. `dummy_interrupt()` logs the first interrupt occurrence and always returns `IRQ_NONE`.

Control flow: module load fails unless `irq=N` is provided and `request_irq()` succeeds. Once loaded, the shared handler observes interrupts but deliberately does not claim them. Module unload frees the same dev_id pointer used at registration.

State and persistence: the only driver state is global `irq` and a static `count` inside the handler that suppresses repeated informational logs. No persistent state.

Dependencies and integration points: depends on Linux interrupt APIs and module parameter infrastructure. It is standalone and does not bind to hardware devices.

Risks: registering on the wrong IRQ can add overhead to a real interrupt line. Returning `IRQ_NONE` is intentional but can still contribute to spurious IRQ accounting. The handler's static `count` is not atomic, but it only gates a best-effort one-time log.

Test signals: load without `irq` should fail, load with an invalid/busy IRQ should fail, load with a shared IRQ should register, first interrupt should log once, and unload should free the handler cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/dummy-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/dw-xdata-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/misc/dw-xdata-pcie.c

Purpose: implements a PCI driver for the Synopsys DesignWare xData PCIe traffic-generation/performance block. It registers a misc device with sysfs attributes to start/stop read or write traffic and report measured throughput.

Important APIs, types, and functions: `struct dw_xdata_regs` maps the device register layout; `struct dw_xdata` stores BAR mapping, max read/write lengths, mutex, PCI device, and miscdevice. `dw_xdata_start()` programs continuous traffic, `dw_xdata_stop()` clears repeat mode, `dw_xdata_perf()` measures counters over 100 ms, and sysfs `read`/`write` attributes both start/stop traffic on store and return MB/s on show. `dw_xdata_pcie_probe()` and `dw_xdata_pcie_remove()` manage PCI/misc lifecycle.

Control flow: probe enables the PCI device with managed helpers, maps BAR 0, sets bus master, allocates state, computes transfer lengths from PCIe MPS and read request size, allocates an IDA id, creates a named miscdevice, initializes RAM address/port and target endpoint memory address, stores drvdata, and registers the misc device. Writing `1` to `read` or `write` stops existing traffic, clears status, enables continuous burst, sets pattern and control direction/length bits, waits briefly, and checks `STATUS_DONE`. Writing `0` stops traffic. Reading sysfs counters disables perf capture, snapshots counters and jiffies, enables perf, waits 100 ms, snapshots again, computes MB/s, and re-enables perf.

State and persistence: runtime state includes the mapped register BAR, max transfer lengths, misc name/id, and mutex. Hardware state persists in xData registers such as target address, burst count, control, status, RAM registers, performance control, and read/write counters until stopped or removed.

Dependencies and integration points: depends on PCI core, DesignWare/Synopsys PCI IDs, miscdevice, sysfs attribute groups, IDA, mutexes, and PCIe helper APIs `pcie_get_mps()` and `pcie_get_readrq()`. User space controls it through `/sys/class/misc/dw-xdata-pcie.N/{read,write}`.

Risks: sysfs show functions sleep for 100 ms under the device mutex. `dw_xdata_pcie_remove()` parses the ID back from `misc_dev.name`; if parsing fails it returns before stopping/deregistering, which would be hazardous if the name were ever malformed. Traffic targets BAR physical address plus a fixed endpoint memory offset and assumes the hardware design maps that memory. There is no interrupt/error recovery path beyond status polling.

Test signals: PCI probe/remove for the Synopsys EDDA ID, miscdevice creation, sysfs start/stop for read and write, nonzero throughput reporting, concurrent sysfs access serialization, remove while traffic is active, and validation of target address/length programming on actual xData hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/dw-xdata-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/eeprom/Kconfig

Purpose: declares Linux Kconfig options for EEPROM and EEPROM-like memory drivers under `drivers/misc/eeprom`.

Important APIs, types, and functions: relevant options for this subset are `EEPROM_AT24`, `EEPROM_AT25`, `EEPROM_93CX6`, `EEPROM_DIGSY_MTC_CFG`, and `EEPROM_EE1004`. The menu also declares options for MAX6875, 93XX46, IDT 89HPESX, and M24LR drivers that are built by the same directory but not part of this source subset. Options select dependencies such as NVMEM, NVMEM_SYSFS, REGMAP, REGMAP_I2C, and SPI_MEM as needed.

Control flow: Kconfig selections determine which EEPROM drivers are compiled. AT24 depends on I2C and SYSFS and selects NVMEM/regmap; AT25 depends on SPI and SYSFS and selects SPI_MEM/NVMEM; EE1004 depends on I2C and SYSFS; DIGSY_MTC_CFG is a board-specific bool depending on GPIO_MPC5200 and SPI_GPIO.

State and persistence: no runtime state; this file controls compile-time availability and dependency selection for drivers that expose persistent EEPROM/FRAM/SPD contents at runtime.

Dependencies and integration points: integrated with the top-level kernel configuration. Help text documents user-visible module names and cautions, especially AT24 misconfiguration risks and SPD handling.

Risks: users can select generic EEPROM geometry that does not match hardware, which can lead to data loss in writable devices. Board-specific DIGSY_MTC_CFG exists as a legacy static device-registration path and should eventually be replaced by device tree.

Test signals: configuration build matrix for each option as built-in/module/disabled where applicable, dependency resolution for I2C/SPI/NVMEM/regmap, and module names matching Makefile output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/eeprom/Makefile

Purpose: maps EEPROM Kconfig options to object files in `drivers/misc/eeprom`.

Important APIs, types, and functions: object mappings include `at24.o`, `at25.o`, `max6875.o`, `eeprom_93cx6.o`, `eeprom_93xx46.o`, `digsy_mtc_eeprom.o`, `idt_89hpesx.o`, `ee1004.o`, and `m24lr.o`.

Control flow: no runtime control flow; Kbuild compiles objects according to selected config symbols.

State and persistence: no runtime state; controls build products only.

Dependencies and integration points: paired with the EEPROM Kconfig menu and source files in the same directory. External drivers may link against exported symbols from `eeprom_93cx6.o`.

Risks: Kconfig/Makefile drift would make options ineffective or compile unexpected code. Because some objects are helper libraries and some are bus drivers, link coverage matters for both built-in and module combinations.

Test signals: `make drivers/misc/eeprom/` with relevant config permutations, especially `EEPROM_93CX6=m/y` for exported symbols and AT24/AT25/EE1004 module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/at24.c -->
# sources/distributed-fs/ceph-client/drivers/misc/eeprom/at24.c

Purpose: implements the generic I2C EEPROM/RAM/ROM/FRAM-style AT24 driver with NVMEM integration, regmap-based I2C access, multi-address chip handling, runtime PM, regulators, and many device-ID/OF/ACPI geometries.

Important APIs, types, and functions: `struct at24_data` stores lock, geometry, flags, NVMEM, regulator, read-post hook, bank shift, and one regmap per I2C address. `struct at24_chip_data` provides static geometry and quirks. NVMEM callbacks are `at24_read()` and `at24_write()`. Low-level helpers include `at24_translate_offset()`, `at24_adjust_read_count()`, `at24_regmap_read()`, `at24_adjust_write_count()`, `at24_regmap_write()`, dummy-client creation, offset adjustment for serial/MAC parts, SPD temp sensor probing, probe/remove, and runtime PM callbacks.

Control flow: module init validates and rounds `at24_io_limit` to a power of two before registering the I2C driver. Probe reads matched chip data plus firmware properties (`pagesize`, `read-only`, `no-read-rollover`, `address-width`, `size`, `num-addresses`, `label`), builds a regmap, allocates `at24_data`, gets the `vcc` regulator, creates dummy I2C clients for additional addresses, configures NVMEM, powers the device when ACPI says D0, performs an optional one-byte test read, registers NVMEM, and probes `jc42` for SPD DIMMs. Reads/writes resume the device, lock `at24->lock`, split operations by IO limit/address boundary/page boundary, retry regmap operations until `at24_write_timeout`, then runtime-put the device.

State and persistence: persistent data is EEPROM/FRAM contents. Runtime state is geometry (`byte_len`, `page_size`, address width, number of addresses), write limit, offset adjustment for special factory areas, regulator/runtime-PM state, and NVMEM registration. `at24_read_post_vaio()` masks sensitive Sony VAIO regions for non-admin readers without changing EEPROM contents.

Dependencies and integration points: depends on I2C, regmap, NVMEM provider/sysfs compatibility, runtime PM, regulators, firmware properties, OF/ACPI/I2C matching, and optional `jc42` thermal sensor instantiation for SPD. User space primarily sees NVMEM/sysfs-compatible EEPROM access.

Risks: wrong geometry properties can corrupt EEPROM data, especially page size, address width, and multi-address layout. The mutex protects only Linux-local access, not other I2C masters. SMBus-limited adapters reduce write size. Runtime PM/regulator errors can surface as read/write failures. Large reads/writes are chunked and may partially complete internally before a later timeout error.

Test signals: bind each major geometry class (8-bit, 16-bit, multi-address, no-read-rollover, serial, MAC, SPD, VAIO), NVMEM read/write bounds, page-boundary writes, retry/timeout behavior when device NACKs during write cycle, regulator suspend/resume, runtime PM autosuspend, dummy-address reservation, and SPD thermal-sensor detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/at24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/at25.c -->
# sources/distributed-fs/ceph-client/drivers/misc/eeprom/at25.c

Purpose: implements a generic SPI-mem driver for AT25-like SPI EEPROMs and Cypress FM25 FRAMs, exposing memory through NVMEM and optional serial/Jedec ID sysfs attributes.

Important APIs, types, and functions: `struct at25_data` stores `spi_eeprom` geometry, `struct spi_mem`, lock, address length, NVMEM config/device, serial number, and JEDEC ID. NVMEM callbacks are `at25_ee_read()` and `at25_ee_write()`. Helpers include `at25_instr()` for 9-bit address-in-instruction parts, `fm25_aux_read()`, `at25_wait_ready()`, firmware/FRAM geometry discovery, and `at25_probe()`. Sysfs read-only attributes are `sernum` and `jedec_id`.

Control flow: probe allocates state, pings the chip with `RDSR` via `at25_wait_ready()`, initializes the lock and drvdata, determines EEPROM versus FRAM from firmware compatible, loads platform-data or firmware-discovered geometry, validates 1/2/3-byte address mode, builds NVMEM config, registers NVMEM, and logs geometry. Reads allocate a bounce buffer, clamp to device size, split by PAGE_SIZE and controller-adjusted SPI-mem op size, execute `READ` ops under the lock, and copy data out. Writes validate bounds, lock for the entire write, issue WREN, split at page/io/controller boundaries, execute `WRITE`, then poll ready until completion or timeout. FRAM discovery can read RDID and serial-number auxiliary commands and infer capacity.

State and persistence: persistent data is EEPROM/FRAM contents plus optional chip serial/ID. Runtime state stores geometry, address mode flags, cached serial/ID bytes, NVMEM registration, and a mutex. EEPROM status-register write-protection bits are observed indirectly only through failed writes; the driver does not manage write-protect configuration.

Dependencies and integration points: depends on SPI core, SPI_MEM, firmware properties or platform data, NVMEM provider, sysfs attribute groups, and `linux/spi/eeprom.h` flags. Matches `atmel,at25`, `cypress,fm25`, and SPI IDs `at25`/`fm25`.

Risks: firmware must provide correct `size`, `pagesize`, and address width for EEPROMs; bad data can truncate or misaddress writes. Writes may partially complete before an error. The code has a diagnostic typo "Read Status Redister" but behavior is unaffected. For FRAM, unsupported JEDEC formats fail probe. `read-only` is enforced through NVMEM config but hardware may still allow writes from other paths.

Test signals: SPI-mem read/write across page and controller-size boundaries, read-only NVMEM behavior, WREN/status timeout handling, 8/9/16/24-bit addressing, platform-data and firmware-property probe, Cypress FRAM ID/serial detection including reversed ID format, and sysfs `sernum`/`jedec_id` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/at25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/digsy_mtc_eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/misc/eeprom/digsy_mtc_eeprom.c

Purpose: statically registers a bit-banged SPI bus and 93xx46 EEPROM device for display-configuration EEPROMs on the DigsyMTC board.

Important APIs, types, and functions: defines GPIO numbers for SPI clock, chip select, data in/out, and output enable; a `spi_gpio_platform_data`; a platform device named `spi_gpio`; a GPIO descriptor lookup table; one `spi_board_info` entry for `eeprom-93xx46`; and init function `digsy_mtc_eeprom_devices_init()`.

Control flow: at `device_initcall`, the driver adds the GPIO lookup table, registers SPI board info, attaches a software node with `"data-size" = 8` to the `spi_gpio` platform device, and registers that platform device. On software-node add failure it returns immediately; on platform-device registration failure it removes the software node.

State and persistence: no runtime private state beyond globally defined platform data/device/lookup structures. Persistent EEPROM contents are handled by the downstream `eeprom-93xx46` driver, not this file.

Dependencies and integration points: depends on `GPIO_MPC5200`, `SPI_GPIO`, GPIO machine lookup tables, SPI board-info registration, software nodes, and the `eeprom-93xx46` SPI driver. It is explicitly a board-specific legacy registration shim.

Risks: the file comment states this should be replaced by device-tree-defined SPI/EEPROM devices. Hard-coded GPIO numbers and bus number can collide with platform changes. There is no cleanup path for the device_initcall registration, which is typical for board setup but not hotplug-friendly.

Test signals: DigsyMTC boot should show `spi_gpio.1` registration, correct GPIO lookup resolution, creation of the `eeprom-93xx46` SPI device, and usable EEPROM sysfs/NVMEM access through the downstream driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/digsy_mtc_eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/ee1004.c -->
# sources/distributed-fs/ceph-client/drivers/misc/eeprom/ee1004.c

Purpose: implements a read-only I2C/NVMEM driver for JEDEC EE1004-compliant DDR4 SPD EEPROMs, which expose two 256-byte pages selected through separate page-select I2C addresses.

Important APIs, types, and functions: global `ee1004_bus_lock` serializes page selection and reads. `struct ee1004_bus_data` tracks one I2C adapter, two dummy page-select clients, device count, and current page. Key helpers are `ee1004_get_bus_data()`, `ee1004_get_current_page()`, `ee1004_set_current_page()`, `ee1004_eeprom_read()`, `ee1004_read()`, temperature-sensor probing, bus-data init/cleanup, and `ee1004_probe()`.

Control flow: probe checks SMBus byte plus block or byte-data read functionality, verifies the SPD address responds, locks the global bus mutex, initializes or reuses bus data and page-select dummy clients at 0x36/0x37, detects the current page, probes for a `jc42` temperature sensor when SPD data indicates or implies one, unlocks, registers cleanup action, registers a read-only NVMEM device, and logs geometry. Reads validate bounds, lock the global bus mutex from page selection through transfer, repeatedly call `ee1004_eeprom_read()` in page- and SMBus-block-limited chunks, and unlock on completion.

State and persistence: persistent data is the 512-byte SPD EEPROM. Driver state is global per-adapter bus data for up to eight busses, page-select dummy clients, reference counts, and cached current page. No writes are exposed.

Dependencies and integration points: depends on I2C SMBus helpers, NVMEM provider/sysfs compatibility, and optional `jc42` temperature sensor instantiation. It matches I2C ID `ee1004`.

Risks: only eight I2C adapters are supported by the static bus-data array. Page selection is global per bus and must remain locked until each read chunk completes to avoid cross-DIMM page races. Some modules NACK page select despite changing pages; the driver handles this by probing current page. SPD revision fallback probing can instantiate thermal sensors if an address responds.

Test signals: multiple DDR4 SPD devices on the same adapter, concurrent reads from different DIMM slots, page-boundary reads across offsets 255/256, adapters with block-read versus byte-data emulation, thermal-sensor discovery, cleanup when the last device on a bus is removed, and NVMEM read-only permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/ee1004.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/eeprom_93cx6.c -->
# sources/distributed-fs/ceph-client/drivers/misc/eeprom/eeprom_93cx6.c

Purpose: provides exported bit-banged access routines for 93cx6 Microwire EEPROMs, especially 93c46 and 93c66, using callbacks supplied in `struct eeprom_93cx6`.

Important APIs, types, and functions: exported functions are `eeprom_93cx6_read()`, `eeprom_93cx6_multiread()`, `eeprom_93cx6_readb()`, `eeprom_93cx6_multireadb()`, `eeprom_93cx6_wren()`, and `eeprom_93cx6_write()`. Internal helpers pulse clock high/low, assert/deassert chip select, write bits, and read bits. The implementation uses callback fields `register_read()` and `register_write()` plus bit fields such as `reg_data_in`, `reg_data_out`, `reg_data_clock`, `reg_chip_select`, and `drive_data`.

Control flow: read operations start the EEPROM transaction, send a READ opcode plus word/byte address based on EEPROM width, optionally perform an extra read cycle quirk, read 16 or 8 bits, and clean up chip select. Multi-read functions loop single reads and convert word reads to little-endian for callers. `eeprom_93cx6_wren()` sends EWEN or EWDS. Write sends WRITE opcode/address, sends 16 data bits, releases data drive, waits for data-out to go high as ready/busy with up to 100 sleep-loop iterations, then cleans up.

State and persistence: persistent state is EEPROM contents and write-enable state. Runtime state is entirely in the caller-provided `struct eeprom_93cx6`, whose register image is repeatedly read/modified/written by callbacks. The helper does not allocate per-device state or provide locking.

Dependencies and integration points: depends on `linux/eeprom_93cx6.h` opcode/width/quirk definitions and hardware-specific drivers that provide register callbacks. Exported symbols are used as a small library by network/wireless or other device drivers with embedded Microwire EEPROMs.

Risks: callers must serialize access and correctly implement register callbacks; the helper itself has no locking. Timing is delay-based and assumes 450 ns pulses plus millisecond write polling are suitable. Address width and byte/word addressing must be configured correctly or reads/writes target the wrong cells. Write-enable is a separate operation; accidental enable plus writes can alter calibration data.

Test signals: callback-level tests on simulated registers, hardware reads for 93c46/93c66 widths, byte and word multi-read ordering, extra-read-cycle quirk behavior, write-enable/disable and write polling, timeout logging when ready never asserts, and endian checks for `multiread()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/eeprom_93cx6.c -->
