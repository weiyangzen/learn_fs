## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/head_32.S

### Purpose
`compressed/head_32.S` is the 32-bit compressed-kernel entry path. It relocates the compressed image to a safe buffer, clears BSS, calls `extract_kernel()`, and jumps to the decompressed kernel entry.

### Important APIs, Types, And Functions
Important symbols are `startup_32`, local `.Lrelocated`, `gdt`, `boot_stack`, and `boot_stack_end`. It uses boot protocol fields such as `BP_scratch`, `BP_kernel_alignment`, and `BP_init_size`, plus constants like `LOAD_PHYSICAL_ADDR` and `BOOT_STACK_SIZE`.

### Control Flow
`startup_32` disables interrupts, computes the load-time GOT delta with a local call/pop, installs a GDT, loads flat segments, chooses the decompression output address based on relocatability and alignment, computes a relocation target at the end of the init buffer, sets a stack, zeroes EFLAGS, copies the compressed image backward to prevent overlap corruption, reloads the GDT from its relocated copy, jumps to `.Lrelocated`, clears BSS, calls `extract_kernel(output, real_mode_pointer)`, and jumps to the returned entry with `%ebx` cleared.

### State, Persistence, And Dependencies
State includes relocated compressed text/data, boot stack, GDT descriptor, and cleared BSS. It depends on exact boot protocol register conventions, real/protected-mode setup having passed `boot_params` in `%esi`, and C `extract_kernel()`.

### Integration Points
Linked into compressed `vmlinux` for 32-bit kernels. The outer setup code transfers control here after protected-mode setup.

### Risks
The overlap-safe backward copy and output address calculations are critical. Wrong `init_size`, `_end`, or alignment values can overwrite the decompressor or payload. The startup address and ABI expectations are fixed by the x86 boot protocol.

### Test Signals
Boot 32-bit relocatable and non-relocatable kernels, vary load address and alignment, test multiple compression formats, and inspect early failures around BSS clearing or image overlap.
