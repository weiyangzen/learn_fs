# subset-b-003810 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-core.c -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-core.c

## Purpose
`i2c-hid-core.c` implements the transport-independent HID-over-I2C protocol core. It owns descriptor fetch and validation, command formatting, interrupt-driven input reads, HID report get/set/send paths, reset sequencing, runtime/system power transitions, and registration of the HID low-level driver. Thin ACPI/OF/vendor wrappers provide power callbacks and the HID descriptor address; this file turns those callbacks plus an `i2c_client` into a normal `hid_device`.

## Important APIs, Types, and Functions
The persistent `struct i2c_hid` stores the I2C client, HID device, parsed HID descriptor, descriptor-register address, command/input/raw buffers, flags, quirks, waitqueue, command/reset mutexes, wrapper `i2chid_ops`, and optional DRM panel-follower state. `i2c_hid_desc` is the packed on-wire HID descriptor. Exported entry points are `i2c_hid_core_probe`, `i2c_hid_core_remove`, `i2c_hid_core_shutdown`, and `i2c_hid_core_pm`.

Protocol helpers include `i2c_hid_xfer`, `i2c_hid_read_register`, `i2c_hid_encode_command`, `i2c_hid_get_report`, `i2c_hid_set_or_send_report`, `i2c_hid_set_power`, `i2c_hid_start_hwreset`, and `i2c_hid_finish_hwreset`. HID core callbacks are supplied through `i2c_hid_ll_driver`: parse, start, stop, open, close, output report, and raw request. Input handling is driven by `i2c_hid_irq` and `i2c_hid_get_input`.

## Control Flow
Probe validates IRQ presence, allocates `struct i2c_hid`, initializes locks/work/waitqueue, allocates minimum buffers, allocates a HID device, and either powers/probes immediately or registers as a DRM panel follower. The direct probe path powers rails through `ops->power_up`, probes the I2C address, fetches the HID descriptor or DMI override, validates descriptor version/length, copies VID/PID into `hid_device`, merges DMI quirks, requests the IRQ, enables it, and calls `hid_add_device`.

HID parse resets the device with retry, then obtains the report descriptor through a DMI override or descriptor-register read before calling `hid_parse_report`. Start recomputes buffer size from parsed input/output/feature reports and reallocates with the IRQ disabled if needed. Interrupt handling reads `wMaxInputLength` bytes, treats zero-length input as reset completion, filters bogus `0xffff` IRQs, validates report length, optionally fixes known bad sizes, and forwards reports through `hid_safe_input_report` only while the HID device is opened.

Suspend calls `hid_driver_suspend`, optionally sends I2C-HID sleep, disables IRQ, and powers down when wakeup is not needed or forced. Resume powers up if required, enables IRQ, optionally delays Goodix wakeup, resets selected devices, otherwise sends power-on, then calls `hid_driver_reset_resume`. Panel followers perform probe/resume asynchronously from panel prepare/enable callbacks and suspend/power-down from panel unprepare/disable.

## State and Persistence Behavior
Persistent state is per I2C client and devm-owned except buffers and `hid_device`, which are explicitly freed/destroyed. `I2C_HID_STARTED` gates input delivery, and `I2C_HID_RESET_PENDING` synchronizes reset IRQ completion with `wait_event_timeout`. `cmd_lock` serializes shared command/raw buffers; `reset_lock` prevents feature report transfers from racing a reset and losing reset-complete interrupts. Device quirks persist after descriptor parsing and affect reset, suspend, wakeup, bogus IRQ, and report-size behavior. Panel-follower state uses workqueue memory barriers to decide whether a suspend callback should power down a successfully powered device.

## Dependencies and Integration Points
The file depends on Linux I2C transfers, IRQ threads, HID core, PM/wakeup, mutex/waitqueue APIs, DRM panel follower support, DMI override helpers from `i2c-hid-dmi-quirks.c`, and wrapper-provided `i2chid_ops` from OF/vendor drivers. It integrates with HID generic/multitouch/RMI consumers through `hid_add_device`, with wake IRQ policy through `device_may_wakeup`, and with board-specific power sequencing through optional callbacks.

## Risks and Edge Cases
The driver trusts descriptor register fields after basic size/version checks; bad register offsets or max lengths can cause failed transfers or buffer-pressure paths. `i2c_hid_set_or_send_report` checks `data_len > ihid->bufsize` before adding command/report-id overhead, so command buffer sizing must stay aligned with max report computation. Reset completion relies on devices sending an IRQ unless the no-IRQ quirk is set. Panel-follower paths require careful ordering because HID device registration may happen after core probe. Goodix, ELAN, QTEC, ALPS, Raydium, SIS, and other quirks show that small timing or power-sequence changes can regress specific hardware.

## Test Signals
Useful signals include successful descriptor/report parsing, HID device creation, input events after open, raw GET/SET feature report behavior, suspend/resume with and without wakeup, reset-on-resume devices, DMI descriptor overrides, panel-follower power ordering, no IRQ storms, no reset timeouts, no incomplete reports, and lockdep-clean operation across IRQ, reset, and raw request paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-dmi-quirks.c -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-dmi-quirks.c

## Purpose
`i2c-hid-dmi-quirks.c` supplies system-specific overrides for broken I2C-HID devices, primarily low-cost laptops whose touchpads do not expose usable HID/I2C-HID descriptors. It also supplies a DMI-scoped HID quirk for a platform where an ELAN touchscreen reports inverted axes.

## Important APIs, Types, and Functions
`struct i2c_hid_desc_override` groups an override I2C-HID descriptor, a HID report descriptor, its size, and the expected I2C device name. `sipodev_desc` is the large static descriptor bundle for SIPODEV/SP1064-compatible touchpads exposed as `SYNA3602:00`. `i2c_hid_dmi_desc_override_table` maps DMI vendor/product strings to that override. `i2c_hid_dmi_quirk_table` maps system identity to a `hid_device_id` carrying HID quirk bits. Exported helpers are `i2c_hid_get_dmi_i2c_hid_desc_override`, `i2c_hid_get_dmi_hid_report_desc_override`, and `i2c_hid_get_dmi_quirks`.

## Control Flow
The core calls the descriptor override helpers before doing normal I2C descriptor/report descriptor reads. Each helper first checks `dmi_first_match`; if no system match exists or the runtime I2C name differs from the override name, it returns `NULL`. On a match it returns the static descriptor pointer and, for report descriptors, writes the static size into the caller-provided size pointer. After normal descriptor parsing, the core calls `i2c_hid_get_dmi_quirks` with VID/PID; if the current system and HID identity match the DMI table, the returned quirk bits are ORed into `hid->initial_quirks`.

## State and Persistence Behavior
All override data is static and read-only after module load. No runtime state is stored. The returned descriptor pointers reference static arrays whose lifetime is the module lifetime, so the core must not free them. The core distinguishes override descriptors from allocated descriptors and only frees non-override report descriptors.

## Dependencies and Integration Points
The file depends on DMI matching, HID IDs/quirk bits, and the local `i2c-hid.h` declarations. It integrates only with `i2c-hid-core.c`, allowing the protocol core to stay generic while encoding platform-specific exceptions here.

## Risks and Edge Cases
DMI matches are exact and narrow; BIOS vendor/product spelling changes can miss needed overrides. Conversely, broad reuse of `sipodev_desc` across many systems assumes identical touchpad wiring and logical descriptor behavior. The descriptor override is selected by I2C name after DMI match, reducing false positives but depending on ACPI naming stability. Static descriptor contents are opaque byte arrays; malformed sizes or report contents would fail HID parsing or produce incorrect input semantics.

## Test Signals
Test by booting matched systems and confirming the core logs descriptor override use, HID parsing succeeds, multitouch and mouse reports work, and no I2C descriptor reads are required from the broken device. For the Dynabook quirk, verify ELAN coordinates are inverted as expected and unrelated ELAN devices do not inherit the quirk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-dmi-quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of-elan.c -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of-elan.c

## Purpose
`i2c-hid-of-elan.c` is a Device Tree I2C driver for ELAN and compatible touchscreens using HID-over-I2C. It contributes board/chip-specific power sequencing and timing to the shared I2C-HID core.

## Important APIs, Types, and Functions
`struct elan_i2c_hid_chip_data` describes reset delays, post-power delay, HID descriptor address, optional main regulator name, and whether power must follow backlight enable. `struct i2c_hid_of_elan` embeds `i2chid_ops` plus regulators, reset GPIO, `no_reset_on_power_off`, and chip data. `elan_i2c_hid_power_up` and `elan_i2c_hid_power_down` implement the core callbacks. `i2c_hid_of_elan_probe` gathers resources and calls `i2c_hid_core_probe`.

## Control Flow
Probe allocates wrapper state, installs power callbacks, requests optional reset GPIO initially asserted, reads `no-reset-on-power-off`, obtains mandatory `vccio`, fetches match data, optionally obtains the configured main supply, derives `HID_QUIRK_POWER_ON_AFTER_BACKLIGHT`, then calls the core with the chip-specific descriptor address. Power-up asserts reset, enables main supply if present, enables IO supply, waits post-power delay, deasserts reset, and waits post-reset-on delay. Power-down usually asserts reset, waits optional reset-off delay, and disables IO and main rails; when `no-reset-on-power-off` is set it leaves reset deasserted to avoid wasting power on shared rails.

## State and Persistence Behavior
State is devm-managed for the lifetime of the I2C device. Regulator and GPIO state persists in hardware across core probe, suspend, resume, remove, and shutdown via the common core. The `power_after_backlight` flag becomes a HID initial quirk that makes the core register as a DRM panel follower, deferring probe/resume until panel prepare or enable.

## Dependencies and Integration Points
The driver depends on GPIO consumer APIs, regulator APIs, OF match data, HID quirks, and `i2c_hid_core_pm/remove/shutdown`. Supported compatibles include ELAN, FocalTech, Ilitek, and Parade parts that share the I2C-HID protocol but need different timings.

## Risks and Edge Cases
The code assumes `device_get_match_data` is present for all bound devices. Regulator enable failure after enabling `vcc33` is unwound, but Good power sequencing depends on accurate DT supply names and delays. Panel-follower mode disables wakeup in the core because the panel, not the HID device, owns power state. Incorrect `no-reset-on-power-off` can leave a controller in an undefined state or waste power.

## Test Signals
Validate each compatible with cold boot, suspend/resume, panel blank/unblank, touch input after resume, regulator/GPIO traces, and absence of probe deferrals. For power-after-backlight devices, verify the touchscreen appears only after panel power and that remove/unfollow powers down cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of-elan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of-goodix.c -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of-goodix.c

## Purpose
`i2c-hid-of-goodix.c` is a Device Tree wrapper for Goodix touchscreens that speak HID-over-I2C. It handles Goodix-specific regulator and reset timing before delegating protocol handling to the shared core.

## Important APIs, Types, and Functions
`struct goodix_i2c_hid_timing_data` stores post-power and post-reset delays. `struct i2c_hid_of_goodix` embeds `i2chid_ops`, `vdd`, `vddio`, optional reset GPIO, `goodix,no-reset-during-suspend`, and timing match data. `goodix_i2c_hid_power_up`, `goodix_i2c_hid_power_down`, and `i2c_hid_of_goodix_probe` form the driver’s behavior.

## Control Flow
Probe allocates state, installs power callbacks, requests reset GPIO asserted, obtains `vdd` and `mainboard-vddio`, reads the `goodix,no-reset-during-suspend` property, stores match timing data, then calls `i2c_hid_core_probe` with HID descriptor address `0x0001`. Power-up optionally asserts reset when no-reset-during-suspend is active, enables `vdd`, enables `vddio`, waits post-power delay, deasserts reset, then waits post-reset delay. Power-down asserts reset unless the no-reset property says suspend should preserve reset state, then disables `vddio` and `vdd`.

## State and Persistence Behavior
All software state is devm-managed and lives as long as the I2C client. Hardware state persists in regulators and reset GPIO across the core’s probe, PM, remove, and shutdown calls. The wrapper supplies no private shutdown or restore callbacks, so all higher-level HID and power transitions are controlled by `i2c-hid-core.c`.

## Dependencies and Integration Points
The file depends on regulator, GPIO, OF match, I2C, PM, and the common I2C-HID core. It currently binds `goodix,gt7375p` with a 10 ms post-power delay and 180 ms reset-deassert delay.

## Risks and Edge Cases
If enabling `vddio` fails after `vdd` succeeds, the current code returns without disabling `vdd`, which is a power-leak risk on probe/resume failure. The no-reset-during-suspend behavior is board-sensitive: preserving reset may be required for wake/resume but may also leave stale controller state. The hard-coded descriptor address assumes all bound Goodix devices use the same register.

## Test Signals
Check cold boot and resume input events, regulator unwind on induced failures, reset GPIO polarity, descriptor fetch at `0x0001`, and long suspend/resume cycles on boards with and without `goodix,no-reset-during-suspend`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of-goodix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of.c -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of.c

## Purpose
`i2c-hid-of.c` is the generic firmware-property/Device Tree I2C-HID wrapper. It handles common supplies, reset GPIO, descriptor-address property parsing, timing properties, and simple touchscreen axis inversion quirks before calling the common core.

## Important APIs, Types, and Functions
`struct i2c_hid_of` stores embedded `i2chid_ops`, the I2C client, optional reset GPIO, two bulk supplies (`vdd`, `vddl`), and post-power/reset delays. `i2c_hid_of_power_up` and `i2c_hid_of_power_down` are passed to the core. `i2c_hid_of_probe` parses `hid-descr-addr`, optional timing properties, reset GPIO, supplies, and inversion properties.

## Control Flow
Probe requires `hid-descr-addr` and rejects values that do not fit in 16 bits. It reads optional `post-power-on-delay-ms` and kernel-internal `post-reset-deassert-delay-ms`, requests reset asserted, obtains `vdd`/`vddl`, maps `touchscreen-inverted-x/y` to HID quirk bits, then calls `i2c_hid_core_probe`. Power-up enables both regulators, waits post-power delay, deasserts reset, and waits post-reset delay. Power-down asserts reset and disables both regulators.

## State and Persistence Behavior
The wrapper is devm-managed. Persistent hardware state is limited to rail enables and reset GPIO. The HID protocol, buffers, and PM behavior are owned by the common core. The timing properties are copied once at probe and reused for every power-up.

## Dependencies and Integration Points
It depends on device properties usable from OF or platform-created property sets, regulator bulk APIs, GPIO consumer APIs, HID quirk definitions, and `i2c_hid_core_pm/remove/shutdown`. It matches OF compatible `hid-over-i2c` and I2C IDs `hid`/`hid-over-i2c`.

## Risks and Edge Cases
Missing `hid-descr-addr` prevents binding. The `post-reset-deassert-delay-ms` property is explicitly kernel-internal and must not be treated as a generic DT binding without documentation. Boards that need vendor-specific rail ordering, optional rails, or reset behavior should use a vendor wrapper instead. Bulk regulator failure is returned cleanly, but incorrect supply names cause probe failure.

## Test Signals
Validate descriptor reads from the configured address, regulator and reset ordering, axis inversion quirk behavior, suspend/resume, and compatibility with ACPI/platform property injection paths that use the generic wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid.h -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid.h

## Purpose
`i2c-hid.h` is the small shared contract between the I2C-HID core, DMI quirks, and platform/vendor wrappers. It declares optional DMI descriptor/quirk hooks, the wrapper operations structure, exported core lifecycle functions, and the common PM ops.

## Important APIs, Types, and Functions
Under `CONFIG_DMI`, the header declares `i2c_hid_get_dmi_i2c_hid_desc_override`, `i2c_hid_get_dmi_hid_report_desc_override`, and `i2c_hid_get_dmi_quirks`; otherwise static inline stubs return no overrides. `struct i2chid_ops` provides optional `power_up`, `power_down`, `shutdown_tail`, and `restore_sequence` callbacks. The core exports `i2c_hid_core_probe`, `i2c_hid_core_remove`, `i2c_hid_core_shutdown`, and `i2c_hid_core_pm`.

## Control Flow
Wrapper drivers allocate their private state, fill `i2chid_ops`, obtain the HID descriptor address and initial HID quirks, then call `i2c_hid_core_probe`. The core stores the ops pointer and invokes callbacks during power-up/down, hibernation restore, and shutdown. DMI helpers are called inside descriptor/report parsing and quirk setup.

## State and Persistence Behavior
The header owns no storage. It defines callback ownership: wrapper-private structures typically embed `i2chid_ops`, and callbacks use `container_of` to recover regulator/GPIO state. The core assumes the ops object remains valid until remove/shutdown.

## Dependencies and Integration Points
The header depends on `<linux/i2c.h>` and the kernel type namespace. It is included by `i2c-hid-core.c`, `i2c-hid-dmi-quirks.c`, and the OF/vendor wrapper modules.

## Risks and Edge Cases
Because all callbacks are optional, the core must continue checking for `NULL` before invoking them. The ops lifetime is not reference-counted; wrappers must allocate it with device lifetime at least as long as the core instance. DMI helper stubs keep non-DMI builds compiling, but any code relying on overrides must tolerate absence.

## Test Signals
Build coverage with and without `CONFIG_DMI`, module builds for all wrappers, suspend/resume/shutdown callback exercise, and compile-time detection of signature drift between core and wrappers are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/Kconfig

## Purpose
`Kconfig` exposes configuration for Intel Integrated Sensor Hub HID support and its optional host firmware downloader.

## Important APIs, Types, and Functions
`INTEL_ISH_HID` is a tristate for the ISH HID/ISHTP stack. It is presented under an `Intel ISH HID support` menu that depends on `(X86_64 || COMPILE_TEST) && PCI`; the option itself depends on `X86`. `INTEL_ISH_FIRMWARE_DOWNLOADER` is a tristate that depends on `INTEL_ISH_HID` and `X86`, adding host firmware loading from the filesystem.

## Control Flow
There is no runtime control flow. Configuration selects whether the Makefile builds the ISHTP bus/core, IPC PCI driver, HID client, and optional firmware loader modules/objects.

## State and Persistence Behavior
The file owns build-time state only. User or distribution kernel configuration determines whether the ISH stack is unavailable, built in, or modular.

## Dependencies and Integration Points
The menu ties the ISH driver family to x86 and PCI because ISH is exposed as an Intel PCI function. The firmware downloader cannot be enabled without the base transport and HID support.

## Risks and Edge Cases
The top menu allows `COMPILE_TEST`, but the concrete options still depend on `X86`, limiting cross-architecture build coverage. Enabling the firmware downloader without appropriate firmware files and device properties can produce runtime load failures even though build-time dependencies are satisfied.

## Test Signals
Check all `n`, `m`, and `y` combinations for `INTEL_ISH_HID`; verify the downloader appears only when base support is enabled; and run build coverage for built-in and module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/Makefile

## Purpose
The `Makefile` assembles the Intel ISH driver family into separate kernel objects for the ISHTP bus/core, IPC PCI transport, HID client, and optional firmware loader.

## Important APIs, Types, and Functions
`intel-ishtp.o` includes ISHTP initialization, host bus management, client handling, bus registration, DMA interface, client buffers, and loader infrastructure. `intel-ish-ipc.o` includes hardware IPC and PCI glue. `intel-ishtp-hid.o` includes HID glue and the HID ISHTP client. `intel-ishtp-loader.o` includes the host firmware loader when configured. `ccflags-y` adds the local `ishtp` include directory.

## Control Flow
There is no runtime flow. Kconfig symbols decide which composite objects are linked. Splitting IPC, bus, HID, and loader objects allows the base transport and HID stack to be built independently from host firmware loading.

## State and Persistence Behavior
The file controls build products only. Object grouping determines module boundaries and symbol visibility interactions between the ISHTP bus exports, IPC transport, and client drivers.

## Dependencies and Integration Points
The object lists must stay synchronized with source-level exports and headers. The include path allows files outside `ishtp/` to include private transport headers such as `bus.h`.

## Risks and Edge Cases
Missing an object silently breaks link-time symbols or runtime functionality. Moving source files without updating composite object lists can make configured modules incomplete. Because the HID and loader clients register through late init calls, module boundaries and init order matter.

## Test Signals
Build `INTEL_ISH_HID=y/m` and `INTEL_ISH_FIRMWARE_DOWNLOADER=y/m`; verify modules contain expected objects; run modpost for unresolved symbols; and boot-test that PCI probe creates ISHTP bus clients and HID devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/hw-ish-regs.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/hw-ish-regs.h

## Purpose
`hw-ish-regs.h` defines the Intel ISH IPC register map, bit fields, doorbell header encoding, firmware status values, protocol IDs, and management command IDs used by the ISH hardware IPC layer.

## Important APIs, Types, and Functions
Register offsets cover interrupt status/mask, firmware status, host communication, reset, host-to-ISH and ISH-to-host doorbells, message windows, and DMA remap enable. Bit macros define busy bits, host ownership, host ready/ILUP, interrupt enables for Cherry Trail versus Broxton-style hardware, firmware ready/DMA bits, and DMA enable. Header helpers include `IPC_HEADER_GET_LENGTH`, `IPC_HEADER_GET_PROTOCOL`, `IPC_HEADER_GET_MNG_CMD`, `IPC_BUILD_HEADER`, `IPC_BUILD_MNG_MSG`, `IPC_IS_BUSY`, and readiness tests.

## Control Flow
There is no executable flow, but these macros drive `ipc.c`: IRQ handling reads doorbell protocol/length/command, transmit builds doorbell values, reset and clock sync use management commands, and DMA/power handling checks firmware status bits.

## State and Persistence Behavior
The header owns no memory. It names hardware registers whose values persist in the PCI MMIO block and firmware state machine until changed by host, firmware, reset, or power transition.

## Dependencies and Integration Points
It is included by `hw-ish.h` and indirectly by `ipc.c`. It depends on kernel integer types and `GENMASK` availability through surrounding includes. It is the ABI between host driver and ISH firmware/hardware.

## Risks and Edge Cases
Incorrect offsets, masks, or protocol constants break all IPC. The clear macros use XOR to clear bits, so callers must ensure bits are set before using them or risk toggling them on. Platform-specific interrupt bits differ between CHV and later devices; using the wrong path can lose interrupts. Header length masks must match IPC payload limits enforced in the ISR.

## Test Signals
Signals include successful host-ready negotiation, reset-notify exchange, ISHTP message traffic, DMA enable/disable, suspend/resume ACKs, firmware clock sync, and interrupt counters increasing without bad-length drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/hw-ish-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/hw-ish.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/hw-ish.h

## Purpose
`hw-ish.h` declares the Intel ISH hardware IPC provider interface, supported PCI device IDs, revision constants, reset/time-sync payload formats, firmware status enum values, and exported IPC hardware functions.

## Important APIs, Types, and Functions
The PCI ID list covers CHV/BXT/APL/SPT/CNL/GLK/ICL/CML/CMP/EHL/TGL/ADL/RPL/MTL/ARL/LNL/PTL/WCL/NVL variants. Revision constants distinguish Cherry Trail stepping-specific register behavior. `struct ipc_rst_payload_type`, `struct time_sync_format`, and `struct ipc_time_update_msg` define management payloads. `struct ish_hw` stores the MMIO base. Exported functions include `ish_irq_handler`, `ish_dev_init`, `ish_hw_start`, `ish_device_disable`, `ish_disable_dma`, and `ish_set_host_ready`.

## Control Flow
The header has no executable flow. `pci-ish.c` probes matching PCI devices, calls `ish_dev_init`, requests IRQs using `ish_irq_handler`, starts hardware with `ish_hw_start`, and disables it with `ish_device_disable`. `ipc.c` implements the exported hooks.

## State and Persistence Behavior
`struct ish_hw` is embedded after `struct ishtp_device` allocation and persists for the PCI device lifetime. Payload structs are transient management messages. Firmware status enum values describe persistent firmware states visible through the hardware status register.

## Dependencies and Integration Points
The header depends on PCI, interrupt, register definitions, and the ISHTP device structure. It is the bridge between the PCI glue and the low-level IPC implementation.

## Risks and Edge Cases
PCI ID additions must be synchronized with `pci-ish.c` matching and firmware generation metadata. Wrong revision constants can choose the wrong interrupt/host-ready programming path. Time-sync struct packing is firmware ABI-sensitive.

## Test Signals
Probe every supported PCI ID class where available, validate MMIO mapping and IRQ routing, confirm firmware status transitions, and test reset/time-sync management messages across older CHV and newer BXT-style hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/hw-ish.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/ipc.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/ipc.c

## Purpose
`ipc.c` implements the low-level MMIO IPC transport between the host and Intel ISH firmware. It owns register access, interrupt decoding, transmit queueing, management messages, reset handling, clock synchronization, DMA enable/disable, hardware reset, and the `ishtp_hw_ops` callbacks consumed by the ISHTP bus/core.

## Important APIs, Types, and Functions
Inline register helpers `ish_reg_read`/`ish_reg_write` access MMIO. Interrupt/readiness helpers include `check_generated_interrupt`, `ish_is_input_ready`, `ishtp_fw_is_ready`, host-ready setters, and `_ish_read_fw_sts_reg`. Message movement is handled by `_ishtp_read_hdr`, `_ishtp_read`, `write_ipc_to_queue`, `write_ipc_from_queue`, and `ipc_send_mng_msg`. Reset and PM helpers include `ish_send_reset_notify_ack`, `ish_fw_reset_handler`, `fw_reset_work_fn`, `_ish_sync_fw_clock`, `recv_ipc`, `ish_disable_dma`, `ish_wakeup`, `_ish_hw_reset`, `_ish_ipc_reset`, and `ish_hw_start`. `ish_dev_init` allocates and initializes the `ishtp_device`.

## Control Flow
Transmitters call the hardware `write` op, which copies a complete IPC frame into a free `wr_msg_ctl_info`, appends it to `wr_processing_list`, and tries immediate send. `write_ipc_from_queue` checks the host-to-ISH doorbell is idle, optionally refreshes clock-sync payload timestamps, writes message dwords and trailing bytes into host-to-ISH registers, rings the doorbell, updates counters, returns the control block to the free list, and calls completion outside the spinlock.

The IRQ handler first filters shared/spurious interrupts, reads the ISH-to-host doorbell, rejects disabled devices and overlong payloads, then dispatches management protocol to `recv_ipc` or ISHTP protocol to `ishtp_recv`. Management RX complete wakes suspend/resume waiters and drains the TX queue; reset notify sends ACK, marks hardware ready, and queues reset work. Reset work clears pending TX, notifies ISHTP reset, waits for input/FW readiness, then restarts HBM enumeration.

Hardware start sets host ready and sends IPC reset/wakeup. Hardware reset tries PCI function reset, disables DMA, cycles D3hot/D0 through PCI PM config, re-enables DMA, and sends reset. Clock sync is rate-limited to roughly every 20 seconds and writes boottime plus realtime values.

## State and Persistence Behavior
Persistent driver state lives in `struct ishtp_device`: device state, waitqueues, TX free/processing lists, IPC counters, suspend/resume flags, `prev_sync`, workqueue, and hardware ops. File-static `ishtp_dev` and `fw_reset_work` support the reset worker. Hardware state persists in IPC registers, doorbells, host communication bits, DMA remap, PCI power state, and firmware status. Spinlocks protect TX queues; waitqueues synchronize reset, suspend, and resume.

## Dependencies and Integration Points
The file depends on `client.h`, `hbm.h`, `hw-ish.h`, PCI power reset, workqueues, waitqueues, spinlocks, jiffies, and ktime. It exports the transport through `ishtp_hw_ops` to `ishtp-dev`/bus code and is driven by `pci-ish.c` IRQ and lifecycle callbacks.

## Risks and Edge Cases
Global `ishtp_dev` assumes a single active ISH instance. TX queue exhaustion returns `-ENOMEM`; callers must tolerate backpressure. Reset handling clears queued messages, so clients need robust reset callbacks. `timed_wait_for_timeout` subtracts sleep time from an unsigned timeout and depends on sane inputs. Manual cache-snooping platform detection must stay current for DMA correctness. Wrong interrupt path for a device generation can lose or fail to clear interrupts.

## Test Signals
Track IPC TX/RX counters, bad-length logs, reset-notify/ACK exchange, HBM restart after reset, suspend/resume ACKs, DMA inactive waits, host-ready recovery after OOB/power transitions, firmware clock sync messages, and HID sensor enumeration after forced `ish_hw_reset`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/pci-ish.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/pci-ish.c

## Purpose
`pci-ish.c` is the PCI glue for the Intel ISH IPC provider. It binds supported Intel ISH PCI functions, maps BARs, allocates IRQs, initializes the ISHTP hardware device, starts the protocol, handles system sleep/resume, exposes firmware version sysfs attributes, and advertises firmware filenames.

## Important APIs, Types, and Functions
`ishtp_driver_data` stores firmware generation strings for newer platforms. `ish_pci_tbl` maps PCI IDs to optional generation data. `ish_event_tracer` routes driver logs into tracepoints. `ish_init` starts hardware and ISHTP. `ish_probe`, `ish_remove`, and `ish_shutdown` are PCI lifecycle callbacks. PM helpers include `ish_should_enter_d0i3`, `ish_should_leave_d0i3`, `ish_suspend`, `ish_resume`, `ish_resume_handler`, and `ish_freeze`. Sysfs attributes `base_version` and `project_version` expose firmware versions when a generation is known.

## Control Flow
Probe rejects invalid Mehlow IDs, enables the PCI device with managed resources, sets bus mastering, maps BAR0, allocates the ISHTP device through `ish_dev_init`, stores trace and platform firmware metadata, allocates one IRQ vector, requests the IRQ, initializes suspend/resume waitqueues, enables wakeup for EHL, and calls `ish_init`. `ish_init` calls `ish_hw_start` to set host ready/wakeup firmware and `ishtp_start` to begin host bus management enumeration.

Suspend either requests D0i3-style ISHTP suspend and waits briefly for RX complete, or disables DMA before D3. If the suspend ACK does not arrive, it disables DMA so firmware will reset on resume. Resume queues unbound work: if leaving D0i3, it disables IRQ wake if needed, restores host ready, sends resume, waits for ACK, and falls back to full init on failure; otherwise it runs full init. Remove removes all ISHTP clients and disables hardware.

## State and Persistence Behavior
Persistent PCI driver state is stored in `struct ishtp_device` via driver data. Firmware generation metadata controls sysfs visibility and firmware path expectations. Suspend/resume flags and waitqueues persist across PM transitions. Hardware state spans PCI power state, IRQ wake, DMA enable, host-ready bits, and firmware runtime state.

## Dependencies and Integration Points
The file depends on PCI managed APIs, Linux PM/suspend helpers, ISHTP bus/core functions, IPC hardware hooks from `hw-ish.h`, and trace events. It integrates with the optional firmware loader through firmware-name generation metadata and `MODULE_FIRMWARE` declarations.

## Risks and Edge Cases
`ish_resume_device` is file-static, so concurrent resume of multiple devices would be unsafe, though typical systems have one ISH. D0i3 decisions depend on platform firmware suspend/resume paths and CHV exceptions. If resume ACKs are missed, the fallback reinitializes the protocol and clients. Sysfs firmware attributes are hidden unless generation data exists; older devices still work without them. Invalid-platform filtering affects all ISH devices when matching IDs are present.

## Test Signals
Check PCI probe/remove, IRQ mode fallback, HBM/client enumeration, suspend/resume via firmware and non-firmware paths, IRQ wake on EHL, D0i3 versus D3 transitions, sysfs firmware versions on new platforms, tracepoint output, and successful HID sensor operation after resume fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/pci-ish.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-fw-loader.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-fw-loader.c

## Purpose
`ishtp-fw-loader.c` implements an optional ISHTP client that loads main ISH firmware from the host filesystem into ISH SRAM through a shim firmware loader, then starts execution. It supports legacy ISHTP-fragment transfer and direct-DMA transfer.

## Important APIs, Types, and Functions
The loader binds a fixed GUID and defines loader commands `XFER_QUERY`, `XFER_FRAGMENT`, and `START`. Packed protocol structs include `loader_msg_hdr`, query/response formats, firmware/version/capability structs, IPC and DMA fragment formats, and start command. `struct response_info` coordinates synchronous command responses. `struct ishtp_cl_data` stores the client, response state, reset/load work, retry flag, and retry count. Key functions are `get_firmware_variant`, `loader_cl_send`, `process_recv`, `ish_query_loader_prop`, `ish_fw_xfer_ishtp`, `ish_fw_xfer_direct_dma`, `ish_fw_start`, `load_fw_from_host`, `loader_init`, reset/remove/probe callbacks, and module init/exit.

## Control Flow
Probe allocates client state and an ISHTP client, initializes wait/work structures, establishes a connection to the loader GUID, registers the RX callback, takes a device reference, and schedules firmware load work. Loading reads the `firmware-name` property from the parent PCI device, requests `intel/<name>`, queries shim capabilities with image size, validates max image size and DMA cacheline alignment, chooses direct DMA if supported else ISHTP, transfers fragments until the image is complete, then sends START. Retryable failures set `flag_retry`; the error path resets ISH and retries up to three attempts.

The send path installs the expected response buffer, sends through `ishtp_cl_send`, waits up to three seconds, validates callback-reported errors, and returns response size. RX processing validates response buffer presence, one outstanding response, minimum header size, command ID, max size, response bit, and firmware status before copying data and waking the waiter.

## State and Persistence Behavior
Firmware image data is transient from `request_firmware`. Loader response state persists per client and assumes one synchronous command outstanding. Work items persist for firmware loading and reset recovery. Direct DMA allocates a coherent buffer for each load attempt and frees it after transfer. Retry count persists until client reprobe/removal.

## Dependencies and Integration Points
The file depends on firmware_class, ISHTP client APIs, PCI parent device properties, DMA coherent allocation, cache flush APIs, and ISH hardware reset. It registers as an ISHTP client driver via `late_initcall`.

## Risks and Edge Cases
`get_firmware_variant` requires a `firmware-name` property; missing metadata makes loading fail. In direct DMA, payload size is rounded down to a cacheline boundary; if limits are smaller than one cacheline, zero-size allocation/progress would be hazardous. The code flushes a coherent DMA buffer, which is conservative but platform-sensitive. Only one outstanding loader command is supported. Some failures are retryable with full ISH reset, which can disrupt other clients.

## Test Signals
Signals include loader client enumeration, firmware-name property presence, successful query response, selected transfer mode, fragment ACKs for every offset, START ACK, retry behavior on injected transport failures, DMA buffer size/module parameter handling, and main ISH firmware version sysfs updates after load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-fw-loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid-client.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid-client.c

## Purpose
`ishtp-hid-client.c` implements the ISHTP client driver for HID-over-ISH. It connects to the ISH HID firmware GUID, enumerates firmware-published HID devices, fetches HID and report descriptors, registers each with hid-core, sends feature/input requests, and routes published reports back to the right HID device.

## Important APIs, Types, and Functions
The driver binds `hid_ishtp_id_table` and uses ring sizes 32 RX / 16 TX. RX parsing is centralized in `process_recv`, with diagnostics in `report_bad_packet`. HID request helpers exported to `ishtp-hid.c` are `hid_ishtp_set_feature`, `hid_ishtp_get_report`, and `ishtp_hid_link_ready_wait`. Initialization helpers are `ishtp_enum_enum_devices`, `ishtp_get_hid_descriptor`, `ishtp_get_report_descriptor`, and `hid_ishtp_cl_init`. Lifecycle functions include probe, remove, reset, suspend, resume, and workqueue handlers.

## Control Flow
Probe allocates client state and ISHTP client, links them through driver data, initializes waitqueues/work, obtains the trace callback, and calls `hid_ishtp_cl_init`. Init establishes an ISHTP connection to the HID GUID, registers RX callback, sends ENUM_DEVICES with retries, then for each enumerated device requests HID descriptor and report descriptor. On first initialization it calls `ishtp_hid_probe` to allocate and register hid-core devices; on reset it refreshes transport/descriptors without re-adding HID devices.

RX processing accepts one or more hostif messages in a buffer. Enumeration and descriptor responses are only accepted before init completes. GET report responses either copy into a raw request buffer or call `hid_input_report`, then wake waiters. SET feature responses wake waiters. Published input reports are routed directly to matching `hid_sensor_hubs`; aggregated report lists iterate embedded reports. Malformed packets increment `bad_recv_cnt`, log details, and trigger `ish_hw_reset`.

## State and Persistence Behavior
`struct ishtp_cl_data` persists per ISHTP HID client and stores descriptor arrays, device info, hid_device pointers, init flags, suspend state, counters, waitqueues, and work. Descriptors are devm-managed against the ISHTP client device. `suspended` blocks HID requests through `ishtp_hid_link_ready_wait` until resume work clears it. Reset work destroys/re-establishes the connection and retries init up to three times.

## Dependencies and Integration Points
The file depends on ISHTP client APIs, the hostif protocol structs in `ishtp-hid.h`, hid-core registration through `ishtp_hid_probe`, ISH hardware reset, and the ISHTP bus workqueue. It is the main bridge between firmware sensor hub protocol and Linux HID devices.

## Risks and Edge Cases
Packet parsing is defensive but complex; aggregated report pointer arithmetic (`report += sizeof(*report) + payload_len`) relies on compiler pointer scaling and is suspicious because `report` is a `struct report *`, not a byte pointer. `MAX_HID_DEVICES` bounds static arrays, but enumeration count from firmware is assigned directly and allocation uses firmware count; counts above 32 risk array overrun in later descriptor/HID arrays. Reset on malformed packet is disruptive but intended for recovery. Raw request state assumes one outstanding request per HID device.

## Test Signals
Test firmware enumeration, descriptor fetch timeouts, multiple HID devices, raw GET/SET feature reports, asynchronous input reports, aggregated report lists, suspend/resume request blocking, reset recovery, bad packet injection, and bounds behavior for zero or excessive device counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid-client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid.c

## Purpose
`ishtp-hid.c` is the hid-core low-level driver glue for HID devices exposed through the ISHTP HID client. It parses firmware-provided report descriptors, translates hid-core GET/SET report calls into ISH hostif messages, waits for responses, and allocates/removes `hid_device` instances.

## Important APIs, Types, and Functions
The `ishtp_hid_ll_driver` implements parse, start, stop, open, close, request, wait, and raw_request callbacks. `ishtp_hid_parse` calls `hid_parse_report` on the descriptor stored by the client. `ishtp_raw_request` handles userspace-style raw GET/SET reports. `ishtp_hid_request` handles hid-core report requests. `ishtp_wait_for_response` waits for completion. `ishtp_hid_probe`, `ishtp_hid_remove`, and `ishtp_hid_wakeup` are called by `ishtp-hid-client.c`.

## Control Flow
Client initialization calls `ishtp_hid_probe` for each enumerated firmware HID device. Probe allocates a hid device and `ishtp_hid_data`, initializes a waitqueue, stores the device in the client array, fills bus/vendor/product/name fields, assigns the low-level driver, and calls `hid_add_device`. Parse occurs during HID addition and consumes the matching report descriptor.

For GET requests, raw or structured callbacks set request state, optionally provide a raw receive buffer, call `hid_ishtp_get_report`, and rely on `hid_hw_wait`/`.wait` to block until `ishtp_hid_wakeup` marks completion. SET requests allocate a hostif-header-prefixed buffer, encode the HID output report when needed, call `hid_ishtp_set_feature`, and free the temporary buffer.

## State and Persistence Behavior
Per-HID state in `struct ishtp_hid_data` stores enumeration index, request completion flag, client backpointer, waitqueue, and raw request buffer metadata. It persists until `ishtp_hid_remove`, which destroys each HID device and frees its private data. Request completion is a boolean synchronized by waitqueues, so callers assume one active request per HID device.

## Dependencies and Integration Points
The file depends on hid-core, `intel-ish-client-if.h`, hostif definitions in `ishtp-hid.h`, and request send/wakeup helpers from `ishtp-hid-client.c`. It exposes devices on `BUS_INTEL_ISHTP`.

## Risks and Edge Cases
`ishtp_raw_request` returns `len` after `hid_hw_wait` even if the wait path times out internally, so error propagation for raw requests is limited. SET report send is asynchronous and the temporary buffer is freed immediately after `hid_ishtp_set_feature` returns; this relies on lower layers copying the buffer synchronously. The trace macro uses a `client_data` token in this file without a local variable in some functions, which depends on macro behavior and should be build-checked carefully.

## Test Signals
Exercise HID descriptor parsing, hidraw GET/SET feature paths, normal HID request/wait paths, timeout behavior when firmware does not respond, multiple registered HID devices, removal cleanup, and build warnings around trace macro use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid.h

## Purpose
`ishtp-hid.h` defines the hostif HID-over-ISH protocol structures, command constants, per-client/per-HID state containers, trace macro, and cross-file function prototypes shared by the ISHTP HID client and hid-core glue.

## Important APIs, Types, and Functions
Constants define fixed ISH HID VID/PID/version, command mask/response bit, hostif command IDs, and `MAX_HID_DEVICES`. Packed ABI structs include `hostif_msg_hdr`, `hostif_msg`, `hostif_msg_to_sensor`, `device_info`, `ishtp_version`, `report`, and `report_list`. `struct ishtp_cl_data` stores enumeration flags, descriptors, HID device pointers, waitqueues, counters, work items, and the ISHTP client device. `struct ishtp_hid_data` stores per-HID request state and raw request buffers.

## Control Flow
The header has no executable flow. `ishtp-hid-client.c` fills `ishtp_cl_data`, parses hostif messages, and calls functions declared here. `ishtp-hid.c` uses the same state to register hid devices and implement hid-core callbacks.

## State and Persistence Behavior
The structures define persistent runtime ownership: client-level state survives across HID device registration and reset work, while HID-level state survives until HID removal. Report descriptors and HID descriptors are indexed by firmware enumeration order.

## Dependencies and Integration Points
It depends on HID and ISHTP client types being visible to including C files. The hostif packed structs are an ABI with ISH firmware and must match firmware layout exactly.

## Risks and Edge Cases
`MAX_HID_DEVICES` is 32, but client code must explicitly validate firmware counts before indexing arrays. The trace macro calls the function pointer unconditionally; if `ishtp_hid_print_trace` is unset, it can fail. Packed layout and field widths are firmware-sensitive. Aggregated report structs contain flexible arrays and require byte-wise walking by consumers.

## Test Signals
Build both C files against this header, validate hostif struct sizes against firmware documentation, test firmware enumeration counts at boundaries, and verify command IDs and response-bit handling with real or mocked firmware messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/bus.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/bus.c

## Purpose
`ishtp/bus.c` implements the Linux bus layer for ISHTP firmware clients. It dispatches received ISHTP messages, sends ISHTP frames through hardware ops, creates `ishtp` bus devices for firmware-advertised clients, registers/unregisters client drivers, schedules RX callbacks, handles reset removal/rebind, and exposes helper APIs to client drivers.

## Important APIs, Types, and Functions
Message functions include `ishtp_recv`, `ishtp_send_msg`, and `ishtp_write_message`. Firmware lookup helpers include `ishtp_fw_cl_by_uuid`, `ishtp_fw_cl_get_client`, `ishtp_get_fw_client_id`, and `ishtp_fw_cl_by_id`. Bus callbacks are `ishtp_cl_device_probe`, match, remove, suspend, resume, reset, uevent, and modalias. Device helpers include `ishtp_bus_add_device`, `ishtp_bus_new_client`, `ishtp_cl_device_bind`, `ishtp_bus_remove_all_clients`, `ishtp_register_event_cb`, get/put drvdata, `ishtp_device`, `ishtp_get_pci_device`, `ishtp_get_workqueue`, `ishtp_trace_callback`, and `ish_hw_reset`.

## Control Flow
`ishtp_recv` reads the ISHTP header from hardware, rate-syncs firmware clock, validates fragment length against MTU, then dispatches HBM, fixed-client, or normal client messages. Sending wraps an ISHTP header and payload with an IPC doorbell header produced by hardware ops and queues it to the IPC layer.

When HBM discovers a new firmware client, `ishtp_bus_new_client` builds a GUID-based name and calls `ishtp_bus_add_device`. Existing names are treated as reset/rebind cases: the firmware client pointer is refreshed and the client driver reset callback is invoked. New devices are registered on the `ishtp` bus and matched against driver GUID tables. RX events queue work on the ISHTP unbound workqueue and invoke the registered event callback. Reset handling marks the device resetting, clears bottom-half queues, removes or disconnects clients, frees DMA/client arrays, and reset completion restarts HBM discovery.

## State and Persistence Behavior
`ishtp_device_ready` gates late client-driver registration until the bus has at least one device. Each `ishtp_cl_device` stores parent device, firmware client pointer, list link, event work, driver data, manual reference count, and callback. Device lists and client lists are protected by spinlocks. Firmware client arrays are freed and rebuilt across reset.

## Dependencies and Integration Points
The file depends on the Linux driver model, module/bus APIs, ISHTP device/client internals, HBM helpers, and hardware ops from IPC. HID and firmware-loader clients register through `ishtp_cl_driver_register` and receive probe/reset/remove callbacks from this bus.

## Risks and Edge Cases
The manual `reference_count` is not a kref and is manipulated without locking in helpers, so reset/remove races need care. `ishtp_cl_driver_register` returns `-ENODEV` until `ishtp_device_ready`, which can affect module load ordering. Warm reset preserves referenced devices but clears firmware pointers, so client reset code must re-establish connections. Device naming by GUID assumes uniqueness.

## Test Signals
Validate HBM enumeration, uevent/modalias generation, driver autoload/probe, RX event callback scheduling, reset rebind of existing devices, client removal on cold remove, suspend/resume callback propagation, DMA module parameter behavior, and no use-after-free under reset storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/bus.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/bus.h

## Purpose
`ishtp/bus.h` declares the private/public ISHTP bus interfaces used by the transport core and ISHTP client drivers. It defines `struct ishtp_cl_device` and prototypes for message send, client enumeration, RX events, reset handling, and helper accessors.

## Important APIs, Types, and Functions
`struct ishtp_cl_device` embeds a Linux `device`, points to the owning `ishtp_device` and `ishtp_fw_client`, links into the device list, stores event work, driver data, manual reference count, and an event callback. Prototypes include `ishtp_bus_new_client`, `ishtp_cl_device_bind`, `ishtp_cl_bus_rx_event`, `ishtp_send_msg`, `ishtp_write_message`, `ishtp_use_dma_transfer`, `ishtp_bus_remove_all_clients`, `ishtp_recv`, `ishtp_reset_handler`, `ishtp_reset_compl_handler`, and `ishtp_fw_cl_by_uuid`.

## Control Flow
The header has no executable flow. HBM code calls `ishtp_bus_new_client` when firmware clients are discovered. Transport IRQ code calls `ishtp_recv`. Client code sends through `ishtp_send_msg`/`ishtp_write_message` indirectly or directly and uses RX event callbacks scheduled by `ishtp_cl_bus_rx_event`.

## State and Persistence Behavior
The structure defines device lifetime and callback state for bus clients. Event work and driver data persist until device removal or reset cleanup.

## Dependencies and Integration Points
It depends on Linux device/model headers and `intel-ish-client-if.h`. It is included by bus implementation, IPC glue, and ISHTP clients that need bus helper APIs.

## Risks and Edge Cases
The manual reference count field requires disciplined get/put usage and does not itself enforce lifetime safety. Event callbacks can be cleared during reset/remove, so users must tolerate missing callbacks. Header prototypes must remain synchronized with exported symbols in `bus.c`.

## Test Signals
Build all ISHTP clients, verify reset/remove callback paths, RX event delivery, message send prototypes, and correct parent/firmware-client pointers during client binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client-buffers.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client-buffers.c

## Purpose
`client-buffers.c` manages per-client ISHTP RX and TX ring buffers plus IO request block recycling. It is the allocation/free/recycle layer used by ISHTP clients after connection setup.

## Important APIs, Types, and Functions
RX APIs are `ishtp_cl_alloc_rx_ring`, `ishtp_cl_free_rx_ring`, `ishtp_io_rb_init`, `ishtp_io_rb_alloc_buf`, `ishtp_cl_io_rb_recycle`, and `ishtp_cl_rx_get_rb`. TX APIs are `ishtp_cl_alloc_tx_ring` and `ishtp_cl_free_tx_ring`. `ishtp_io_rb_free` frees a standalone request block.

## Control Flow
RX ring allocation uses the firmware client maximum message length, creates `rx_ring_size` request blocks, allocates each data buffer, and appends them to `free_rb_list` under `free_list_spinlock`. TX allocation creates `tx_ring_size` transmit ring entries, allocates send buffers of the same max message length, appends them to `tx_free_list`, and increments `tx_ring_free_size`. Failure paths call the corresponding free function to unwind partial allocation.

RX free drains both free and in-process lists under their spinlocks, freeing data buffers and request blocks. TX free drains both free and active TX lists. Recycling returns an RX block to the free list and, if the client has no outgoing flow-control credits, calls `ishtp_cl_read_start` to notify firmware that receive capacity is available. `ishtp_cl_rx_get_rb` removes the first in-process RX block for client event callbacks.

## State and Persistence Behavior
Ring entries persist for the connection lifetime and are freed on disconnect/reset/remove. List membership tracks ownership: free RX, in-process RX, free TX, and active TX. Spinlocks protect list mutation and `tx_ring_free_size`.

## Dependencies and Integration Points
The file depends on `client.h` definitions for `struct ishtp_cl`, request block types, lists, spinlocks, and flow-control helper `ishtp_cl_read_start`. It is called from ISHTP client connection setup and reset cleanup.

## Risks and Edge Cases
Max message length comes from firmware properties; a bogus large value can drive memory pressure. `ishtp_cl_io_rb_recycle` appends without checking whether the block is already on a list, so double recycle would corrupt lists. Free paths assume no concurrent users remain; reset/remove ordering must cancel callbacks first. Flow-control restart during recycle can fail and returns the error to the caller, but many callbacks may ignore it.

## Test Signals
Test allocation failure unwind, normal RX event recycle, flow-control restart when credits are exhausted, reset cleanup with in-process buffers, TX free-size accounting, and concurrency under high-rate sensor reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client-buffers.c -->
