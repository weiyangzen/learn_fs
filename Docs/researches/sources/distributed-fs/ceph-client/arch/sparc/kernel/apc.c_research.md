<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/apc.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/apc.c

Purpose: Platform driver and misc-device interface for Aurora Personality Chip power-management functions on SPARCstation-4/5 derivatives.

Important APIs and control flow: `apc_setup()` parses `apc=noidle`. `apc_swift_idle()` enters CPU standby by setting `APC_IDLE_ON`. `apc_ioctl()` implements fan, convenience-power, and bit-port get/set commands using UAPI masks. `apc_probe()` maps the `power-management` OF resource, registers `/dev/apc`, and installs `sparc_idle` unless disabled. The driver registers as a platform driver at `__initcall`.

State, dependencies, and risks: state includes global mapped `regs`, `apc_no_idle`, misc-device registration, and possibly the global `sparc_idle` callback. Dependencies include OF platform resources, SBus byte I/O, APC UAPI constants, user-copy helpers, and optional AUXIO debug LED. Risks include no remove path, global singleton registers, platform-specific bit-port side effects, and idle instability on prototype systems. Test signals are `/dev/apc` ioctl read/write tests, boot with and without `apc=noidle`, idle/resume behavior, and OF match/resource mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/apc.c -->
