# sources/distributed-fs/ceph-client/arch/arm64/include/asm/setup.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/setup.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/setup.h` Declares early boot FDT/boot argument storage and parses the arm64 debug_rodata mode. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
__fdt_pointer, boot_args[4], arch_parse_debug_rodata(). The file is 44 lines / 792 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
arch_parse_debug_rodata accepts on/off/noalias and sets rodata_enabled/rodata_full accordingly; other strings return false for generic parsing.

### State, Persistence, And Dependencies
Persistent boot state includes __fdt_pointer, boot_args, rodata_enabled, and rodata_full. Depends on string and uapi setup; used by head.S, early boot setup, command-line parsing, and rodata permission setup.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Incorrect parsing can weaken rodata protection or reject valid boot arguments; early variables must remain accessible before full init.

### Test Signals
Boot with debug_rodata=on/off/noalias/invalid, inspect rodata permissions and early FDT argument propagation.
