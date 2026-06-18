<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/Kconfig -->
# sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/Kconfig

Purpose: defines kernel configuration options for the Bluetooth RFCOMM protocol layer and optional RFCOMM TTY emulation.

Important APIs/types/functions: `config BT_RFCOMM` is a tristate depending on `BT_BREDR`; it builds RFCOMM stream transport for Dialup Networking, OBEX, and similar Bluetooth applications. `config BT_RFCOMM_TTY` is a bool depending on `BT_RFCOMM` and `TTY`; it enables `/dev/rfcomm*` TTY emulation over RFCOMM channels.

Control flow: Kconfig selection determines whether the RFCOMM object is built into the kernel, as a module, or omitted, and whether `tty.o` is included in the RFCOMM module.

State and persistence behavior: no runtime state. Configuration persists in the kernel `.config` and determines compiled code and module availability.

Dependencies and integration points: `BT_RFCOMM` integrates with BR/EDR Bluetooth and `BTPROTO_RFCOMM`; `BT_RFCOMM_TTY` integrates with the Linux TTY subsystem and the RFCOMM device ioctl layer.

Risks: enabling TTY support expands the RFCOMM attack surface to ioctls, device lifetime, sysfs attributes, and line-discipline interactions. Disabling RFCOMM removes user-visible protocol support expected by legacy Bluetooth applications.

Test signals: allmodconfig/build tests should cover built-in and module modes, and runtime tests should confirm RFCOMM sockets are unavailable when disabled, available when `BT_RFCOMM` is enabled, and `/dev/rfcomm*` support appears only with `BT_RFCOMM_TTY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/Kconfig -->
