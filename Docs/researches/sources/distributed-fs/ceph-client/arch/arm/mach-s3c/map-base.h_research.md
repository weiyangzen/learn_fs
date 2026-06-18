<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-base.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-base.h

### Purpose
Defines the shared high virtual-address base layout for legacy Samsung S3C/S5P ARM I/O mappings.

### Important APIs, Types, And Functions
Important macros include `S3C_ADDR_BASE`, `S3C_ADDR()`, `S3C_VA_IRQ`, `S3C_VA_SYS`, `S3C_VA_MEM`, `S3C_VA_UART`, `S3C_VA_TIMER`, `S3C_VA_WATCHDOG`, `S3C_VA_USB_HSPHY`, and related virtual regions.

### Control Flow
There is no runtime flow; machine map descriptors use these constants during `iotable_init()`.

### State, Persistence, And Dependencies
No mutable state. The file persists a virtual memory contract between early boot code, register headers, and mapping setup.

### Integration Points
Included by map wrappers and register headers for clock, GPIO, system controller, watchdog, timer, UART, and USB PHY bases.

### Risks
Changing the layout can break early debug, exception-safe mappings, and register macros before `ioremap()` is available.

### Test Signals
Early boot console, timer init, IRQ init, and register access before driver probing validate the mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-base.h -->
