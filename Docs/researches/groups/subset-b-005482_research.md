# subset-b-005482 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/usb.c

## Purpose
`usb.c` is the host-side USB core library and module lifecycle file. It is not a hardware driver; it provides exported helpers for endpoint discovery, interface/configuration lookup, USB device/interface references, reset locking, DMA-safe buffer allocation, descriptor parsing, periodic endpoint sizing, USB bus notifications, debugfs exposure, and usbcore initialization/cleanup.

## Important APIs, types, and functions
Important exported APIs include `usb_disabled`, `usb_find_common_endpoints`, `usb_find_common_endpoints_reverse`, `usb_check_bulk_endpoints`, `usb_check_int_endpoints`, `usb_find_alt_setting`, `usb_ifnum_to_if`, `usb_altnum_to_altsetting`, `usb_find_interface`, `usb_for_each_dev`, `usb_alloc_dev`, `usb_get_dev`, `usb_put_dev`, `usb_get_intf`, `usb_put_intf`, `usb_intf_get_dma_device`, `usb_lock_device_for_reset`, `usb_get_current_frame_number`, `__usb_get_extra_descriptor`, coherent/noncoherent DMA allocation helpers, and periodic payload helpers. Internal objects include `usb_device_type`, `usb_bus_nb`, and small callback argument structs used with the driver core bus walkers.

## Control flow
Endpoint helpers clear caller-provided result pointers, scan the active alternate setting, and return success only when every requested endpoint class/direction has been found. Device/interface lookup helpers walk the current configuration or global USB bus. `usb_alloc_dev` allocates and initializes a `struct usb_device`, takes an HCD reference, sets device core type/groups/node/name/topology strings, initializes ep0 and runtime PM fields, derives OF node and route information, applies authorization policy, and returns an attached but not enumerated device. Module initialization gates on `nousb`, initializes pool/debugfs/ACPI/bus notifier/major class/usbfs/devio/hub/generic driver in order, and unwinds in reverse on failure. Exit releases quirks and unregisters generic driver, major, usbfs, devio, hub, class, notifier, bus, ACPI, debugfs, and the bus IDR.

## State and persistence behavior
Persistent runtime state is kernel in-memory state: module parameters `nousb` and `autosuspend`, device references, sysfs/debugfs nodes, PM autosuspend delay, stable `devpath`/route strings, authorization flags, endpoint state, and HCD references. The file does not persist data to disk. It relies on driver-core reference counting for lifetime and on `usb_release_dev` to destroy configurations, BOS descriptors, OF nodes, HCD references, strings, and the device allocation.

## Dependencies and integration points
This file integrates with `hub.h`, `trace.h`, USB HCD APIs, usbfs, sysfs attribute creation/removal, ACPI, OF, debugfs, DMA mapping, runtime/system PM, bus/class registration, and the generic USB device driver. It is the utility surface used by class and interface drivers to avoid open-coding descriptor scans, refcount operations, and DMA buffer management.

## Risks
The main risks are lifetime/refcount mistakes around `bus_find_device` and `put_device`, reset-lock deadlocks if callers ignore `usb_lock_device_for_reset` semantics, descriptor parsing rejecting malformed but present extra descriptors, endpoint matching using first/last semantics that may not match a quirky device, route truncation for deep paths, and init unwinding bugs because many subsystems are registered in sequence. DMA helper callers must pass matching size/address/table/direction values on free.

## Test signals
Useful signals are USB core boot with and without `nousb`, module init failure injection, device enumeration under hubs and root hubs, sysfs add/remove notification coverage, usbfs/debugfs `/sys/kernel/debug/usb/devices`, runtime/system suspend/resume, endpoint helper unit-style coverage with synthetic descriptors, malformed descriptor parsing tests, DMA API debug checks, and hotplug/disconnect stress tests watching for leaks or refcount warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/usb.h -->
# sources/distributed-fs/ceph-client/drivers/usb/core/usb.h

## Purpose
`usb.h` is the private header for `drivers/usb/core`. It declares cross-file USB core internals that are not part of the public USB driver API, including sysfs helpers, endpoint enable/disable helpers, authorization, descriptor/configuration routines, hub/devio/lpm/PM integration, bus/class/device type symbols, usbfs symbols, notification hooks, firmware location helpers, and ACPI glue.

## Important APIs, types, and functions
The header declares device and interface sysfs helpers, endpoint device creation/removal, `usb_enable_endpoint`, `usb_enable_interface`, endpoint/interface/device disable paths, interface cache release, authorization/deauthorization, quirk detection/release, ignored endpoint checks, descriptor/configuration APIs, generic driver probe/disconnect/suspend/resume hooks, hub workqueue and ownership helpers, hub/major/devio lifecycle functions, LPM helpers, PM suspend/resume/autosuspend functions, and ACPI registration/lookup functions. It defines `usb_get_max_power`, type predicates such as `is_usb_device`, and `usb_port_location_t`.

## Control flow
This file mainly shapes compile-time linkage. When `CONFIG_PM` is enabled, consumers call real suspend/resume/autosuspend/LPM functions; otherwise inline stubs return success or no-op. When `CONFIG_ACPI` is disabled, ACPI registration/unregistration become no-ops. Type predicates compare `struct device.type` to the USB core device/interface/endpoint/port type singletons, allowing bus walkers to filter mixed USB bus devices.

## State and persistence behavior
The header itself stores no state, but it exposes state-owning globals such as `usb_bus_type`, `usbmisc_class`, `usb_port_peer_mutex`, USB device types, `usb_generic_driver`, `usbfs_driver`, file operations, attribute group arrays, and `usbcore_name`. Its inline stubs intentionally preserve caller control flow when PM or ACPI is absent, which can hide feature differences behind successful no-ops.

## Dependencies and integration points
It depends on Linux PM and ACPI headers and public USB structures. It is included across USB core implementation files to share internal contracts among hub, config, driver, sysfs, devio, quirks, message, and ACPI code. External USB function or class drivers should generally use public headers instead.

## Risks
Because this is an internal contract header, prototype drift can create broad build failures. Stubbed PM/LPM/ACPI behavior can mask missing feature coverage if tests only check return values. The type predicates depend on device type pointer identity, so all USB device objects must be initialized with the correct singleton. `usb_get_max_power` encodes unit selection by speed and depends on current USB descriptor semantics.

## Test signals
Build matrices should cover PM on/off and ACPI on/off, host-only and gadget-related USB configurations, and sparse or CFI-style checks for prototype consistency. Runtime signals include correct sysfs and usbfs behavior, successful suspend/resume paths when PM is enabled, harmless no-op behavior when PM is disabled, and correct filtering in bus walkers using `is_usb_device` and related helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/Kconfig

## Purpose
This Kconfig file defines build-time selection for the Synopsys DesignWare USB2 DRD core driver. It controls whether the common DWC2 module is built, whether it supports host, peripheral, or dual-role operation, whether the PCI glue is available, and whether debug or SOF tracking diagnostics are compiled.

## Important APIs, types, and functions
The central symbol is `USB_DWC2`, a tristate depending on DMA, USB or USB_GADGET, and MMIO support, and selecting `USB_ROLE_SWITCH`. The mode choice selects one of `USB_DWC2_HOST`, `USB_DWC2_PERIPHERAL`, or `USB_DWC2_DUAL_ROLE` with defaults based on enabled USB host and gadget subsystems. Additional symbols are `USB_DWC2_PCI`, `USB_DWC2_DEBUG`, `USB_DWC2_VERBOSE`, `USB_DWC2_TRACK_MISSED_SOFS`, and `USB_DWC2_DEBUG_PERIODIC`.

## Control flow
The `if USB_DWC2` block presents a mutually exclusive mode choice. Host mode requires host USB availability and handles built-in/module constraints. Peripheral and dual-role mode require gadget support. PCI glue is independently selectable when USB PCI support is present. Debug and verbose options feed compiler flags in the Makefile, while missed SOF tracking enables extra host state in `core.h`.

## State and persistence behavior
No runtime state is stored here. The selected symbols persist in the kernel configuration and determine which objects, fields, stubs, debug prints, and host/gadget code paths exist in the compiled driver.

## Dependencies and integration points
This file integrates Kconfig with the DWC2 Makefile, USB host core, USB gadget core, USB role-switch framework, PCI bus glue, debugfs-dependent debug output, and host scheduler diagnostics. Its defaults are important because the source uses `IS_ENABLED(CONFIG_USB_DWC2_...)` to compile host/gadget structures and fallback stubs.

## Risks
Misconfigured dependencies can produce a DWC2 build with unavailable host or gadget APIs. The dual-role option requires both host and gadget support, so distribution configs must ensure all dependency combinations are covered. Verbose debug can flood logs. The missed-SOF option is explicitly experimental and may impose memory/logging overhead.

## Test signals
Build coverage should include built-in and module `USB_DWC2`, host-only, peripheral-only, dual-role, PCI enabled/disabled, debug/verbose, debugfs on/off, and missed-SOF tracking. Runtime smoke tests should confirm that expected modules (`dwc2`, platform glue, optional PCI glue) appear and that role-switch support is present for dual-role-capable systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/Makefile

## Purpose
The DWC2 Makefile maps Kconfig selections to object composition. It builds the common `dwc2.o` module from core, interrupt, platform, role-switch, and parameter code, conditionally adds host, gadget, and debugfs components, and builds optional PCI glue as `dwc2_pci.o`.

## Important APIs, types, and functions
The significant build variables are `ccflags-$(CONFIG_USB_DWC2_DEBUG) += -DDEBUG`, `ccflags-$(CONFIG_USB_DWC2_VERBOSE) += -DVERBOSE_DEBUG`, `obj-$(CONFIG_USB_DWC2) += dwc2.o`, and `dwc2-y := core.o core_intr.o platform.o drd.o params.o`. Host mode adds `hcd.o`, `hcd_intr.o`, `hcd_queue.o`, and `hcd_ddma.o`. Peripheral or dual-role mode adds `gadget.o`. Any debugfs-enabled build adds `debugfs.o`. `USB_DWC2_PCI` builds `pci.o` into `dwc2_pci.o`.

## Control flow
Build composition follows Kconfig: common files are always part of the DWC2 core, host files are linked only when host or dual-role mode is enabled, gadget files only when peripheral or dual-role mode is enabled, and debugfs only when the kernel has debugfs support. The PCI glue module is separate from the core module.

## State and persistence behavior
The Makefile stores no runtime state, but it determines which runtime state fields and functions from `core.h` are backed by implementations versus inline stubs. It also controls whether debug statements are compiled and whether debugfs registration symbols resolve to real code.

## Dependencies and integration points
It connects Kconfig to the Linux kbuild system and to the source-level `IS_ENABLED` boundaries in `core.h`, `debug.h`, and implementation files. The note documents the historical move of the old `s3c-hsotg` peripheral driver into `gadget.c` and clarifies module names for host, peripheral, dual-role, PCI, and platform cases.

## Risks
Conditional object omissions can create unresolved symbols if header stubs and implementation boundaries diverge. The `ifneq ($(filter y,...))` checks add host/gadget objects only for built-in boolean mode symbols, so module/built-in combinations must match Kconfig constraints. Enabling `VERBOSE_DEBUG` can increase logging volume substantially.

## Test signals
Build tests should inspect object membership for host-only, gadget-only, dual-role, debugfs-disabled, debugfs-enabled, and PCI-enabled configurations. Link tests should verify that `dwc2.o`, `dwc2_platform.ko`, and `dwc2_pci.ko` resolve all mode-specific symbols in their supported configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/core.c

## Purpose
`core.c` implements common DWC2 controller services used by host and gadget modes: global register backup/restore, partial power down and hibernation coordination, core reset, mode forcing, active clock gating, register dump helpers, FIFO flushing, controller liveness checks, global interrupt enable/disable, hardware capability checks, polling helpers, host clock selection, and PHY initialization.

## Important APIs, types, and functions
Key functions are `dwc2_backup_global_registers`, `dwc2_restore_global_registers`, `dwc2_enter_partial_power_down`, `dwc2_exit_partial_power_down`, `dwc2_hib_restore_common`, `dwc2_enter_hibernation`, `dwc2_exit_hibernation`, `dwc2_core_reset`, `dwc2_force_mode`, `dwc2_force_dr_mode`, `dwc2_enable_acg`, `dwc2_flush_tx_fifo`, `dwc2_flush_rx_fifo`, `dwc2_is_controller_alive`, `dwc2_enable_global_interrupts`, `dwc2_disable_global_interrupts`, `dwc2_op_mode`, `dwc2_hw_is_otg`, `dwc2_hw_is_host`, `dwc2_hw_is_device`, wait-bit helpers, `dwc2_init_fs_ls_pclk_sel`, and `dwc2_phy_init`.

## Control flow
Power-state wrappers dispatch to host or gadget implementations based on current mode or backed-up `GOTGCTL_CURMODE_HOST`. Hibernation restore sequences toggle `GPWRDN` power/reset/clamp/restore bits, restore essential global and mode-specific registers, and poll for `GINTSTS_RESTOREDONE`. Core reset writes `GRSTCTL_CSFTRST`, waits using revision-specific completion semantics, clears gadget FIFO mapping, waits for AHB idle, and optionally waits for host mode after IDDIG debounce. Mode forcing edits `GUSBCFG_FORCEHOSTMODE` or `GUSBCFG_FORCEDEVMODE` only when hardware and requested `dr_mode` allow it. PHY init selects FS or HS setup, programs `GUSBCFG`, may reset after PHY changes, configures UTMI/ULPI details, sets turnaround timing, ULPI FS/LS bits, and host VBUS override behavior.

## State and persistence behavior
The file writes hardware registers and in-memory backups in `hsotg->gr_backup`, plus mode and parameter-derived runtime behavior. Backup validity is tracked with `gr_backup.valid` and consumed on restore. It also modifies `fifo_map` through `dwc2_clear_fifo_map` when gadget-capable builds reset the core. No disk persistence is involved; correctness depends on the controller retaining or losing register state according to the selected low-power mode.

## Dependencies and integration points
It depends on `core.h`, `hcd.h`, register definitions in `hw.h`, Linux delay/io/USB/HCD APIs, and host/gadget functions declared conditionally in `core.h`. It is called by platform probe, host init, gadget init, suspend/resume, interrupt handlers, and role-switch code.

## Risks
Register restore sequences are revision- and mode-sensitive; a wrong delay or missing valid backup can leave the core wedged. Reset polling uses microsecond loops and returns `-EBUSY` on timeout, so callers must handle failed hardware reset. Mode forcing can conflict with fixed `dr_mode`, and debounce delays can create races around role changes. PHY initialization has many SoC-specific flags, so regressions can break only certain UTMI/ULPI/FS combinations.

## Test signals
Useful tests include host/gadget/dual-role enumeration after reset, suspend/resume under partial power down and hibernation, controller revision coverage before and after 4.20a reset semantics, UTMI 8/16-bit and ULPI DDR/SDR configurations, low/full/high speed devices, FIFO flush timeout logs, `GSNPSID == 0xffffffff` dead-controller detection, and role switching with IDDIG debounce enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/core.h -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/core.h

## Purpose
`core.h` is the shared internal contract for the DWC2 driver. It defines the central `struct dwc2_hsotg` state object, endpoint/request structures, parameter and hardware capability structures, register backup layouts, host scheduler constants, low-power and EP0 state enums, MMIO helpers, compile-time host/gadget stubs, and prototypes for common, host, gadget, DRD, debug, platform, and parameter code.

## Important APIs, types, and functions
Important types include `dwc2_hsotg_ep`, `dwc2_hsotg_req`, `dwc2_lx_state`, `dwc2_ep0_state`, `dwc2_core_params`, `dwc2_hw_params`, `dwc2_gregs_backup`, `dwc2_dregs_backup`, `dwc2_hregs_backup`, `dwc2_hsotg`, and `dwc2_halt_status`. Important helpers are `dwc2_readl`, `dwc2_writel`, `dwc2_readl_rep`, `dwc2_writel_rep`, `dwc2_is_iot`, `dwc2_is_fs_iot`, `dwc2_is_hs_iot`, `dwc2_is_host_mode`, `dwc2_is_device_mode`, and `call_gadget`. The header also declares the common reset/power/PHY/interrupt functions and conditional host/gadget APIs.

## Control flow
The header encodes compile-time control flow with `IS_ENABLED(CONFIG_USB_DWC2_HOST)`, `CONFIG_USB_DWC2_PERIPHERAL`, and dual-role checks. When a mode is not built, inline stubs make common code compile while returning harmless defaults. `call_gadget` releases and reacquires the controller spinlock around gadget driver callbacks to avoid callback execution under the DWC2 lock. MMIO helpers centralize optional byte swapping before every register access.

## State and persistence behavior
`struct dwc2_hsotg` is the persistent in-memory controller state across interrupts, role changes, suspend/resume, host scheduling, gadget endpoint operations, debugfs, and platform resources. It stores hardware-derived parameters, selected parameters, requested dual-role mode, role switch handle/default, low-level hardware flags, hibernation/partial-power-down flags, bus suspend state, PHY/clocks/resets/regulators, the global spinlock, OTG workqueue/timer, register backups, host schedule lists and bitmaps, DMA buffers and caches, gadget endpoint arrays, EP0 buffers, test mode, FIFO map, and connection/enabled flags.

## Dependencies and integration points
The header integrates with Linux PHY, regulator, USB gadget, USB OTG, USB role, debugfs, HCD, platform, ACPI/OF matching, and DWC2 register definitions in `hw.h`. It is included by nearly every DWC2 source file and is therefore the main boundary between platform setup, common core, host controller, gadget controller, DRD role switching, interrupts, and debugfs.

## Risks
Because `dwc2_hsotg` is large and mode-dependent, adding fields or changing conditionals can break ABI expectations inside the driver or create uninitialized state in one mode. The no-op stubs can conceal missing feature behavior in unsupported builds. MMIO byte swapping must be correct for every register access. Locking assumptions around `call_gadget` are subtle because callbacks run with the spinlock dropped and shared state may change.

## Test signals
Compile matrices across host-only, peripheral-only, dual-role, debugfs, and missed-SOF tracking are critical. Runtime signals include lockdep coverage around gadget callbacks, sparse or Coccinelle checks for MMIO accessor usage, suspend/resume verifying backup structures, host periodic scheduling tests, endpoint queue debugfs visibility, and role-switch tests ensuring fields present only in some configurations are not accessed in others.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/core_intr.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/core_intr.c

## Purpose
`core_intr.c` implements common DWC2 interrupt handling shared by host and device modes. It handles OTG events, connector ID changes, session requests, wakeup/resume, USB suspend, LPM L1 transitions, disconnects, port interrupts observed in device mode, and GPWRDN hibernation wake events.

## Important APIs, types, and functions
The exported entry point is `dwc2_handle_common_intr`. Important helpers include `dwc2_op_state_str`, `dwc2_handle_usb_port_intr`, `dwc2_handle_mode_mismatch_intr`, `dwc2_handle_otg_intr`, `dwc2_handle_conn_id_status_change_intr`, `dwc2_handle_session_req_intr`, `dwc2_wakeup_from_lpm_l1`, `dwc2_handle_wakeup_detected_intr`, `dwc2_handle_disconnect_intr`, `dwc2_handle_usb_suspend_intr`, `dwc2_handle_lpm_intr`, `dwc2_read_common_intr`, `dwc_handle_gpwrdn_disc_det`, and `dwc2_handle_gpwrdn_intr`.

## Control flow
The IRQ entry takes `hsotg->lock`, verifies the controller is alive, snapshots the current frame number from `DSTS` or `HFNUM`, masks common interrupts through `GINTSTS`, `GINTMSK`, and global interrupt enable, and dispatches handlers. Hibernated controllers bypass normal `GINTSTS` handling and use `GPWRDN` bits. OTG interrupts update `op_state`, clear HNP/SRP status, and may start or disconnect the host controller while temporarily dropping the spinlock. Connector ID changes clear and mask SOF, then queue OTG work. Session request wakes device low-power state or powers host port and connects HCD. Suspend paths choose partial power down, hibernation, or clock gating. LPM transitions place the gadget in L1 and call suspend callbacks; wake exits L1/L2 and calls resume as appropriate.

## State and persistence behavior
The file mutates `op_state`, `lx_state`, `frame_number`, `srp_success`, `hibernated`, `bus_suspended`, and power-down/clock-gating state. It writes many clear-on-write interrupt registers (`GINTSTS`, `GOTGINT`, `GPWRDN`) and relies on hardware interrupt masks. State is volatile in memory and hardware registers, with no disk persistence.

## Dependencies and integration points
It depends on `core.h`, `hcd.h`, host start/connect/disconnect helpers, gadget connect/disconnect/suspend/resume helpers, power management routines in `core.c`, USB PHY suspend handling, timers/workqueues, and low-level register definitions. It is the bridge from the platform IRQ registration to host and gadget mode-specific interrupt handlers.

## Risks
Interrupt handlers mix hardware register clears, state transitions, callbacks, timers, and lock dropping, so races are the main risk. Incorrect clearing can lose interrupts or cause storms, especially restore-done and GPWRDN wake cases. LPM L1 wake has timeout paths that reinitialize LPM but do not report a hard failure to the IRQ caller. HNP/mode transitions depend on revision-specific delays and can fail on marginal hardware. Calling host/gadget callbacks with state changes in progress requires strong lockdep and stress coverage.

## Test signals
Exercise cable attach/detach, ID pin changes, B-device SRP, HNP transitions, host and gadget suspend/resume, L1 LPM entry/exit with remote wakeup, partial power down, hibernation wake by disconnect/line-state/reset/status-change, dead-controller IRQ handling, and port enable-change in device mode. Logs for `Mode Mismatch`, timeout warnings, restore-done, GPWRDN reasons, and lockdep reports are key diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/core_intr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/debug.h -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/debug.h

## Purpose
`debug.h` is the small DWC2 debugfs interface header. It exposes debugfs lifecycle hooks to the rest of the driver while compiling them out cleanly when `CONFIG_DEBUG_FS` is disabled.

## Important APIs, types, and functions
When debugfs is enabled, it declares `dwc2_debugfs_init(struct dwc2_hsotg *hsotg)` and `dwc2_debugfs_exit(struct dwc2_hsotg *hsotg)`. When disabled, it provides inline stubs returning `0` or doing nothing. It includes `core.h` for the `dwc2_hsotg` declaration.

## Control flow
Callers can unconditionally call debugfs init/exit during probe/remove. The preprocessor selects real debugfs code or no-op stubs. This keeps platform and core code free of repeated `#ifdef CONFIG_DEBUG_FS` blocks.

## State and persistence behavior
The header stores no state. In enabled builds, state lives in `hsotg->debug_root` and `hsotg->regset` as created by `debugfs.c`; in disabled builds no debugfs state exists.

## Dependencies and integration points
It integrates the platform/core probe path with `debugfs.c`, `core.h`, and Linux `CONFIG_DEBUG_FS`. It also mirrors the DWC2 Makefile condition that only links `debugfs.o` when debugfs support is enabled.

## Risks
The main risk is signature drift between stubs and real functions, which would compile in one configuration and fail in another. Stub success can hide missing debugfs coverage in tests if only return values are checked.

## Test signals
Build DWC2 with `CONFIG_DEBUG_FS=y` and `CONFIG_DEBUG_FS=n`. Runtime debugfs-enabled tests should confirm per-controller debug directories appear and are removed; debugfs-disabled tests should confirm probe/remove still succeed without unresolved symbols or conditional logic failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/debugfs.c

## Purpose
`debugfs.c` creates DWC2 debugfs observability and limited gadget test-mode control. It exposes current parameters, hardware parameters, requested `dr_mode`, register dumps, gadget state, FIFO layout, endpoint queues, and test mode selection.

## Important APIs, types, and functions
The public functions are `dwc2_debugfs_init` and `dwc2_debugfs_exit`. Gadget-capable helpers include `testmode_write`, `testmode_show`, `state_show`, `fifo_show`, `ep_show`, and `dwc2_hsotg_create_debug`. Common debugfs helpers include the large `dwc2_regs` `debugfs_reg32` table, `params_show`, `hw_params_show`, and `dr_mode_show`. File operations are generated through `DEFINE_SHOW_ATTRIBUTE` or custom `testmode_fops`.

## Control flow
Initialization creates a directory named after the device under `usb_debug_root`, adds `params`, `hw_params`, `dr_mode`, optional gadget files, allocates a `debugfs_regset32`, and exposes `regdump`. Gadget state files read registers directly; endpoint files also take `hsotg->lock` while walking request queues. `testmode_write` copies a short command from userspace, maps known strings to USB test-mode constants, and calls `dwc2_hsotg_set_test_mode` under the spinlock. Exit removes the whole tree recursively and clears `debug_root`.

## State and persistence behavior
Debugfs entries are ephemeral runtime files. They expose live hardware and in-memory state but do not persist configuration. The only mutating interface is `testmode`, which can change controller test mode. The `regset` is devm-allocated and tied to the device lifetime, while debugfs dentries are manually removed.

## Dependencies and integration points
It depends on Linux debugfs, seq_file, uaccess, DWC2 core state/registers, USB test constants, gadget endpoint structures, and `usb_debug_root` from USB core. It integrates with `debug.h`, the DWC2 Makefile, and the platform probe/remove path.

## Risks
Reading registers through debugfs can trigger mode mismatch interrupts, acknowledged in the register table comment. Endpoint queue display must hold the lock to avoid list races, but register reads outside locks may still see transient state. `testmode_write` accepts prefix matches and maps unknown strings to `0`, so accidental writes can leave test mode rather than fail. Debugfs is not a stable ABI and must not be used as the only validation path.

## Test signals
With debugfs enabled, verify the DWC2 device directory, `params`, `hw_params`, `dr_mode`, `regdump`, and gadget files. Exercise reads during host and gadget operation, endpoint queue activity, and suspend/resume. Test test-mode writes for all supported names and unknown input. Watch dmesg for mode mismatch warnings, lockdep issues, and removal-time debugfs use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/drd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/drd.c

## Purpose
`drd.c` implements DWC2 dual-role integration with the Linux USB role-switch framework. It translates role-switch requests into GOTGCTL session-valid overrides and controller mode forcing, and preserves role behavior across suspend/resume.

## Important APIs, types, and functions
The public functions are `dwc2_drd_init`, `dwc2_drd_suspend`, `dwc2_drd_resume`, and `dwc2_drd_exit`. Internal helpers are `dwc2_ovr_init`, `dwc2_ovr_avalid`, `dwc2_ovr_bvalid`, and `dwc2_drd_role_sw_set`. The key macro `dwc2_ovr_gotgctl` enables B/A/VBUS valid overrides and bypasses the debounce filter.

## Control flow
`dwc2_drd_init` only acts when firmware has `usb-role-switch`; it reads the default mode, registers a userspace-controllable role switch, stores it on `hsotg`, then initializes override bits. Role changes reject requests incompatible with fixed `dr_mode`, reject dropping to none while gadget test mode is active, temporarily enable the clock if low-level hardware is off, take the spinlock, map `USB_ROLE_NONE` to a configured default if any, exit gadget clock gating if needed, set A-session or B-session validity, connect/disconnect gadget soft state when appropriate, release the lock, force host/device mode for OTG if the session actually changed, and disable the temporary clock. Suspend masks connector-ID changes for role-switch-managed controllers; resume restores the last role/default, forces mode, and unmasks connector-ID changes. Exit unregisters the role switch.

## State and persistence behavior
Runtime state lives in `hsotg->role_sw`, `role_sw_default_mode`, `dr_mode`, `ll_hw_enabled`, `test_mode`, `lx_state`, `bus_suspended`, and GOTGCTL/GUSBCFG hardware bits. The last role is retrieved from the role-switch framework during resume; no disk persistence exists.

## Dependencies and integration points
It integrates DWC2 with firmware properties, fwnode/device property APIs, USB role-switch, platform clock control, the common DWC2 lock and MMIO helpers, gadget connect/disconnect helpers, clock-gating exit helpers, and `dwc2_force_mode`. It is always compiled into the core DWC2 object, but most useful behavior depends on role-switch firmware data and dual-role-capable configuration.

## Risks
Role switching touches clocks, spinlocks, register overrides, gadget connection state, and forced mode, so ordering is sensitive. Returning success for `-EALREADY` session states is intentional but can hide no-op changes. Temporary clock enable must be balanced on all paths. Forcing mode after releasing the lock can race with cable/interrupt changes. Test mode blocks role-none only in gadget-capable builds.

## Test signals
Test firmware with and without `usb-role-switch`, default host/peripheral/none modes, userspace role changes among host/device/none, fixed host/peripheral `dr_mode` rejection, boot with cable already plugged while clocks are off, suspend/resume preserving role, connector-ID interrupt masking/unmasking, gadget test mode blocking role-none, and repeated role toggling under lockdep and clock framework debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/drd.c -->
