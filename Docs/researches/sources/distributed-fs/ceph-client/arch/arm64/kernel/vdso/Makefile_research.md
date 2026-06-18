## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/Makefile

### Purpose
`vdso/Makefile` builds the native AArch64 VDSO shared object, strips it, checks it, and generates kernel offsets for exported VDSO symbols.

### Important APIs, Types, And Functions
It defines `obj-vdso` objects for time, note, sigreturn, getrandom, and ChaCha, VDSO linker flags, VDSO-specific C flags, `vdso.so.dbg`, stripped `vdso.so`, and `include/generated/vdso-offsets.h` generation through `gen_vdso_offsets.sh`.

### Control Flow
Kbuild compiles VDSO C/assembly with profiling, stack protector, LTO, CFI, randstruct, SCS, and incompatible warning flags removed, links with the VDSO linker script as a shared object, runs generic VDSO checks, strips debug data for the embedded image, and extracts `VDSO_*` symbol offsets from `nm` output.

### State, Persistence, And Dependencies
Build outputs are object files, `vdso.lds`, `vdso.so.dbg`, stripped `vdso.so`, and generated offsets. No runtime state is created by the Makefile.

### Integration Points
It depends on `lib/vdso/Makefile.include`, compiler support for tiny code model, optional generated gettimeofday/getrandom include files, BTI linker flags, and `vdso-wrap.S` including the final `vdso.so`.

### Risks
Global kernel flags can break freestanding VDSO builds if not removed. Linker orphan handling and exported symbol versions are ABI-sensitive. Missing generated offsets breaks kernel references to VDSO symbols.

### Test Signals
Run ARM64 builds with GCC/Clang, LLD/BFD, BTI on/off, WERROR on, VDSO check output, and inspect exported symbol versions and generated offsets.
