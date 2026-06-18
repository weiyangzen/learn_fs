# sources/distributed-fs/ceph-client/tools/perf/perf-read-vdso.c

### Purpose
`perf-read-vdso.c` is a small helper that writes the current process's `[vdso]` mapping bytes to stdout. Perf uses this kind of helper to capture vDSO contents for symbolization or tests.

### Important APIs, Types, And Functions
It includes `util/find-map.c` to reuse `find_map()`. `main()` locates the mapping named `[vdso]`, calculates `end - start`, writes it to stdout in a loop with `fwrite()`, flushes stdout, and returns nonzero on failure.

### Control Flow
The program exits with 1 if the vDSO map cannot be found, if any write returns zero, or if `fflush()` fails. Otherwise it streams the exact mapped bytes and exits 0.

### State And Persistence
It has no persistent state and writes only to stdout.

### Dependencies And Integration Points
It depends on Linux process maps and the shared `find_map()` implementation also used by perf's vDSO utility code.

### Risks
Pointer arithmetic is performed on `void *`, which relies on compiler extension support common in this codebase. Short writes are handled, but write errors only surface as zero writes or flush failure.

### Test Signals
Run the helper and verify it emits an ELF-like vDSO blob on Linux, returns nonzero in environments without `[vdso]`, and produces bytes that downstream perf tooling can parse.
