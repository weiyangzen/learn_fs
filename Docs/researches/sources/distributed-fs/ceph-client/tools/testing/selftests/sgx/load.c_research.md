# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/load.c

## Purpose
Loads the test enclave ELF, prepares SGX segment metadata, creates an enclave through `/dev/sgx_enclave`, adds pages, and initializes the enclave with a generated signature.

## Important APIs, types, and functions
`encl_delete()` releases enclave mappings, binary mapping, fd, heap, and segment table. `encl_map_bin()` maps `test_encl.elf`. `encl_ioc_create()` issues `SGX_IOC_ENCLAVE_CREATE`. `encl_ioc_add_pages()` issues `SGX_IOC_ENCLAVE_ADD_PAGES` with `SGX_PAGE_MEASURE` when needed. `encl_get_entry()` scans ELF `SHT_SYMTAB`/`SHT_STRTAB` for a symbol value. `encl_load()` parses program headers into `struct encl_segment` entries and appends an anonymous heap segment. `encl_map_area()` reserves an aligned power-of-two enclave virtual range. `encl_build()` creates, adds, and initializes the enclave with `SGX_IOC_ENCLAVE_INIT`.

## Control flow
`encl_load()` opens `/dev/sgx_enclave`, sanity-checks readable and executable mappings of the device, maps the enclave ELF, counts `PT_LOAD` segments plus a heap, translates ELF flags to VMA protections and SGX SECINFO flags, computes source size, and rounds enclave size up to a power of two. `encl_build()` maps an aligned address window, creates SECS, adds all segments before userspace VMAs are mapped, then initializes using `encl->sigstruct`.

## State and persistence
All state is contained in `struct encl`: device fd, ELF mapping, segment table, source and enclave sizes, base address, SECS, and SIGSTRUCT. Kernel enclave state persists only for the lifetime of the fd/mappings and is cleaned by `encl_delete()`.

## Dependencies and integration points
Depends on ELF layout produced by the SGX Makefile and linker script, Linux SGX UAPI ioctls, `main.h` structures, and `sigstruct.c` populating `encl->sigstruct` before `encl_build()`.

## Risks
Segment parsing assumes the first RW `PT_LOAD` is TCS and computes offsets from a shared source base. Device `PROT_EXEC` mapping fails on noexec `/dev`, and the diagnostic explicitly points to remounting. Partial cleanup paths must avoid double-closing fd 0, since `encl->fd` is treated as truthy.

## Test signals
Failures print device, ELF, mmap, or ioctl errors. Higher-level SGX tests fail at setup if load, measure, build, or vDSO symbol resolution does not complete.
