# subset-b-005526 Research

Grouped source research for Renesas USBHS RZ/A2 glue, USB role-switch core and Intel xHCI role switch glue, and the early USB serial driver set from AIRcable through Cypress M8. Each section is marker-delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza2.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza2.c

## Purpose

This file supplies Renesas USBHS platform callbacks for RZ/A2 and RZ/G2L-family USBHS blocks. It binds the common Renesas USBHS core to the SoC-specific PHY lifecycle, suspend-mode bit programming, gadget-only ID policy, and platform capability flags. The complete 86-line source was read.

## Important APIs, Types, and Functions

The key callbacks are `usbhs_rza2_hardware_init()`, `usbhs_rza2_hardware_exit()`, and `usbhs_rza2_power_ctrl()`. They are installed through `struct renesas_usbhs_platform_info` instances `usbhs_rza2_plat_info` and `usbhs_rzg2l_plat_info`. The code uses `usbhs_pdev_to_priv()`, `usbhs_bset()`, `phy_get()`, `phy_put()`, `phy_init()`, `phy_power_on()`, `phy_power_off()`, and `phy_exit()`.

## Control Flow

Probe-time common USBHS code calls `hardware_init`, which obtains the `"usb"` PHY and stores it in `priv->phy`. Runtime power transitions call `power_ctrl`: enable initializes the PHY, sets `SUSPMODE.SUSPM`, waits 100 microseconds for PLL stability, then powers the PHY on if initialization succeeded; disable clears `SUSPM`, powers the PHY off, and exits the PHY. Removal calls `hardware_exit`, which releases the PHY and clears the cached pointer.

## State and Persistence Behavior

The only persistent state owned here is the PHY pointer cached in `struct usbhs_priv`. Hardware-visible state is limited to the `SUSPMODE` register bit and PHY power/init state. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on the Linux PHY framework, Renesas USBHS common headers, and platform-device glue. It integrates with the generic Renesas USBHS driver through platform callbacks and with board firmware through the named PHY. Both platform-info objects force gadget identity using `usbhs_get_id_as_gadget`; RZ/A2 additionally sets `has_new_pipe_configs`.

## Risks and Edge Cases

Risks include missing or deferred PHY lookup, unbalanced PHY init/power calls if upper layers call power transitions unexpectedly, ignoring the `base` argument because register access goes through `usbhs_priv`, and PLL timing sensitivity. On the enable path `SUSPM` is set even if `phy_init()` failed, so callers rely on the returned error and later disable cleanup.

## Test Signals

Useful validation includes RZ/A2 and RZ/G2L probe/remove with a real or stub `"usb"` PHY, runtime enable/disable cycles, failure injection for `phy_get()`, `phy_init()`, and `phy_power_on()`, checking `SUSPMODE.SUSPM` transitions, and gadget enumeration after PLL-stability delay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/roles/Kconfig

## Purpose

This Kconfig file defines the USB role-switch subsystem option and the Intel xHCI role-switch driver option. It controls whether the generic role class and the Intel ACPI/x86 glue driver are built into the kernel or as modules.

## Important APIs, Types, and Functions

The relevant symbols are `USB_ROLE_SWITCH` and `USB_ROLES_INTEL_XHCI`. `USB_ROLE_SWITCH` is a tristate that builds the role-switch class as `roles.ko` when modular. `USB_ROLES_INTEL_XHCI` is a tristate visible only when role-switch support is enabled and depends on `ACPI && X86`; its module is `intel-xhci-usb-role-switch`.

## Control Flow

There is no runtime flow. During configuration, enabling `USB_ROLE_SWITCH` opens the nested menu and allows Intel role-switch selection. Build-system expansion later maps these symbols to `class.o` and `intel-xhci-usb-role-switch.o` in the local Makefile.

## State and Persistence Behavior

The file stores no runtime state. It persists build policy in kernel configuration and therefore affects module availability, sysfs class presence, and whether controller drivers can link against role-switch APIs.

## Dependencies and Integration Points

It integrates with the USB role-switch public API under `include/linux/usb/role.h`, with controller drivers that call `usb_role_switch_register()` or `usb_role_switch_get()`, and with Intel SoC ACPI/xHCI/DWC3 platforms.

## Risks and Edge Cases

Build risks include users selecting Intel role-switch support without the surrounding ACPI/x86 platform, missing role-switch support for dual-role controllers, and module/builtin mismatches with consumers. The help text correctly describes mux-based and controller-integrated switches, so misconfiguration is mainly a platform-integration issue.

## Test Signals

Test signals are `allmodconfig` and `allyesconfig` builds, X86 ACPI builds with and without `USB_ROLE_SWITCH`, module-name checks for `roles.ko` and `intel-xhci-usb-role-switch.ko`, and menuconfig visibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/roles/Makefile

## Purpose

This Makefile maps USB role-switch Kconfig symbols to build objects. It builds the generic role-switch class and, when selected, the Intel xHCI role-switch platform driver.

## Important APIs, Types, and Functions

`obj-$(CONFIG_USB_ROLE_SWITCH) += roles.o` builds the aggregate role class module, `roles-y := class.o` defines its content, and `obj-$(CONFIG_USB_ROLES_INTEL_XHCI) += intel-xhci-usb-role-switch.o` builds the Intel-specific driver.

## Control Flow

There is no runtime flow. Kbuild expands the selected symbols into object lists and links either built-in objects or modules according to tristate configuration.

## State and Persistence Behavior

No runtime state is owned here. The persistent effect is the object-to-symbol build contract: `class.c` is the only object in `roles.o`, while the Intel driver remains a separate module/object.

## Dependencies and Integration Points

The Makefile integrates with `drivers/usb/roles/Kconfig`, kernel module naming, and exported APIs consumed by other USB controller and connector drivers.

## Risks and Edge Cases

Risks are simple build-map drift: adding source files without updating `roles-y`, renaming modules without Kconfig/help updates, or accidentally folding Intel platform glue into the generic role module.

## Test Signals

Build USB role support as built-in and module, inspect generated modules, and confirm `class.o` exports role-switch APIs while Intel glue is independently selectable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/class.c -->
# sources/distributed-fs/ceph-client/drivers/usb/roles/class.c

## Purpose

This file implements the Linux USB role-switch class. It provides the exported API used by USB controller, connector, mux, and PHY drivers to register a switch, find it through firmware-node or device-connection relationships, set or get host/device/none role, and optionally expose userspace control through sysfs. The complete 469-line source was read.

## Important APIs, Types, and Functions

The core type is private `struct usb_role_switch`, containing `struct device dev`, a lockdep-keyed mutex, owner module, cached `enum usb_role`, registration flag, optional `usb2_port`, `usb3_port`, `udc`, callbacks `set` and `get`, and `allow_userspace_control`. Exported functions include `usb_role_switch_register()`, `usb_role_switch_unregister()`, `usb_role_switch_set_role()`, `usb_role_switch_get_role()`, `usb_role_switch_get()`, `fwnode_usb_role_switch_get()`, `usb_role_switch_put()`, `usb_role_switch_find_by_fwnode()`, `usb_role_string()`, and driver-data accessors. Sysfs is centered on the `role` attribute.

## Control Flow

At subsystem init, `usb_roles_init()` registers the `usb_role` class. A provider calls `usb_role_switch_register()`, which validates `desc->set`, allocates the switch, initializes the mutex, copies descriptor fields, binds the parent driver owner, assigns class/type/fwnode/name, registers the device, and optionally adds component binding for connector symlinks. Consumers find a switch via parent connector fwnode or device/fwnode connection lookup, then the class bumps the provider module reference. Setting a role locks the switch, calls the provider `set()` callback, caches the new role on success, and emits a `KOBJ_CHANGE` uevent. Getting a role calls provider `get()` if present or returns the cached role.

## State and Persistence Behavior

State is in memory and device-model visible: cached role, registration state, driver data, sysfs attribute visibility, module reference, and connector symlinks. No persistent storage is used. Userspace may write `host`, `device`, `none`, or boolean false only when `allow_userspace_control` makes the attribute visible.

## Dependencies and Integration Points

The file depends on the device model class API, firmware-node/property connection lookup, component framework, sysfs, uevents, lockdep, module refcounting, and `include/linux/usb/role.h`. It integrates with Type-C connector devices by creating reciprocal `connector` and `usb-role-switch` sysfs links during component bind.

## Risks and Edge Cases

Important risks are lifetime and registration races: `set_role()` rejects unregistered switches, but callers can still hold references during unregister. Module reference acquisition uses `try_module_get()` with `WARN_ON`, so odd owner state is noisy but not fatal. The parent-fwnode connector path must put the parent fwnode correctly, and missing role-switch providers return `-EPROBE_DEFER`. Sysfs `role_show()` indexes `usb_roles[role]`, so provider `get()` must return a valid enum. Component symlink creation failure only warns after registration.

## Test Signals

Tests should cover provider register/unregister, consumer lookup by device connection and fwnode, usb-b-connector parent lookup, sysfs visibility with and without userspace control, valid and invalid role writes, uevent contents, connector symlink creation/removal, module refcount get/put, concurrent set/get/unregister under lockdep/KCSAN, and provider callbacks returning errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/intel-xhci-usb-role-switch.c -->
# sources/distributed-fs/ceph-client/drivers/usb/roles/intel-xhci-usb-role-switch.c

## Purpose

This platform driver exposes the internal Intel xHCI USB OTG role switch found on Cherry Trail, Broxton, and related SoCs as a generic USB role switch. It programs dual-role configuration registers that select xHCI host mode or DWC3 gadget/device mode and allows userspace role control through the role-switch class. The complete 227-line source was read.

## Important APIs, Types, and Functions

The private state is `struct intel_xhci_usb_data`, containing the device, registered `usb_role_switch`, MMIO base, and `enable_sw_switch` quirk flag. Main functions are `intel_xhci_usb_probe()`, `intel_xhci_usb_remove()`, `intel_xhci_usb_set_role()`, and `intel_xhci_usb_get_role()`. Hardware definitions include `DUAL_ROLE_CFG0`, `SW_VBUS_VALID`, `SW_IDPIN_EN`, `SW_IDPIN`, `SW_SWITCH_EN`, `DRD_CONFIG_*`, `DUAL_ROLE_CFG1`, and `HOST_MODE`.

## Control Flow

Probe allocates state, maps MMIO resource 0, registers a software node, fills a `usb_role_switch_desc` with set/get callbacks and userspace control, checks the `sw_switch_disable` property, registers the role switch, and enables runtime PM. `set_role()` acquires the ACPI global lock to serialize with AML handlers, resumes the device, edits CFG0 ID/VBUS/dynamic/static bits for none/host/device, optionally sets `SW_SWITCH_EN`, writes CFG0, releases the ACPI lock, then polls CFG1 for `HOST_MODE` to match the requested role for up to 1000 ms. `get_role()` resumes, reads CFG0, and derives role from ID pin and VBUS-valid bits. Remove disables runtime PM, unregisters the role switch, and releases the software fwnode reference.

## State and Persistence Behavior

Driver state is devm-managed except the software node registration/reference and role-switch registration. Hardware state persists in CFG0/CFG1 dual-role registers across callbacks and potentially across firmware interaction. Runtime PM state is updated around each register transaction.

## Dependencies and Integration Points

The driver depends on ACPI, x86 platform-device enumeration, MMIO mapping, runtime PM, software nodes, and the generic USB role-switch class. It coordinates with ACPI AML by using `acpi_acquire_global_lock()` because platform firmware may read-modify-write the same CFG0 register.

## Risks and Edge Cases

Risks include global software-node registration collisions if multiple instances exist, missing cleanup of the software-node registration itself, `pm_runtime_get_sync()` errors not checked, ACPI lock acquisition failure, firmware racing if the global lock is absent, platforms requiring `sw_switch_disable`, and timeout when hardware does not reflect the requested host bit. Register programming for `USB_ROLE_NONE` still waits for non-host state, which may not prove true electrical idle.

## Test Signals

Validate host/device/none sysfs role writes on affected Intel SoCs, CFG0/CFG1 traces, AML event races, `sw_switch_disable` platforms, runtime suspend/resume around role changes, timeout injection, remove/reprobe, and userspace-visible uevents from the role class. Build coverage requires `ACPI && X86`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/intel-xhci-usb-role-switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/Kconfig

## Purpose

This Kconfig file declares USB serial converter support, the optional USB serial console, the generic/simple drivers, and a large matrix of device-specific USB serial drivers. It is the configuration front door for the USB serial core and all listed converter modules.

## Important APIs, Types, and Functions

The main symbol is `USB_SERIAL`, a `menuconfig` tristate depending on `TTY`. Important nested symbols in this work item include `USB_SERIAL_CONSOLE`, `USB_SERIAL_GENERIC`, `USB_SERIAL_AIRCABLE`, `USB_SERIAL_ARK3116`, `USB_SERIAL_BELKIN`, `USB_SERIAL_CH341`, `USB_SERIAL_CP210X`, `USB_SERIAL_CYBERJACK`, and `USB_SERIAL_CYPRESS_M8`. The file also declares many other converter options such as FTDI, PL2303, option, sierra, TI, and WWAN helper symbols.

## Control Flow

There is no runtime control flow. When `USB_SERIAL` is enabled, nested config entries become visible and selected symbols drive `drivers/usb/serial/Makefile`. Some entries select helper dependencies, for example `USB_SERIAL_WHITEHEAT` and `USB_SERIAL_KEYSPAN` select `USB_EZUSB_FX2`, while modem drivers select `USB_SERIAL_WWAN`.

## State and Persistence Behavior

The persistent state is kernel configuration. It determines whether the usbserial core is present, whether the console code is compiled into a built-in core, and which per-device modules can bind to USB IDs at runtime.

## Dependencies and Integration Points

The file integrates with the TTY subsystem, USB core, per-driver Makefile object rules, Documentation/usb/usb-serial.rst, and optional helper subsystems such as PARPORT or EZUSB firmware loading.

## Risks and Edge Cases

Risks include selecting console support only when `USB_SERIAL=y`, hidden helper symbols such as `USB_SERIAL_WWAN` being selected by modem drivers, module names needing to match Makefile outputs, and old help URLs or device lists becoming stale. Configuration gaps show up as devices matching no built module even though the usbserial core is present.

## Test Signals

Use `olddefconfig`, `allmodconfig`, `allyesconfig`, and focused builds for each symbol in this work item. Runtime signals include expected module aliases, `modinfo` names, successful `ttyUSB` registration, and console availability only in built-in usbserial configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/Makefile

## Purpose

This Makefile maps USB serial Kconfig symbols to the core usbserial aggregate and individual converter driver objects. It is the build manifest for the drivers covered in this subset.

## Important APIs, Types, and Functions

`obj-$(CONFIG_USB_SERIAL) += usbserial.o` builds the core. `usbserial-y := usb-serial.o generic.o bus.o` defines always-built core objects, and `usbserial-$(CONFIG_USB_SERIAL_CONSOLE) += console.o` conditionally adds console support. Relevant per-device mappings include `aircable.o`, `ark3116.o`, `belkin_sa.o`, `ch341.o`, `cp210x.o`, `cyberjack.o`, and `cypress_m8.o`.

## Control Flow

There is no runtime flow. Kbuild expands each selected symbol into either built-in objects or modules, preserving the core/per-device split so many converters can be built independently while sharing `usbserial.o`.

## State and Persistence Behavior

No runtime state exists here. The durable contract is module composition: `bus.o` and optionally `console.o` are part of the core, while converter modules register through `module_usb_serial_driver()`.

## Dependencies and Integration Points

The file integrates with `drivers/usb/serial/Kconfig`, Linux Kbuild, USB serial core registration, module alias generation, and optional helper modules such as `usb_wwan.o`.

## Risks and Edge Cases

Risks are object-list drift when adding or renaming drivers, console code being linked only for built-in core support as intended by Kconfig, and accidentally omitting shared helper objects from `usbserial-y`.

## Test Signals

Build `USB_SERIAL=y/m`, toggle `USB_SERIAL_CONSOLE`, and build each relevant converter as module. Check resulting module names, dependencies, and that core symbols resolve for converter modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/aircable.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/aircable.c

## Purpose

This driver supports the AIRcable USB Bluetooth dongle as a USB serial device. The device presents multiple interfaces; the driver ignores the firmware/control interface without bulk-out endpoints and binds the serial interface. The complete 160-line source was read.

## Important APIs, Types, and Functions

The USB ID table matches vendor `0x16ca`, product `0x1502`. Key functions are `aircable_calc_num_ports()`, `aircable_prepare_write_buffer()`, `aircable_process_read_urb()`, and `aircable_process_packet()`. The driver fills `struct usb_serial_driver aircable_device` with `bulk_out_size = 64`, custom read and write framing, and generic throttle/unthrottle.

## Control Flow

During probe, `calc_num_ports` rejects the first interface when it lacks bulk-out endpoints and returns one port for the serial interface. Writes pull payload from `port->write_fifo`, reserve four bytes for a header, prepend `0x20 0x29` and a little-endian payload length, and submit a 64-byte-framed packet through the generic write path. Reads inspect whether the URB begins with the receive header prefix `0x00`; if so each 64-byte frame skips a four-byte header, otherwise data is passed through directly for the documented overflow/no-header case.

## State and Persistence Behavior

The driver owns no private allocation. It relies on the usbserial port write FIFO, tty flip buffer, and generic throttle flags. No persistent configuration is stored.

## Dependencies and Integration Points

Dependencies are the USB serial core, tty flip buffering, unaligned little-endian helpers, and generic usbserial write/throttle helpers. It integrates by implementing only the protocol framing hooks required by this device.

## Risks and Edge Cases

Risks include malformed frames shorter than the four-byte header, devices sending mixed header/no-header frames in one URB because `has_headers` is determined once per URB, payload lengths not being validated against the header value, and the first-interface rejection depending solely on endpoint layout.

## Test Signals

Test with a real AIRcable dongle or emulation covering both interfaces, writes spanning exactly and less than 60 payload bytes, receive frames with headers, receive data without headers, zero-length and short malformed packets, and throttle/unthrottle behavior under tty backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/aircable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ark3116.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ark3116.c

## Purpose

This driver supports ARK Micro 3116 USB serial and IrDA adapters. It models the chip as a 16450-style UART behind USB vendor control messages, with bulk endpoints for data and an interrupt endpoint for modem/line-status changes. The complete 734-line source was read.

## Important APIs, Types, and Functions

Private state `struct ark3116_private` stores IrDA mode, `hw_lock`, baud divisor `quot`, line-control `lcr`, handshake-control `hcr`, modem-control `mcr`, `status_lock`, modem-status `msr`, and line-status `lsr`. Major functions are `ark3116_port_probe()`, `ark3116_open()`, `ark3116_close()`, `ark3116_set_termios()`, `ark3116_tiocmget()`, `ark3116_tiocmset()`, `ark3116_break_ctl()`, `ark3116_read_int_callback()`, and `ark3116_process_read_urb()`. Register access is via `ark3116_write_reg()` and `ark3116_read_reg()`.

## Control Flow

Port probe allocates private state, detects IrDA by USB ID, initializes UART-like registers, sets RS232 or IrDA magic registers, programs 9600 8N1, and disables extra baud override. Open starts generic bulk I/O, drains stale RX, reads initial MSR/LSR, submits the interrupt URB, enables modem/line-status interrupts, enables DMA-select in FCR, and applies termios. Termios builds LCR from character size/parity/stop bits, computes a 12 MHz based divisor, handles 460800/921600 override register values, serializes hardware updates with `hw_lock`, and warns that software flow control is not implemented. Interrupt URBs decode `0xe8 IIR LSR MSR`, update status counters and wake waiters; bulk reads apply the accumulated LSR error flags to received data.

## State and Persistence Behavior

Private state mirrors hardware registers across operations and survives while the port object exists. `hw_lock` serializes register writes that must be consistent, while `status_lock` protects async status from interrupt callbacks. Hardware settings persist in chip registers until changed or the device resets.

## Dependencies and Integration Points

The driver depends on USB serial core, tty/termios, serial UART register definitions, generic `tiocmiwait` and `get_icount`, and vendor control endpoint 0. It integrates with tty modem-control ioctls, break control, and tty error flag propagation.

## Risks and Edge Cases

Risks include incomplete error-to-byte ordering because status arrives on the interrupt endpoint separately from bulk data, undocumented IrDA magic registers, unsupported XON/XOFF despite termios requests, unchecked write-register failures in many setup paths, high-speed divisor uncertainty, and hardware-lock ordering with close/open transitions.

## Test Signals

Validate RS232 and IrDA IDs, probe register sequence, 9600 default, termios matrix for data bits/parity/stop/baud including 0, 460800, and 921600, modem-control set/get, break toggling, interrupt status changes with `TIOCMIWAIT`, injected LSR errors on bulk reads, disconnect during open, and suspend/remove with active URBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ark3116.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/belkin_sa.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/belkin_sa.c

## Purpose

This driver supports Belkin, Peracom, GoHubs, HandyLink, and Belkin dockstation single-port USB serial adapters. It sends vendor control requests for baud, framing, flow control, modem lines, and break, while using interrupt status reports for modem and line status. The complete 480-line source was read.

## Important APIs, Types, and Functions

Private state `struct belkin_sa_private` contains a spinlock, `control_state`, `last_lsr`, `last_msr`, and `bad_flow_control`. Main functions are `belkin_sa_port_probe()`, `belkin_sa_open()`, `belkin_sa_close()`, `belkin_sa_read_int_callback()`, `belkin_sa_process_read_urb()`, `belkin_sa_set_termios()`, `belkin_sa_break_ctl()`, `belkin_sa_tiocmget()`, and `belkin_sa_tiocmset()`. `BSA_USB_CMD()` wraps the adapter's vendor requests from `belkin_sa.h`.

## Control Flow

Probe allocates private state and flags old firmware (`bcdDevice <= 0x0206`) as having bad flow-control behavior. Open submits the interrupt URB first, then starts generic bulk I/O; close stops generic I/O and kills the interrupt URB. Interrupt callbacks update cached MSR/LSR and modem-control state bits, then resubmit the interrupt URB. Read URB processing consumes the cached LSR error bits, maps break/parity/framing/overrun to tty flags, and pushes bulk data. Termios sends control requests when baud, parity, data bits, stop bits, or flow-control settings change; B0 disables flow control and drops DTR/RTS.

## State and Persistence Behavior

The private `control_state` combines requested DTR/RTS and observed DSR/CTS/RI/CD. `last_lsr` is consumed by the next read and error bits are cleared after use. Device settings persist in adapter firmware until changed, unplugged, or reset.

## Dependencies and Integration Points

The driver depends on the USB serial core, tty termios, tty flip buffering, spinlocks, and constants from `belkin_sa.h`. It exposes standard tty modem-control, break, and line-discipline behavior through usbserial callbacks.

## Risks and Edge Cases

Risks include stale line-status attribution because errors are reported separately from bulk data, reliance on interrupt packet indexes without length validation, old firmware flow-control quirks, vendor command failures that log but do not always roll back termios, and cached modem state standing in for true query support.

## Test Signals

Exercise all supported USB IDs, old and new `bcdDevice` flow-control behavior, open/close interrupt URB handling, B0 hangup and reassertion from B0, baud clipping, parity/data/stop changes, RTS/DTR ioctls, break control, injected LSR errors, and disconnect during active interrupt resubmission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/belkin_sa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/belkin_sa.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/belkin_sa.h

## Purpose

This header defines USB IDs, vendor request numbers, request type, baud/framing conversion macros, flow-control bits, and interrupt status register masks for the Belkin serial adapter driver.

## Important APIs, Types, and Functions

Important definitions include vendor/product IDs for Belkin, old Belkin, Peracom, GoHubs, HandyLink, vendor requests such as `BELKIN_SA_SET_BAUDRATE_REQUEST`, `BELKIN_SA_SET_DTR_REQUEST`, `BELKIN_SA_SET_RTS_REQUEST`, `BELKIN_SA_SET_BREAK_REQUEST`, and `BELKIN_SA_SET_FLOW_CTRL_REQUEST`, conversion macros `BELKIN_SA_BAUD()`, `BELKIN_SA_STOP_BITS()`, `BELKIN_SA_DATA_BITS()`, parity constants, flow-control bit masks, and 16550-like LSR/MSR indexes and flags.

## Control Flow

The header has no executable flow. `belkin_sa.c` uses these constants to assemble USB control requests and decode interrupt endpoint status bytes.

## State and Persistence Behavior

No storage is owned here. The values define the protocol contract for hardware state programmed by control messages and status state reported by interrupt packets.

## Dependencies and Integration Points

The header integrates only with the Belkin driver and the USB serial core indirectly. Its register layout comments explain why interrupt bytes are decoded like 16550 LSR/MSR fields.

## Risks and Edge Cases

Risks include protocol constants being inferred from reverse engineering, unsupported placeholder requests hidden under `WHEN_I_LEARN_THIS`, baud conversion division-by-zero if misused with zero baud, and drift between bit masks and firmware behavior.

## Test Signals

Compile include-order coverage, static checks that request values match driver use, and runtime tests for each request constant through the Belkin driver's termios, modem-control, flow-control, break, and status paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/belkin_sa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/bus.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/bus.c

## Purpose

This file implements the `usb-serial` bus used by the USB serial core to bind already-detected serial ports to their converter drivers, register tty devices, expose dynamic USB IDs, and deregister driver state. The complete 171-line source was read.

## Important APIs, Types, and Functions

The central object is exported `const struct bus_type usb_serial_bus_type` with `.match`, `.probe`, `.remove`, and driver attribute groups. Important functions are `usb_serial_device_match()`, `usb_serial_device_probe()`, `usb_serial_device_remove()`, `new_id_store()`, `new_id_show()`, `usb_serial_bus_register()`, `usb_serial_bus_deregister()`, and `free_dynids()`.

## Control Flow

`usb_serial_bus_register()` assigns the bus to a `struct usb_serial_driver`, initializes its dynamic-ID list, and calls `driver_register()`. Matching is simple because `serial_probe` has already assigned `port->serial->type`; the bus match returns true only for that driver. Probe obtains an autopm reference to block suspend races, invokes optional `port_probe`, registers the tty device at `ttyUSB<minor>`, releases autopm, and logs attachment. Remove obtains autopm when possible, unregisters the tty device, calls optional `port_remove`, logs disconnect, and releases autopm if acquired.

## State and Persistence Behavior

State includes driver registration, per-driver dynamic USB IDs, and tty device registration for each port minor. Dynamic IDs persist only while the driver is loaded and are freed before unregister.

## Dependencies and Integration Points

The file depends on the USB serial core, USB dynamic-ID helpers, tty port registration, runtime PM, driver core bus APIs, and `usb_dynids_lock`. It bridges USB interface probing to tty device creation.

## Risks and Edge Cases

Risks include suspend/resume races if autopm acquisition fails, cleanup ordering when tty registration fails after `port_probe`, dynamic-ID duplication across usbserial and underlying usb_driver dynid lists, and freeing dynamic IDs under the global lock. Remove still calls `port_remove` if autopm get failed because no further PM callbacks will be made.

## Test Signals

Test driver register/deregister, port probe failure rollback, tty registration failure rollback, dynamic `new_id` show/store, suspend during probe/remove, disconnect during probe, and multi-port devices with correct minor attachment and removal logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ch341.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ch341.c

## Purpose

This driver supports Winchiphead/QinHeng CH341/CH340-family USB serial adapters in asynchronous serial mode. It programs vendor registers for baud, line control, modem control, flow control, break, and status, with quirks for limited devices. The complete 893-line source was read.

## Important APIs, Types, and Functions

Private state `struct ch341_private` stores lock-protected baud rate, MCR, MSR, LCR, quirk flags, chip version, and simulated-break end time. Major functions include `ch341_port_probe()`, `ch341_configure()`, `ch341_detect_quirks()`, `ch341_open()`, `ch341_close()`, `ch341_set_termios()`, `ch341_set_baudrate_lcr()`, `ch341_get_divisor()`, `ch341_set_flow_control()`, `ch341_break_ctl()`, `ch341_simulate_break()`, `ch341_tiocmset()`, `ch341_tiocmget()`, `ch341_read_int_callback()`, `ch341_update_status()`, and `ch341_reset_resume()`.

## Control Flow

Probe allocates private state, sets default 9600 8N1, configures the chip by reading version, sending serial-init, programming baud/LCR, and setting handshake, then probes break-register support to enable limited-prescaler and simulated-break quirks when needed. Open applies termios, submits the interrupt URB, reads initial modem status, and starts generic bulk I/O. Termios avoids redundant writes, computes LCR, clamps and rounds divisor fields for the 48 MHz clock, handles version-specific LCR register layout, updates DTR/RTS around B0 transitions, and writes flow-control mode. Interrupt callbacks decode four-byte status reports, update modem counters, notify DCD changes, and resubmit. Reset-resume reconfigures registers and restarts interrupt/status handling before generic resume.

## State and Persistence Behavior

Private state mirrors the desired UART settings and observed modem status. Hardware settings persist until reset; reset-resume explicitly restores them. Simulated break temporarily lowers baud and sends a NUL byte, then later restores `priv->baud_rate` and `priv->lcr`.

## Dependencies and Integration Points

The driver depends on the USB serial core, tty termios, serial modem-control conventions, unaligned helpers, jiffies scheduling for break simulation, and vendor control endpoint requests. It integrates with generic `tiocmiwait`, DCD hangup handling, and reset-resume.

## Risks and Edge Cases

Risks include device-family quirks detected via failed break-register reads, incorrect divisor rounding for marginal baud rates, version-dependent meaning of bit 7 in the divisor value, redundant control writes causing byte loss, simulated break corrupting incoming data and having fixed duration, and not checking all control-write failures in simple DTR/RTS paths.

## Test Signals

Test all listed USB IDs, version <0x30 and >=0x30 devices, limited-prescaler devices, baud range 46 to 3 Mbps, B0 and B0 recovery, CRTSCTS toggling, parity/word/stop settings, real and simulated break, modem status interrupts including DCD changes, reset-resume after bus reset, disconnect while interrupt URB is active, and line-discipline behavior under `INPCK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ch341.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/console.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/console.c

## Purpose

This file implements optional USB serial console support for built-in usbserial. It lets `console=ttyUSB<n>,...` use a USB serial port as the kernel console after the first suitable USB serial device appears. The complete 304-line source was read.

## Important APIs, Types, and Functions

Private global state is `struct usbcons_info usbcons_info`, which stores a magic field, break flag, and console port pointer. Main functions are `usb_console_setup()`, `usb_console_write()`, `usb_console_device()`, `usb_serial_console_init()`, `usb_serial_console_exit()`, and `usb_serial_console_disconnect()`. The console object is `usbcons` with name `ttyUSB`.

## Control Flow

`usb_serial_console_init()` registers the console only for minor 0 so console setup is deferred until a USB serial device exists. Setup parses baud/parity/bits/flow options, looks up the port by minor, obtains a runtime-PM reference, clears the tty pointer, increments the port count, creates a fake tty if the driver needs `set_termios`, calls the converter `open()` on first initialization, applies requested termios through the fake tty, marks the tty port initialized and console-owned, and returns with the serial disconnect mutex unlocked. Console writes check that the port still exists and is console-open, split output at LF boundaries, call the converter `write()` callback, and append CR after LF. Disconnect unregisters the console and drops the serial reference.

## State and Persistence Behavior

Console state is global and points to one usbserial port. The port's tty initialized and console flags persist while it is the active console. There is no persistent storage; command-line console options drive setup.

## Dependencies and Integration Points

The file depends on the console subsystem, tty core internals, USB serial lookup/reference handling, runtime PM, and converter driver `open`, `write`, and optional `set_termios` callbacks. It is compiled only when `USB_SERIAL_CONSOLE` is enabled.

## Risks and Edge Cases

Risks include unusual locking because setup exits by unlocking `serial->disc_mutex` acquired by lookup code, fake tty lifetime and module references, converter drivers not tolerating `tty == NULL` writes, console write during disconnect, CR/LF insertion changing byte stream semantics, and limited registration behavior for minors other than 0.

## Test Signals

Boot with `console=ttyUSB0` and multiple option strings, verify first-device console registration, converter open/set_termios with fake tty, printk output including newline CR insertion, disconnect while console active, runtime PM failures, and builds with `USB_SERIAL_CONSOLE=y` versus disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/cp210x.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/cp210x.c

## Purpose

This driver supports Silicon Labs CP210x USB-to-UART bridges and many products using those chips. It handles serial open/close, baud/framing/flow control, modem lines, break, embedded line-status events, transmit-empty queries, chip-family detection, firmware quirks, and optional GPIO registration. The complete 2201-line source was read.

## Important APIs, Types, and Functions

Global serial state `struct cp210x_serial_private` stores optional GPIO chip state, part number, firmware version, min/max speed, actual-rate policy, and quirk flags. Per-port state `struct cp210x_port_private` stores interface number, event-mode parser state, mutex-protected CRTSCTS/DTR/RTS booleans, and LSR. Major functions include `cp210x_attach()`, `cp210x_determine_type()`, `cp210x_init_max_speed()`, `cp210x_port_probe()`, `cp210x_open()`, `cp210x_close()`, `cp210x_set_termios()`, `cp210x_change_speed()`, `cp210x_set_flow_control()`, `cp210x_enable_event_mode()`, `cp210x_process_read_urb()`, `cp210x_tiocmset_port()`, `cp210x_tiocmget()`, `cp210x_break_ctl()`, and the GPIO family init functions for CP2104, CP2105, CP2108, and CP2102N.

## Control Flow

Attach allocates serial-private state, queries the part number, detects CP2102 event-mode and CP2102N flow-control quirks, sets speed limits, and initializes GPIO if supported. Port probe records the USB interface number. Open enables the UART with `CP210X_IFC_ENABLE`, applies termios, then starts generic bulk I/O; close stops I/O, purges queues, disables the UART, and clears event mode. Termios clamps/quantizes baud by chip family, writes baud and line-control registers, programs special XON/XOFF chars and `CP210X_SET_FLOW`, updates DTR/RTS around B0, and enables embedded event mode when input parity checking is enabled. Read URBs either pass data through or parse `0xec` escape sequences for LSR/MSR events and per-character error flags. GPIO code reads chip-specific configuration, masks alternate-function pins, emulates input mode for open-drain pins, and issues vendor latch reads/writes under runtime PM.

## State and Persistence Behavior

Serial and port-private structures persist for device and port lifetimes. Hardware UART state persists while enabled but is cleared by close and reset. Event-mode parser state persists across URBs. GPIO registration persists until disconnect/release and exposes kernel GPIO state backed by device latch registers.

## Dependencies and Integration Points

The driver depends on USB serial core, tty/termios, tty flip buffering, GPIO library when enabled, runtime PM for GPIO access, little-endian packed vendor structures, and many Silicon Labs vendor requests. It integrates with tty modem-control, `tx_empty`, generic throttle/unthrottle, generic `get_icount`, and gpiolib.

## Risks and Edge Cases

High-risk areas include the very large USB ID table, part-number and firmware probing failures, CP2102 counterfeit/no-event-mode behavior, CP2102N flow-control erratum, event-mode escape parser synchronization across URBs, `SET_FLOW` read-modify-write races with modem-line changes, GPIO alternate-function masking by package, open-drain input emulation, CP2105 break unsupported on interface 1, and close-time purge needed to avoid CP2108 hangs.

## Test Signals

Test representative CP2101/2/3/4/5/8/2N devices, unknown part fallback, firmware-version quirks, baud limits and actual-rate reporting, line-control matrix, CRTSCTS and IXON/IXOFF including special chars, B0 DTR/RTS transitions, embedded LSR events with parity/framing/overrun/break, `tx_empty` queue reads, break on CP2105 interfaces, GPIO get/set/direction/valid-mask for each GPIO-capable family, runtime PM during GPIO access, disconnect/release cleanup, and malformed event streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/cp210x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/cyberjack.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/cyberjack.c

## Purpose

This driver supports the REINER SCT cyberJack pinpad/e-com USB chipcard reader as a USB serial device. It implements device-specific framing around interrupt announcements, bulk-in reads, and segmented bulk-out writes. The complete 422-line source was read.

## Important APIs, Types, and Functions

Private state `struct cyberjack_private` contains a spinlock, `rdtodo`, a 320-byte write buffer, `wrfilled`, and `wrsent`. Main functions are `cyberjack_port_probe()`, `cyberjack_port_remove()`, `cyberjack_open()`, `cyberjack_close()`, `cyberjack_write()`, `cyberjack_write_room()`, `cyberjack_read_int_callback()`, `cyberjack_read_bulk_callback()`, and `cyberjack_write_bulk_callback()`.

## Control Flow

Port probe allocates state and immediately submits the interrupt-in URB. Open clears the bulk-out halt and resets read/write counters. User writes are accumulated until at least a three-byte header is present and the expected frame length (`len_hi:len_lo + 3`) has arrived; the first bulk-out chunk is then submitted and remaining chunks are sent by the write completion callback. Interrupt callbacks treat four-byte packets beginning with `0x01` as announcements of pending bulk-in data, add the announced length to `rdtodo`, and submit a read URB if none was pending. Bulk-read callbacks push data to tty, decrement `rdtodo`, and resubmit while bytes remain.

## State and Persistence Behavior

All state is per-port and protected by a spinlock. `rdtodo` tracks announced but unread bytes; `wrbuf`, `wrfilled`, and `wrsent` track an in-progress outgoing protocol frame. State resets on open and is freed on port removal.

## Dependencies and Integration Points

The driver depends on USB serial core URBs, tty flip buffering, write-URB free-bit handling, and softint notification. It exposes only basic serial write/read behavior, without termios or modem-control callbacks.

## Risks and Edge Cases

Risks include fixed local write-buffer size, dropping buffered data on overflow or submit failure, `write_room()` returning a constant FIXME value rather than true room, interrupt probe submission before open, `rdtodo` overflow handling, no deep validation of announced lengths, and close racing with callback resubmission.

## Test Signals

Exercise full and partial write frames, oversized write frame reset, multi-URB write completion, interrupt announcements with multiple reads, `rdtodo` overflow prevention, zero-length bulk reads, close/remove while URBs are active, and real reader command/response transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/cyberjack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/cypress_m8.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/cypress_m8.c

## Purpose

This driver supports Cypress M8 HID-to-serial firmware variants, including DeLorme Earthmate GPS, Cypress HID->COM adapters, FRWD, Powercom UPS, and Nokia CA-42 v2. It moves serial data over HID interrupt reports rather than conventional bulk endpoints. The complete 1206-line source was read.

## Important APIs, Types, and Functions

Private state `struct cypress_private` stores locks, chip type, statistics, command count, write FIFO, URB-in-use flag, read/write intervals, communication-health flag, line control, current status/config, throttle flags, packet format, unsafe-get-config flag, baud rate, and previous modem status. Important functions include `cypress_generic_port_probe()`, chip-specific probe wrappers, `cypress_open()`, `cypress_close()`, `cypress_serial_control()`, `analyze_baud_rate()`, `cypress_set_termios()`, `cypress_dtr_rts()`, `cypress_write()`, `cypress_send()`, `cypress_read_int_callback()`, `cypress_write_int_callback()`, throttle/unthrottle, and tty modem-control helpers.

## Control Flow

Generic probe verifies interrupt endpoints, allocates state and a 1024-byte FIFO, optionally resets configuration, chooses packet format by interrupt-out size, stores polling intervals, and sets drain delay. Earthmate probe forces packet format 1 and marks newer Earthmates unsafe for `GET_CONFIG`. Open clears endpoint halts, resets counters, sends pending line-control state, applies termios, fills and submits the interrupt-in URB. Writes enqueue data unless a line-control command is pending; `cypress_send()` formats either a command report or data report, marks the write URB busy, and submits interrupt-out. Read callbacks parse packet-format-specific status and byte counts, handle throttling, update modem counters and hangup on carrier loss, mark parity errors, push payload to tty, update statistics, and resubmit reads while communication remains healthy.

## State and Persistence Behavior

Per-port state persists until removal. `comm_is_ok` permanently stops new I/O after serious communication failures. `line_control`, `current_config`, and `baud_rate` mirror device settings. Statistics persist across an open session and can be logged on close through the `stats` module parameter. Module parameters `interval` and `unstable_bauds` influence runtime behavior.

## Dependencies and Integration Points

The driver depends on USB serial core, interrupt URBs, HID class `GET_REPORT`/`SET_REPORT` control messages, tty termios and flip buffers, kfifo, unaligned little-endian helpers, module parameters, and constants from `cypress_m8.h`. It integrates with tty modem-control ioctls, `tiocmiwait`, hangup semantics, throttling, and device-specific init termios for Earthmate.

## Risks and Edge Cases

Risks include devices that crash on `GET_CONFIG`, low-speed baud limitations, optional unstable baud override, interrupt interval sensitivity causing `comm_is_ok` shutdown, two packet formats with different count encodings, command reports interleaving with data writes, throttle leaving a read URB unsubmitted until unthrottle, carrier-loss hangup location, limited error reporting to one parity bit, and lockless updates of `write_urb_in_use` in callbacks.

## Test Signals

Test each supported chip type and packet format, low-speed baud rejection, Earthmate 4800 custom termios, unsafe `GET_CONFIG` devices, FRWD reset skip, line-control commands via DTR/RTS and B0, FIFO write room/chars-in-buffer, command/data write URB chaining, read status deltas and `TIOCMIWAIT`, carrier hangup, parity-error flagging, throttle/unthrottle resubmission, interval override, communication failure paths, and stats logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/cypress_m8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/cypress_m8.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/cypress_m8.h

## Purpose

This header defines the HID report requests, USB IDs, Cypress serial configuration request IDs, throttle flags, chip-type constants, and RS-232 status/control bit masks used by the Cypress M8 USB serial driver.

## Important APIs, Types, and Functions

Important constants are `HID_REQ_GET_REPORT`, `HID_REQ_SET_REPORT`, device IDs for DeLorme, Cypress, SAI, FRWD, Powercom, and Dazzle/Nokia CA-42, `CYPRESS_SET_CONFIG`, `CYPRESS_GET_CONFIG`, `THROTTLED`, `ACTUALLY_THROTTLED`, chip types `CT_EARTHMATE`, `CT_CYPHIDCOM`, `CT_CA42V2`, `CT_GENERIC`, control bits `CONTROL_DTR`, `CONTROL_RTS`, `CONTROL_RESET`, modem bits `UART_RI`, `UART_CD`, `UART_DSR`, `UART_CTS`, and `CYP_ERROR`.

## Control Flow

The header has no executable flow. `cypress_m8.c` uses these constants to select IDs, issue HID feature reports, encode outgoing line control, decode incoming modem status, and mark throttled read state.

## State and Persistence Behavior

No storage is owned by the header. Its constants define the in-memory and hardware protocol state stored in `struct cypress_private` and in Cypress HID report payloads.

## Dependencies and Integration Points

The header integrates directly with `cypress_m8.c` and indirectly with USB HID class control transfers and USB serial tty behavior.

## Risks and Edge Cases

Risks include adding new Cypress-based devices without updating all ID tables, confusing chip type with USB ID, one-bit `CYP_ERROR` ambiguity, and packet/status bit definitions needing to stay aligned with the firmware application notes.

## Test Signals

Compile coverage of the Cypress driver, USB ID matching for every defined vendor/product pair, report encoding/decoding tests for control and modem bits, and runtime validation that throttle and chip-type constants drive the expected code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/cypress_m8.h -->
