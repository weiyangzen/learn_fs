# sources/distributed-fs/ceph-client/arch/um/os-Linux/mem.c

## Purpose
Manages host temporary memory backing files and KASAN shadow mappings for UML.

## Important APIs, Types, and Functions
`kasan_map_memory()` maps noreserve anonymous shadow memory and marks it DONTDUMP/DONTFORK. `choose_tempdir()` prefers environment temp dirs or `/dev/shm` on tmpfs. `make_tempfile()`, `create_tmp_file()`, and `create_mem_file()` create unlinked or `O_TMPFILE` host files sized for UML physical memory. `check_tmpexec()` verifies executable mappings are allowed from the tempdir.

## Control Flow, State, and Persistence
Global `tempdir` is set once during early boot. Temporary files are unlinked or anonymous and persist only as open FDs. `check_tmpexec()` exits early if no executable mapping can be created.

## Dependencies and Integration Points
Used by physical memory setup, SKAS stub executable fallback, host memory mapping, and early host checks. Depends on tmpfs behavior, `O_TMPFILE`, `mkstemp`, `mmap`, and `madvise`.

## Risks and Test Signals
Risks include non-tmpfs dirty throttling, noexec temp dirs, failed sparse file sizing, KASAN shadow fork/dump flags, and tempdir environment lifetime. Test TMPDIR variants, `/dev/shm` absence, noexec mounts, KASAN configs, and large memory sizes.
