# subset-b-005446 Research

Grouped source research for USB4/Thunderbolt router, port, and XDomain support plus selected TTY build manifests and platform serial drivers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/usb4.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/usb4.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/usb4.c` implements the core USB4-specific Thunderbolt router and adapter helper layer. It wraps USB4 router operations, DROM/NVM access, wake and sleep programming, buffer credit discovery, DisplayPort resource arbitration, USB4 port configuration, sideband access, retimer management, lane margining, USB3 bandwidth allocation, DP bandwidth allocation mode, and PCIe extended encapsulation. The source was read as a complete 3147-line file for this report.

## Important APIs, Types, and Functions

Major router helpers include `usb4_switch_setup`, `usb4_switch_configuration_valid`, `usb4_switch_read_uid`, `usb4_switch_drom_read`, `usb4_switch_set_wake`, `usb4_switch_set_sleep`, `usb4_switch_credits_init`, `usb4_switch_query_dp_resource`, `usb4_switch_alloc_dp_resource`, `usb4_switch_dealloc_dp_resource`, and the router NVM functions `usb4_switch_nvm_sector_size`, `usb4_switch_nvm_read`, `usb4_switch_nvm_write`, `usb4_switch_nvm_authenticate`, and `usb4_switch_nvm_authenticate_status`.

Port-facing APIs include `usb4_switch_add_ports`, `usb4_switch_remove_ports`, `usb4_port_unlock`, `usb4_port_hotplug_enable`, `usb4_port_reset`, `usb4_port_configure`, `usb4_port_unconfigure`, `usb4_port_configure_xdomain`, `usb4_port_unconfigure_xdomain`, `usb4_port_sb_read`, `usb4_port_sb_write`, `usb4_port_router_offline`, `usb4_port_router_online`, `usb4_port_enumerate_retimers`, `usb4_port_clx_supported`, `usb4_port_asym_supported`, `usb4_port_asym_set_link_width`, and `usb4_port_asym_start`.

Retimer and diagnostics APIs are built on sideband transactions: `usb4_port_margining_caps`, `usb4_port_hw_margin`, `usb4_port_sw_margin`, `usb4_port_sw_margin_errors`, `usb4_port_retimer_set_inbound_sbtx`, `usb4_port_retimer_unset_inbound_sbtx`, `usb4_port_retimer_is_last`, `usb4_port_retimer_is_cable`, `usb4_port_retimer_nvm_*`. Adapter bandwidth and protocol helpers include `usb4_usb3_port_max_link_rate`, `usb4_usb3_port_allocated_bandwidth`, `usb4_usb3_port_allocate_bandwidth`, `usb4_usb3_port_release_bandwidth`, `usb4_dp_port_*`, and `usb4_pci_port_set_ext_encapsulation`. Key local machinery is `usb4_native_switch_op`, `__usb4_switch_op`, `usb4_port_wait_for_bit`, `usb4_port_sb_op`, `usb3_bw_to_mbps`, and `mbps_to_usb3_bw`.

## Control Flow

Router operations flow through `__usb4_switch_op`: validate that TX/RX data is at most `USB4_DATA_DWORDS`, optionally proxy through `tb_cm_ops->usb4_switch_op`, then fall back to native config-space operation. The native path writes metadata and TX data to router registers, asserts the operation-valid bit, waits for completion, checks operation-not-supported and status fields, and reads metadata/RX data back.

Router setup starts with capability/config reads, detects whether the upstream link is USB4 or Thunderbolt 3, enables USB3 and PCIe tunneling according to ACPI policy and parent adapter availability, optionally leaves internal xHCI enabled, then `usb4_switch_configuration_valid` sets the configuration-valid bit and waits for completion. Wake and sleep paths program router and port registers and feed wake status into PM core.

NVM and DROM reads use `tb_nvm_read_data` callbacks that translate byte offsets into USB4 operation metadata. NVM writes set the write offset, stream blocks through `tb_nvm_write_data`, and authenticate with special handling for expected disconnect/timeouts during router power cycling. Retimer NVM mirrors this through sideband target operations.

Sideband register access writes command metadata into USB4 port config space, waits for `PND` to clear, maps no-response/response-code bits to Linux errno values, and optionally reads/writes up to 16 data dwords. Higher-level retimer, router-offline, lane-margining, and CLx/asymmetric-link helpers all layer on top of this sideband primitive.

USB3 bandwidth allocation obtains CM ownership with the CMR/HCA handshake, reads consumed and allocated bandwidth registers, converts between scaled USB3 register units and Mb/s, clamps allocations so consumed bandwidth is not removed, and releases to at least 900 Mb/s. DP bandwidth allocation validates USB4 DP-IN support, programs CM ID, group ID, non-reduced link parameters, granularity, estimated/allocated bandwidth, acknowledges DPCD requests, and waits for the DP request bit to clear.

## State and Persistence Behavior

The file persists state through `struct tb_switch` and `struct tb_port` fields such as `link_usb4`, `credit_allocation`, credit limits, `port->usb4`, XDomain link type, `port->bonded`, and adapter-specific maximum bandwidth. Hardware state is persisted in USB4 router, adapter, sideband, retimer, NVM, DP, USB3, and PCIe registers. NVM write/authentication paths modify firmware storage and may power cycle routers or retimers. There is no filesystem persistence.

## Dependencies and Integration Points

The implementation depends on Thunderbolt core types and helpers in `tb.h`, sideband register definitions in `sb_regs.h`, config-space accessors (`tb_sw_read`, `tb_sw_write`, `tb_port_read`, `tb_port_write`), NVM streaming helpers (`tb_nvm_read_data`, `tb_nvm_write_data`), ACPI policy helpers, PM wake APIs, retimer scanning, topology helpers, and DisplayPort/USB3/PCIe adapter register definitions. It is consumed by the Thunderbolt connection manager, tunnel creation logic, retimer/NVM sysfs flows, bandwidth management, XDomain setup, and USB4 port device registration.

## Risks and Edge Cases

The operation wrappers are tightly coupled to register bit layouts and operation completion timing. Incorrect metadata length/offset packing can corrupt NVM or read wrong data. Authentication intentionally treats several transport errors as success because hardware disappears during power cycling; callers must read authentication status before any other router operation. Sideband calls can time out or return `-ENODEV` for missing retimers, and the first inbound SBTX command has a special retry allowance. Bandwidth conversion uses scale selection and rounding; bad values can over- or under-allocate isochronous capacity. Many helpers silently return unsupported for non-USB4 or non-DP-IN ports, so callers need explicit capability checks.

## Test Signals

Useful signals include USB4 router enumeration with USB3/PCIe/DP tunneling enabled and disabled by ACPI policy; suspend/resume wake tests for connect, disconnect, USB4, USB3, PCIe, and DP wake bits; router and retimer NVM read/write/authentication with power-cycle status checks; sideband timeout and missing-retimer coverage; retimer enumeration and offline/online transitions; USB3 bandwidth allocation/release with active isochronous load; DP bandwidth allocation mode request/ack tests; lane bonding/asymmetric width transitions; and kernel build coverage for Thunderbolt with USB4 enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/usb4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/usb4_port.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/usb4_port.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/usb4_port.c` creates the Linux device model representation for USB4 ports. It exposes sysfs attributes for link state and service-mode retimer access, binds USB4 port devices to Type-C connector devices through the component framework, supports firmware-node matching between USB3 and USB4 ports, and provides resume handling for ports left in offline mode. The source was read as a complete 366-line file for this report.

## Important APIs, Types, and Functions

Public entry points are `usb4_usb3_port_match`, `usb4_port_device_add`, `usb4_port_device_remove`, `usb4_port_device_resume`, and the exported `usb4_port_device_type`. Important local functions include `connector_bind`, `connector_unbind`, `link_show`, `offline_show`, `offline_store`, `rescan_store`, `service_attr_is_visible`, `usb4_port_offline`, and `usb4_port_online`.

Sysfs attributes are `link`, `offline`, and `rescan`. `link` is always visible and reports `usb4`, `tbt`, or `none`; `offline` and `rescan` are visible only when `usb4->can_offline` is set. The component operations create reciprocal sysfs links named `connector` and by USB4 port device name.

## Control Flow

`usb4_port_device_add` allocates `struct usb4_port`, initializes an embedded `struct device`, registers it below the owning switch device, adds the connector component, marks downstream ports wake-capable, and enables runtime PM with autosuspend. Removal deletes the component and unregisters the device.

`offline_store` parses a boolean, takes a runtime PM reference, locks the Thunderbolt domain, rejects offline mode when a remote router is connected, powers retimers through ACPI, asks the USB4 router sideband path to go offline, scans retimers, and records `usb4->offline`. Clearing offline mode brings the router online, powers retimers down, and removes discovered retimer devices. `rescan_store` requires the port to already be offline and then refreshes the retimer list.

`link_show` locks the domain and derives link type from upstream switch state, remote switch state, or attached XDomain state. `usb4_usb3_port_match` is designed for component matching: it follows the USB3 firmware node's `usb4-host-interface` reference, compares it against the NHI device fwnode, reads `usb4-port-number`, and compares it with `usb4_port_index`.

## State and Persistence Behavior

State is stored in the allocated `struct usb4_port` and linked from `struct tb_port->usb4`. The important persistent-in-memory fields are `port`, `offline`, `can_offline`, runtime PM state, wake capability, and the registered device lifetime. Hardware-side state changes happen through USB4 router offline/online sideband commands and ACPI retimer power calls. There is no disk persistence.

## Dependencies and Integration Points

The file depends on Thunderbolt core structures in `tb.h`, runtime PM, the component framework, firmware-node property APIs, sysfs, ACPI retimer power helpers, retimer scan/remove helpers, USB4 sideband helpers from `usb4.c`, and Type-C connector components. It integrates with switch enumeration through `usb4_switch_add_ports`, with USB3 port binding through `usb4_usb3_port_match`, and with userspace through `/sys/bus/thunderbolt/devices/.../usb4_port*`.

## Risks and Edge Cases

Offline mode is intentionally limited to disconnected ports; forcing it while a remote switch exists returns `-EBUSY`. ACPI retimer power sequencing must stay balanced across offline failures and online transitions. `usb4_port_device_add` calls `device_unregister` after a component-add failure but still returns the allocated pointer, so callers rely on the current behavior and lifetime conventions. Sysfs operations must take the Thunderbolt domain lock because topology and XDomain pointers can change while userspace reads.

## Test Signals

Useful signals include creation/removal of `usb4_port*` devices during USB4 router enumeration; reciprocal connector sysfs links; `link` values for no device, USB4 router, TBT router, and XDomain connections; offline/rescan behavior with retimers present and absent; rejection of offline mode on connected ports; runtime PM autosuspend/resume preserving offline state; and firmware-node matching with USB3 component binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/usb4_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/xdomain.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/xdomain.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/xdomain.c` implements Thunderbolt XDomain host-to-host discovery and service enumeration. It exchanges UUID, link-state, lane-bonding, properties, and properties-changed messages over the Thunderbolt control channel; creates `thunderbolt_xdomain` devices; enumerates remote service devices from property directories; exposes sysfs attributes; manages XDomain DMA path HopIDs; and provides registration APIs for XDomain service drivers and protocol handlers. The source was read as a complete 2597-line file for this report.

## Important APIs, Types, and Functions

Public APIs include `tb_is_xdomain_enabled`, `tb_xdomain_request`, `tb_xdomain_response`, `tb_register_protocol_handler`, `tb_unregister_protocol_handler`, `tb_register_service_driver`, `tb_unregister_service_driver`, `tb_xdomain_alloc`, `tb_xdomain_add`, `tb_xdomain_remove`, `tb_xdomain_lane_bonding_enable`, `tb_xdomain_lane_bonding_disable`, `tb_xdomain_alloc_in_hopid`, `tb_xdomain_alloc_out_hopid`, `tb_xdomain_release_in_hopid`, `tb_xdomain_release_out_hopid`, `tb_xdomain_enable_paths`, `tb_xdomain_disable_paths`, `tb_xdomain_find_by_uuid`, `tb_xdomain_find_by_link_depth`, `tb_xdomain_find_by_route`, `tb_xdomain_handle_request`, `tb_register_property_dir`, `tb_unregister_property_dir`, `tb_xdomain_init`, and `tb_xdomain_exit`.

Key local mechanisms are the `XDOMAIN_STATE_*` handshake states, `struct xdomain_request_work`, `xdomain_lock`, `xdomain_property_dir`, `protocol_handlers`, `tb_xdp_fill_header`, `tb_xdp_handle_error`, `tb_xdp_*_request/response` helpers, `update_property_block`, `tb_xdp_handle_request`, `populate_properties`, `enumerate_services`, `tb_xdomain_state_work`, and `tb_xdomain_properties_changed`.

## Control Flow

Outbound request/response paths allocate `struct tb_cfg_request`, install matching/copy callbacks that verify route and UUID, submit through `tb_cfg_request_sync` or `tb_cfg_request`, and translate control-layer errors to Linux errno values. XDomain discovery protocol helpers build typed packets with `tb_xdp_fill_header`, send them as `TB_CFG_PKG_XDOMAIN_REQ` or `RESP`, and parse returned error responses.

Inbound control packets enter `tb_xdomain_handle_request`. Packets with the XDomain discovery UUID are scheduled to process asynchronously in `tb_xdp_handle_request`; packets for other UUIDs are offered to registered protocol handlers under `xdomain_lock`. The work handler resolves the route, finds the matching XDomain, updates local property blocks, and responds to UUID, properties, properties-changed, link-state status, and link-state change requests.

Discovery is a delayed-work state machine. It starts in `INIT`, optionally reads the remote UUID, optionally probes link status and negotiates lane bonding, sends a properties-changed notification, fetches remote properties, parses them, adds the XDomain device, and enumerates service child devices. Retryable failures reschedule the same state; non-retryable discovery failures move to `ERROR` and stop handshake work.

Service enumeration walks the remote property directory. Missing services are unregistered, existing service keys are retained, and new `struct tb_service` devices are allocated, populated from protocol properties, assigned IDs from `ida`, registered on `tb_bus_type`, and made discoverable through modalias and sysfs attributes.

## State and Persistence Behavior

Important state lives in `struct tb_xdomain`: local and remote UUIDs, route, local/remote HopID limits, link speed and width, lane-bonding flags, work items, retry counters, property blocks, parsed remote properties, service IDA, HopID IDAs, vendor/device IDs, names, and device registration state. Global mutable state includes the local property template, its generation counter, the protocol handler list, and the `xdomain` module parameter. State is in memory only, but it controls hardware link width, lane adapter bonding, and approved DMA paths. Remote property changes are represented by generation counters and uevents, not by filesystem persistence.

## Dependencies and Integration Points

The file depends on Thunderbolt control-channel request APIs, topology lookup, `tb_property` formatting/parsing, `tb_bus_type`, runtime PM, workqueues, UUID helpers, IDA allocation, PM sleep callbacks, link speed/width helpers, lane bonding helpers, debugfs hooks, and domain path approval/disconnection callbacks. It integrates with service drivers through `tb_register_service_driver`, with service advertisement through `tb_register_property_dir`, with cross-domain data protocols through `tb_register_protocol_handler`, and with userspace through `thunderbolt_xdomain` and `thunderbolt_service` sysfs devices and modalias uevents.

## Risks and Edge Cases

The handshake is asynchronous and route-based, so stale packets, unplug races, or UUID changes can cause retries, device replacement, or `is_unplugged` handling. Properties are length-delimited and chunked; offset, generation, and maximum-length validation are critical to avoid malformed remote input. Lock ordering requires `xdomain_lock` before `xd->lock`. Lane bonding has a split-brain avoidance rule based on UUID ordering; failures intentionally fall back to unbonded operation. HopID allocation must respect local and remote maximums. Service enumeration must handle partial allocation failures without leaving broken child devices.

## Test Signals

Useful signals include host-to-host attach and detach; XDomain disabled by module parameter or ACPI policy; UUID request/response retries and loopback detection; property block parsing, generation updates, and properties-changed notifications; service modalias uevents and driver binding; lane-bonding negotiation with lower and higher UUID sides; suspend/resume restarting the handshake; HopID allocation exhaustion and release; DMA path enable/disable for XDomain services; and malformed XDomain packet length/UUID/route rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/xdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/tty/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/Kconfig` defines the top-level Linux TTY configuration menu. It controls whether the TTY core, virtual terminals, PTYs, line disciplines, non-standard serial drivers, platform TTY drivers, serdev, HVC, and selected console options are buildable. The source was read as a complete 429-line file for this report.

## Important APIs, Types, and Functions

This is Kconfig data, not C code. Important symbols include `TTY`, `VT`, `CONSOLE_TRANSLATIONS`, `VT_CONSOLE`, `VT_CONSOLE_SLEEP`, `VT_HW_CONSOLE_BINDING`, `UNIX98_PTYS`, `LEGACY_PTYS`, `LEGACY_PTY_COUNT`, `LEGACY_TIOCSTI`, `LDISC_AUTOLOAD`, `SERIAL_NONSTANDARD`, `MOXA_INTELLIO`, `MOXA_SMARTIO`, `SYNCLINK_GT`, `N_HDLC`, `PPC_EPAPR_HV_BYTECHAN`, `PPC_EARLY_DEBUG_EHV_BC`, `PPC_EARLY_DEBUG_EHV_BC_HANDLE`, `GOLDFISH_TTY`, `GOLDFISH_TTY_EARLY_CONSOLE`, `IPWIRELESS`, `N_GSM`, `NOZOMI`, `MIPS_EJTAG_FDC_TTY`, `MIPS_EJTAG_FDC_EARLYCON`, `MIPS_EJTAG_FDC_KGDB`, `MIPS_EJTAG_FDC_KGDB_CHAN`, `NULL_TTY`, `NULL_TTY_DEFAULT_CONSOLE`, `VCC`, and `RPMSG_TTY`.

## Control Flow

Kconfig evaluation gates the entire file behind `if TTY` after the top-level `TTY` boolean. It sources `drivers/tty/serial/Kconfig`, later sources `drivers/tty/hvc/Kconfig`, closes `endif # TTY`, and then sources `drivers/tty/serdev/Kconfig`. Dependencies and `select` statements determine which objects the TTY Makefile can build and which subsystems are automatically enabled, such as `INPUT` for `VT`, `FW_LOADER` for Moxa Intellio, `EPAPR_PARAVIRT` for ePAPR byte channel, `SERIAL_CORE` and `SERIAL_CORE_CONSOLE` for Goldfish TTY, and `SERIAL_EARLYCON` for Goldfish early console.

## State and Persistence Behavior

The file persists build-time configuration in `.config`. Runtime defaults are indirectly affected by symbols such as `LEGACY_TIOCSTI` and `LDISC_AUTOLOAD`, whose help text notes sysctl-controlled runtime behavior initialized from Kconfig defaults. No runtime state is owned by this file.

## Dependencies and Integration Points

This manifest integrates with `drivers/tty/Makefile`, architecture symbols (`PPC`, `S390`, `MIPS_CDMM`, `SUN_LDOMS`), bus/subsystem symbols (`PCI`, `PCMCIA`, `NETDEVICES`, `RPMSG`, `GOLDFISH`, `XEN` through HVC), and nested Kconfig files for serial, HVC, and serdev. It controls whether source files such as `amiserial.c`, `ehv_bytechan.c`, and `goldfish.c` can be built through their corresponding symbols.

## Risks and Edge Cases

Because `TTY` is default-on but optional for `EXPERT`, disabling it removes core terminal and serial infrastructure and blocks many dependent drivers. `LEGACY_TIOCSTI` and `LDISC_AUTOLOAD` are security-sensitive defaults. Several platform drivers have narrow dependencies, so missing architecture or bus symbols can make drivers disappear from configuration menus. `SYNCLINK_GT` depends on `BROKEN`, preventing ordinary builds despite its prompt.

## Test Signals

Useful signals include `olddefconfig` and `menuconfig` coverage for TTY enabled and disabled; build matrix checks for PTY, VT, HVC, Goldfish, ePAPR byte channel, MIPS FDC, RPMSG, and null TTY options; verification that selected dependencies appear in `.config`; and boot tests confirming `/dev/tty`, `/dev/ptmx`, virtual consoles, and selected platform TTY devices appear only when their symbols are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tty/Makefile

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/Makefile` maps TTY-related Kconfig symbols to built-in or modular kernel objects. It is the top-level build manifest for the TTY core, line disciplines, virtual terminal subtree, serial subtree, HVC subtree, serdev, and selected TTY device drivers. The source was read as a complete 31-line file for this report.

## Important APIs, Types, and Functions

This is kbuild data. Important object mappings include `CONFIG_TTY` to core files such as `tty_io.o`, `n_tty.o`, `tty_ioctl.o`, `tty_ldisc.o`, `tty_buffer.o`, `tty_port.o`, `tty_mutex.o`, `tty_ldsem.o`, `tty_baudrate.o`, `tty_jobctrl.o`, and `n_null.o`; PTY symbols to `pty.o`; line disciplines to `n_hdlc.o` and `n_gsm.o`; and platform drivers such as `CONFIG_AMIGA_BUILTIN_SERIAL` to `amiserial.o`, `CONFIG_PPC_EPAPR_HV_BYTECHAN` to `ehv_bytechan.o`, and `CONFIG_GOLDFISH_TTY` to `goldfish.o`.

## Control Flow

kbuild evaluates `obj-y`, `obj-m`, and `obj-$(CONFIG_*)` assignments. The `vt/`, `serial/`, `serdev/`, and `ipwireless/` subdirectories are descended into according to their object assignments, while `hvc/` is entered only when `CONFIG_HVC_DRIVER` is enabled. Core TTY files are compiled only when `CONFIG_TTY` is true.

## State and Persistence Behavior

The Makefile has no runtime state. Its persistent effect is in build artifacts: which objects are linked into `vmlinux`, built as modules, or omitted based on `.config`.

## Dependencies and Integration Points

It integrates with `drivers/tty/Kconfig`, nested subtree Makefiles, and the kernel kbuild system. It is the build bridge for the researched TTY source files: `amiserial.o`, `ehv_bytechan.o`, `goldfish.o`, plus HVC files through `drivers/tty/hvc/Makefile`.

## Risks and Edge Cases

Multiple symbols map to `pty.o`, so both Unix98 and legacy PTY configurations share implementation. `obj-y += vt/` and `obj-y += serial/` always descend into subdirectories, leaving their internal Makefiles/Kconfig to decide object inclusion. Build failures can occur if Kconfig dependencies allow an object whose architecture-specific headers or APIs are unavailable.

## Test Signals

Useful signals include `make drivers/tty/` under representative configs; module-vs-built-in checks for tristate drivers; verification that `CONFIG_TTY=n` omits core TTY objects; and build coverage for `CONFIG_AMIGA_BUILTIN_SERIAL`, `CONFIG_PPC_EPAPR_HV_BYTECHAN`, `CONFIG_GOLDFISH_TTY`, `CONFIG_HVC_DRIVER`, and selected line disciplines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/amiserial.c -->
# sources/distributed-fs/ceph-client/drivers/tty/amiserial.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/amiserial.c` is the serial TTY and optional console driver for the Amiga built-in serial port. It adapts legacy 16550-style serial driver concepts to Amiga custom chip registers and CIA modem-control bits, registers one `ttyS` minor at 64, handles RX/TX/status interrupts, and provides termios, modem-control, ioctl, proc, and console operations. The source was read as a complete 1665-line file for this report.

## Important APIs, Types, and Functions

The central type is `struct serial_state`, containing `struct tty_port`, transmit `circ_buf`, `async_icount`, baud/divisor state, status masks, timeout, interrupt-enable emulation, modem-control bits, and high-priority XON/XOFF character state. Driver globals include `serial_driver`, `serial_state`, and `current_ctl_bits`.

Important interrupt and data-path functions are `receive_chars`, `transmit_chars`, `check_modem_status`, `ser_vbl_int`, `ser_rx_int`, and `ser_tx_int`. TTY operations include `rs_open`, `rs_close`, `rs_write`, `rs_put_char`, `rs_flush_chars`, `rs_write_room`, `rs_chars_in_buffer`, `rs_flush_buffer`, `rs_ioctl`, `rs_set_termios`, `rs_stop`, `rs_start`, `rs_hangup`, `rs_break`, `rs_send_xchar`, `rs_wait_until_sent`, `rs_tiocmget`, `rs_tiocmset`, `rs_get_icount`, `set_serial_info`, and `get_serial_info`. Probe/remove and console functions are `amiga_serial_probe`, `amiga_serial_remove`, `serial_console_write`, and `amiserial_console_init`.

## Control Flow

Probe allocates a one-line TTY driver, initializes `serial_state`, links the `tty_port`, registers the driver, requests Amiga TX and RX IRQs, disables and clears pending hardware interrupts, configures CIA modem-control directions, and stores driver data. Open links the tty to the single port, calls `rs_startup`, allocates the TX page buffer, clears RX state, requests the vertical blank IRQ for modem-status polling, enables RX/TX interrupt sources, asserts DTR/RTS according to baud, programs speed, and blocks until carrier if required.

RX IRQs call `receive_chars`, which reads `amiga_custom.serdatr`, decodes break and overrun status, updates counters, applies termios ignore/read masks, inserts flip-buffer characters, and pushes to the TTY layer. TX IRQs call `transmit_chars`, prioritizing `x_char`, then circular-buffer bytes, disabling transmit interrupts when empty or stopped and waking writers below `WAKEUP_CHARS`. The vertical blank IRQ periodically polls DCD/CTS/DSR, updates counters, wakes modem waiters, handles carrier hangup/open wakeups, and enforces CTS hardware flow control.

Termios changes recompute data framing, baud divisor, timeout, status masks, carrier checking, CTS flow, and hardware SERPER register values. Close disables RX, waits for transmitter drain, shuts down interrupts and buffers, optionally drops DTR/RTS, flushes line discipline state, and completes TTY close. Console writes disable TX interrupt temporarily, emit CR before LF, poll for transmit-ready, and restore interrupt enable state.

## State and Persistence Behavior

Runtime state is kept in the single static `serial_state`, including transmit buffer pointers, counters, modem-control bits, baud divisor, masks, and TTY port lifetime. Hardware-visible state is stored in Amiga custom registers (`serdat`, `serdatr`, `serper`, `intena`, `intreq`, `adkcon`) and CIA port A direction/data bits. No data persists across driver unload or reboot.

## Dependencies and Integration Points

The driver depends on the TTY core, `tty_port`, flip buffers, serial ioctl structures, circ-buffer helpers, Amiga architecture headers (`amigahw.h`, `amigaints.h`, IRQ/setup headers), platform driver probing, optional `CONFIG_SERIAL_CONSOLE`, and proc support via `tty_operations.proc_show`. It is built through `CONFIG_AMIGA_BUILTIN_SERIAL` from the TTY Makefile and aliases `platform:amiga-serial`.

## Risks and Edge Cases

The implementation uses local interrupt disabling around shared state instead of fine-grained locks, reflecting its single-port hardware model. The vertical blank IRQ is used for modem-status polling, so status latency depends on that interrupt. Carrier and CTS bits are active-low in CIA registers, which makes control logic easy to invert accidentally. `TIOCMIWAIT` must handle signals and modem counter races. Baud divisor fallback behavior preserves old termios or falls back to 9600 when invalid. Console output directly touches hardware and temporarily masks TX interrupts.

## Test Signals

Useful signals include Amiga or emulator boot showing `ttyS0 is the amiga builtin serial port`; open/close with carrier-required and `CLOCAL` modes; RX break/overrun counter behavior; TX buffering and `tty_wakeup`; CTS/RTS flow control; `TIOCMGET`, `TIOCMSET`, `TIOCGICOUNT`, `TIOCMIWAIT`, and `TIOCSERGETLSR`; baud and parity termios changes; `/proc/tty/driver` serial info; suspend-free module probe/remove paths; and serial console output with newline CRLF conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/amiserial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ehv_bytechan.c -->
# sources/distributed-fs/ceph-client/drivers/tty/ehv_bytechan.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/ehv_bytechan.c` implements TTY, console, and optional early udbg support for ePAPR hypervisor byte-channel devices on PowerPC. It exposes each device-tree byte channel as a `/dev/ttyEHV*` TTY, uses the `/chosen/stdout` byte channel as the kernel console, and sends/receives bytes through ePAPR hypercalls. The source was read as a complete 820-line file for this report.

## Important APIs, Types, and Functions

The main type is `struct ehv_bc_data`, holding device pointer, `tty_port`, hypervisor handle, RX/TX IRQs, a spinlock-protected transmit circular buffer, and TX interrupt enable state. Important globals are `bcs`, `stdout_bc`, `stdout_irq`, and `ehv_bc_driver`.

Important helpers include `find_console_handle`, `local_ev_byte_channel_send`, `enable_tx_interrupt`, `disable_tx_interrupt`, optional `udbg_init_ehv_bc`, `ehv_bc_console_write`, `ehv_bc_console_init`, `ehv_bc_tty_rx_isr`, `ehv_bc_tx_dequeue`, `ehv_bc_tty_tx_isr`, `ehv_bc_tty_write`, `ehv_bc_tty_open`, `ehv_bc_tty_close`, `ehv_bc_tty_write_room`, `ehv_bc_tty_throttle`, `ehv_bc_tty_unthrottle`, `ehv_bc_tty_hangup`, `ehv_bc_tty_port_activate`, `ehv_bc_tty_port_shutdown`, `ehv_bc_tty_probe`, and `ehv_bc_init`.

## Control Flow

Console init runs early, locates the device-tree stdout node if it is compatible with `epapr,hv-byte-channel`, reads its interrupt and `hv-handle`, adds it as the preferred `ttyEHV` console, and registers a console that spins on hypervisor send until output is accepted. Optional udbg setup verifies the configured handle with `ev_byte_channel_poll`, installs a putc hook, and emits early output before the normal console/TTY driver.

Driver init counts compatible nodes, allocates the `bcs` array, allocates/registers a dynamic TTY driver, and registers the platform driver. Probe reads each node's `hv-handle`, assigns line 0 to stdout and increasing indices to other byte channels, maps RX/TX IRQs, initializes a `tty_port`, and registers the TTY device.

TTY open delegates to `tty_port_open`. Port activation installs RX and TX IRQ handlers and disables TX IRQ until buffered output needs it. Writes copy bytes into the circular buffer under spinlock, then call `ehv_bc_tx_dequeue`, which sends chunks of up to `EV_BYTE_CHANNEL_MAX_BYTES` through hypercalls and enables TX IRQ when the hypervisor buffer is full. RX IRQs poll available bytes, reserve flip-buffer room, receive chunks from the byte channel, insert them into the TTY flip buffer, and push. Throttle/unthrottle disable and enable RX IRQs.

## State and Persistence Behavior

Per-channel state persists in `bcs[]` for the lifetime of the boot: hypervisor handles, mapped IRQs, `tty_port` state, TX buffer head/tail, and interrupt-enable tracking. Console state persists in `stdout_bc` and the registered `console`. The hypervisor owns the actual byte-channel queues. No filesystem-backed state is maintained.

## Dependencies and Integration Points

The driver depends on PowerPC ePAPR hypercall APIs (`ev_byte_channel_send`, `receive`, `poll`), Open Firmware device-tree parsing, IRQ mapping, TTY core, console subsystem, `tty_port`, flip buffers, circ-buffer helpers, optional PowerPC udbg, and the platform bus. Kconfig requires `PPC_EPAPR_HV_BYTECHAN` and selects `EPAPR_PARAVIRT`; early debug support uses `PPC_EARLY_DEBUG_EHV_BC`.

## Risks and Edge Cases

Hypervisor send requires at least the maximum byte-channel buffer size, so short writes are copied and padded locally. TX IRQ enable/disable is tracked manually because IRQ APIs are reference counted. RX throttling disables the Linux IRQ while the hypervisor may continue queueing data. `ehv_bc_tx_dequeue` advances the tail when the hypervisor accepts bytes or returns `EV_EAGAIN` with a valid partial length, so return-code semantics are important. The driver has no remove path and is initialized with `device_initcall`, matching platform lifetime assumptions.

## Test Signals

Useful signals include device-tree boots with and without `epapr,hv-byte-channel`; console selection through `/chosen/stdout`; optional udbg handle mismatch warning; `/dev/ttyEHV0` assigned to stdout and additional byte channels assigned increasing indices; RX/TX interrupt operation under sustained input/output; throttle/unthrottle behavior under TTY buffer pressure; TX IRQ only enabled when buffered output remains; and hypervisor `EV_EAGAIN` paths for full byte-channel queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ehv_bytechan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/goldfish.c -->
# sources/distributed-fs/ceph-client/drivers/tty/goldfish.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/goldfish.c` implements the TTY, console, and early-console driver for the Goldfish virtual platform. It exposes MMIO-backed emulator TTY devices as `/dev/ttyGF*`, supports legacy Goldfish virtual-address I/O and newer Ranchu DMA/physical-address I/O, handles interrupts for incoming data, and registers per-line consoles. The source was read as a complete 472-line file for this report.

## Important APIs, Types, and Functions

The main type is `struct goldfish_tty`, containing `tty_port`, spinlock, MMIO base, IRQ, console, device pointer, and device version. Key globals are `goldfish_tty_driver`, `goldfish_tty_line_count`, `goldfish_tty_current_line_count`, `goldfish_ttys`, and `goldfish_tty_lock`.

Important functions include `do_rw_io`, `goldfish_tty_rw`, `goldfish_tty_do_write`, `goldfish_tty_interrupt`, `goldfish_tty_activate`, `goldfish_tty_shutdown`, `goldfish_tty_open`, `goldfish_tty_close`, `goldfish_tty_hangup`, `goldfish_tty_write`, `goldfish_tty_write_room`, `goldfish_tty_chars_in_buffer`, `goldfish_tty_console_write`, `goldfish_tty_console_setup`, `goldfish_tty_create_driver`, `goldfish_tty_delete_driver`, `goldfish_tty_probe`, `goldfish_tty_remove`, `gf_earlycon_setup`, and the platform driver/of-match declarations.

## Control Flow

Probe maps the MMIO resource, gets the IRQ, assigns a line from platform ID or the current count, creates the shared TTY driver on the first device, initializes per-line port state, reads the device version, sets a 32-bit DMA mask for Ranchu-style devices, disables interrupts, requests the IRQ, registers the TTY device, registers a per-line console, and stores driver data. Remove unregisters the console and TTY device, unmaps MMIO, frees the IRQ, destroys the port, and deletes the shared driver when the last line is removed.

Writes flow through `goldfish_tty_rw`. Version 0 devices pass virtual addresses to MMIO registers. Version > 0 devices split the buffer by page, DMA-map each chunk, program data pointer and length registers, issue read/write commands, and unmap after completion. RX interrupts read `BYTES_READY`, reserve flip-buffer space, command a device read into the prepared buffer, and push the flip buffer. Port activation and shutdown enable/disable device interrupts with MMIO commands.

Console writes reuse the same write path by console index. Early console setup installs a UART-console write shim that writes characters directly to the mapped MMIO address for `google,goldfish-tty`.

## State and Persistence Behavior

Driver state is kept in the global `goldfish_ttys` array and per-device `struct goldfish_tty`: port state, MMIO base, IRQ, console, version, and device pointer. Global line count controls allocation and lifetime of the shared TTY driver. Hardware state is in Goldfish MMIO registers for data pointer, length, command, interrupt enable, bytes-ready, and version. There is no persistent storage.

## Dependencies and Integration Points

The driver depends on the platform bus, OF matching for `google,goldfish-tty`, Goldfish MMIO helpers (`gf_ioread32`, `gf_iowrite32`, `gf_write_ptr`), DMA mapping APIs, TTY core, `tty_port`, flip buffers, console and earlycon infrastructure, IRQ handling, and serial core console helpers. It is selected by `CONFIG_GOLDFISH_TTY`; early console is controlled by `CONFIG_GOLDFISH_TTY_EARLY_CONSOLE`.

## Risks and Edge Cases

The driver creates the shared TTY driver lazily on the first probed device and deletes it when the last device is removed, so line-count accounting must remain balanced on all probe failures. Ranchu DMA mode assumes 32-bit DMA addressing and splits transfers at page boundaries. `goldfish_tty_chars_in_buffer` returns `BYTES_READY`, which is receive-side device state rather than pending TX bytes. The reported maximum write room is a fixed large value because the emulator accepts command-buffer writes. Console writes depend on the per-line device already being probed unless earlycon is used.

## Test Signals

Useful signals include Goldfish/Ranchu boot with `ttyGF*` devices; IRQ-driven input into the TTY flip buffer; writes in legacy version 0 and DMA version > 0 modes; DMA mapping failure handling; console registration per probed line; earlycon output for `google,goldfish-tty`; probe failure unwinding for IRQ, DMA mask, and TTY registration errors; and remove/unregister behavior across multiple lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/goldfish.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/hvc/Kconfig` defines configuration options for hypervisor virtual console infrastructure and backend drivers. It covers generic HVC support, IRQ support, PowerPC pSeries/PowerNV/RTAS/HVSI/HVCS backends, z/VM IUCV, Xen, PPC udbg, ARM DCC, RISC-V SBI, and related debug constraints. The source was read as a complete 136-line file for this report.

## Important APIs, Types, and Functions

This is Kconfig data. Important symbols include `HVC_DRIVER`, `HVC_IRQ`, `HVC_CONSOLE`, `HVC_OLD_HVSI`, `HVC_OPAL`, `HVC_RTAS`, `HVC_IUCV`, `HVC_XEN`, `HVC_XEN_FRONTEND`, `HVC_UDBG`, `HVC_DCC`, `HVC_DCC_SERIALIZE_SMP`, `HVC_RISCV_SBI`, and `HVCS`.

## Control Flow

Kconfig dependency evaluation makes `HVC_DRIVER` a hidden common infrastructure symbol selected by individual backends. `HVC_IRQ` is selected by interrupt-driven backends. Architecture and hypervisor symbols gate each backend: for example `PPC_PSERIES` gates pSeries HVC, `PPC_POWERNV` gates OPAL, `S390 && NET` gates IUCV, `XEN` gates Xen, `ARM || ARM64` gates DCC, and `RISCV_SBI && NONPORTABLE` gates RISC-V SBI. Defaults enable common console paths for several platform types.

## State and Persistence Behavior

The file persists build-time HVC choices in `.config`. Runtime state is owned by the corresponding HVC C drivers and the common `hvc_console` layer, not by this Kconfig file.

## Dependencies and Integration Points

It integrates with `drivers/tty/hvc/Makefile`, the TTY Makefile's `obj-$(CONFIG_HVC_DRIVER) += hvc/`, architecture platform symbols, Xen and S390 IUCV infrastructure, serial console support for DCC, and the common HVC core. The selected symbols determine which backend object files are built.

## Risks and Edge Cases

Several options are architecture-specific and should not be visible outside their platform dependencies. `HVC_UDBG` and `HVC_RISCV_SBI` are explicitly bring-up or nonportable paths and can conflict with production console expectations. `HVC_DCC_SERIALIZE_SMP` intentionally restricts DCC use to CPU0 and can affect CPU hotplug or SMP behavior.

## Test Signals

Useful signals include configuration tests for each architecture backend; build checks that selecting a backend also selects `HVC_DRIVER` and, where needed, `HVC_IRQ`; boot console tests on pSeries, PowerNV, Xen, S390 z/VM, ARM DCC, and RISC-V SBI setups; and negative config tests confirming unavailable backends stay hidden when architecture dependencies are false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tty/hvc/Makefile

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/hvc/Makefile` maps HVC Kconfig symbols to the common hypervisor virtual console core and backend object files. The source was read as a complete 13-line file for this report.

## Important APIs, Types, and Functions

This is kbuild data. Important mappings are `CONFIG_HVC_DRIVER` to `hvc_console.o`, `CONFIG_HVC_IRQ` to `hvc_irq.o`, `CONFIG_HVC_CONSOLE` to `hvc_vio.o hvsi_lib.o`, `CONFIG_HVC_OPAL` to `hvc_opal.o hvsi_lib.o`, `CONFIG_HVC_OLD_HVSI` to `hvsi.o`, `CONFIG_HVC_RTAS` to `hvc_rtas.o`, `CONFIG_HVC_DCC` to `hvc_dcc.o`, `CONFIG_HVC_XEN` to `hvc_xen.o`, `CONFIG_HVC_IUCV` to `hvc_iucv.o`, `CONFIG_HVC_UDBG` to `hvc_udbg.o`, `CONFIG_HVC_RISCV_SBI` to `hvc_riscv_sbi.o`, and `CONFIG_HVCS` to `hvcs.o`.

## Control Flow

kbuild evaluates the `obj-$(CONFIG_*)` lines after the parent TTY Makefile descends into `drivers/tty/hvc/`. Built-in and module linkage follows the selected symbol values. Shared `hvsi_lib.o` is included by both pSeries HVC and OPAL configurations when selected.

## State and Persistence Behavior

No runtime state is owned here. The file persists build decisions as object inclusion in the kernel image or modules.

## Dependencies and Integration Points

It is paired with `drivers/tty/hvc/Kconfig` and depends on the parent `drivers/tty/Makefile` only entering the directory when `CONFIG_HVC_DRIVER` is enabled. It integrates HVC backend source files with the common console layer.

## Risks and Edge Cases

Shared library object inclusion must remain aligned with backend users; omitting `hvsi_lib.o` for a backend that references it would fail link. If Kconfig selects a backend without `HVC_DRIVER`, the parent directory might not be entered, so the Kconfig select relationships are part of the build contract.

## Test Signals

Useful signals include build-only checks for each HVC backend symbol, link checks for shared `hvsi_lib.o`, module/built-in combinations for `HVCS`, and config tests verifying the directory is skipped when no HVC backend selects `HVC_DRIVER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/hvc/Makefile -->
