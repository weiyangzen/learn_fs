<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/ioctl.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/ioctl.go

Purpose: Go equivalents of Linux `_IOC`, `_IOR`, `_IOW`, and `_IOWR` macros used to construct ioctl command numbers.

Important APIs/types/functions: constants for bit widths, masks/shifts, direction bits, and functions `_ioc`, `_ior`, `_iow`, `_iowr`.

Control flow: command constructors combine direction, type, number, and size using shifts and bitwise OR.

State and persistence: none; command values are pure calculations.

Dependencies and integration points: used by `beegfs.go` to initialize BeeGFS ioctl command variables.

Risks: bit widths and direction constants are architecture-sensitive as comments note. A mismatch yields ioctl numbers the kernel will reject or misinterpret.

Test signals: no direct tests; integration ioctl tests indirectly verify command numbers on the target architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/ioctl.go -->
