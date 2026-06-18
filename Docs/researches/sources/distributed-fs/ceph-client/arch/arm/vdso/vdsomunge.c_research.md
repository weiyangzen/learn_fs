## sources/distributed-fs/ceph-client/arch/arm/vdso/vdsomunge.c

### Purpose
Host build utility that copies an ARM vDSO shared object while clearing `EF_ARM_ABI_FLOAT_SOFT` and rejecting hard-float or unsupported ELF inputs.

### Important APIs, Types, And Functions
Key functions are `fail`, `cleanup`, `read_elf_word`, `read_elf_half`, `write_elf_word`, and `main`. It uses ELF32 headers, `mmap`, `ftruncate`, `msync`, and ARM `e_flags` constants.

### Control Flow
`main` validates arguments, maps the input ELF, checks magic, class, data order, `ET_DYN`, `EM_ARM`, and EABI v5. It fails if hard-float is set, copies the input to a writable output mapping, clears the soft-float flag if present, syncs, and lets `cleanup()` remove the output on failure.

### State, Persistence, And Dependencies
Persistent state is the output `.so.dbg`. Local state includes endian-swap decisions and the global failure/outfile variables used by `atexit`. Dependencies are host libc, `<elf.h>`, and kernel-defined fallback constants for older host headers.

### Integration Points
Invoked by the ARM vDSO Makefile between raw linking and stripping so the final vDSO is usable by both soft- and hard-float programs that do not pass FP arguments.

### Risks
Insufficient ELF validation could map short files and read invalid headers. Any future vDSO FP argument/result would invalidate the flag-clearing assumption. Host endianness and target ELF data order must be handled correctly.

### Test Signals
Run on sample ARM ELF files with soft, hard, and no float flags; check output `e_flags` with `readelf -h`; verify failure removes partial output.
