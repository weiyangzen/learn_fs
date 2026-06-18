<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/common.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/common.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/common.h` belongs to Intel/DEC Footbridge ARM platform support in the Ceph-client kernel source snapshot. It exports register definitions, physical/virtual address helpers, IRQ constants, or prototypes consumed by adjacent platform C/assembly files.

### Important APIs, Types, And Functions
The file is declarative and has no standalone runtime API beyond the build or header surface.

### Control Flow
There is no executable control flow; consumers include the header or build metadata.

### State, Persistence, And Dependencies
Dependencies include `linux/reboot.h`. Local/static state or exported register data includes none. Compatible strings or firmware/device-tree identifiers observed: none. There is no private runtime persistence in this header; it defines constants and declarations used by compiled platform code.

### Integration Points
Integration points are adjacent platform C/assembly files through shared macros, prototypes, or build rules. Callers should treat none as platform hooks rather than generic APIs when those symbols are visible.

### Risks
Primary risks include interrupt masking/wakeup regressions.

### Test Signals
Useful test signals include ARM build coverage for the relevant CONFIG symbols, interrupt storm, mask/unmask, and wake-capable IRQ tests. Source reading signal: 15 lines; 1 include; 0 function/entry points; 0 macro/defines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/common.h -->
