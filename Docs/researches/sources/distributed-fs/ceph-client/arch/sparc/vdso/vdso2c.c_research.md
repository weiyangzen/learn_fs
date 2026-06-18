# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso2c.c

Purpose: host tool that converts stripped/unstripped SPARC vDSO ELF files into either raw output or a kernel C `vdso_image` object.

Important APIs/functions: main flow is `main()`, `map_input()`, `go()`, and `fail()`. It includes `vdso2c.h` twice to generate `go64()` and `go32()`. Big-endian `GET_BE`/`PUT_BE` helper macros read ELF fields.

Control flow: the tool maps raw and stripped input files, derives an output object name from the output filename unless writing a `.so`, dispatches by ELF class, and lets the bitness-specific generated function validate and emit data. `fail()` unlinks partial output and exits.

State and persistence: writes the requested output file at build time. No kernel runtime state.

Dependencies and integration points: run by the vDSO Makefile after linking/stripping. Depends on Linux ELF headers, tools big-endian byte helpers, mmap, and the validation/emission logic in `vdso2c.h`.

Risks: SPARC vDSO is big-endian, so unaligned BE field reads must be correct. Output naming controls generated C symbol names. Validation failures should remove partial outputs.

Test signals: build both 32-bit and 64-bit vDSO images, run usage/error paths, feed malformed ELF with missing PT_LOAD/relocations, and inspect generated C object names/data alignment.
