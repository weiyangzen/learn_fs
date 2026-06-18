## sources/distributed-fs/ceph-client/arch/x86/boot/boot.h

### Purpose
`boot.h` is the shared C header for x86 real-mode setup code. It defines early boot globals, segment-address helpers, heap allocation primitives, BIOS register layout, and prototypes for setup subsystems.

### Important APIs, Types, And Functions
Important declarations include `hdr`, `boot_params`, `STACK_SIZE`, `cpu_relax()`, `io_delay()`, segment helpers for DS/FS/GS, `rdfs*`, `wrfs*`, `rdgs*`, `wrgs*`, `memcmp_fs()`, `memcmp_gs()`, `RESET_HEAP()`, `GET_HEAP()`, `heap_free()`, `struct biosregs`, `intcall()`, `cmdline_find_option()`, `cmdline_find_option_bool()`, and prototypes for A20, APM, CPU validation, console, EDD, memory, protected-mode jump, formatting, tty, and video code.

### Control Flow
Most routines are inline utilities used by setup modules. Segment helpers load FS/GS and perform memory access through segment overrides. Heap helpers bump `HEAP` with alignment and bounds checking. The command-line inline wrappers reject pointers at or above 1 MiB for real-mode access, then call the parser implementation.

### State, Persistence, And Dependencies
Central persistent boot state is `boot_params`, the setup header `hdr`, and the bump heap between `_end` and `heap_end`. The header depends on Linux boot protocol structures, EDD definitions, local boot C type/string/I/O helpers, and exact real-mode compiler assumptions.

### Integration Points
Every real-mode boot C file includes this header. It is the API boundary between setup modules and assembly stubs such as `bioscall.S`, `copy.S`, `pmjump.S`, and `header.S`.

### Risks
The segment helper API can address only what real-mode segmentation permits. The heap is a simple bump allocator with no free path, so ordering and size estimates matter. `struct biosregs` layout is consumed by assembly and cannot be changed casually.

### Test Signals
Build setup objects with `REALMODE_CFLAGS`, check `struct biosregs` offsets against assembly expectations, run boot tests that exercise command line, BIOS calls, memory detection, video, and protected-mode transition.
