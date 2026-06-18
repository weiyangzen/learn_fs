<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/Makefile -->
## sources/distributed-fs/ceph-client/arch/parisc/lib/Makefile

### Purpose
This Makefile selects PA-RISC architecture library objects for built-in archive and object linkage.

### Important APIs, Types, And Functions
`lib-y` includes `lusercopy.o`, `bitops.o`, `io.o`, `memset.o`, `memcpy.o`, `ucmpdi2.o`, and `delay.o`; `obj-y` includes `iomap.o`.

### Control Flow
Kbuild compiles listed library sources into the architecture library or built-in objects according to `lib-y`/`obj-y`.

### State, Persistence, And Dependencies
No runtime state. Build output persists in the kernel build tree. Dependencies are Kbuild object classification and source availability.

### Integration Points
These objects provide low-level copy, memory, atomic, I/O, compare, delay, and iomap helpers used throughout the PA-RISC kernel.

### Risks
Moving helpers between `lib-y` and `obj-y` can affect link order/export availability. Missing objects cause architecture-wide build failures.

### Test Signals
Full PA-RISC build and symbol resolution for atomic, delay, memcpy/usercopy, and I/O helper references validate this Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/Makefile -->
