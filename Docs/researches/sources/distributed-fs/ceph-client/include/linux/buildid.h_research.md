## sources/distributed-fs/ceph-client/include/linux/buildid.h

**Purpose:** This header exposes helpers for parsing ELF build IDs from VMAs, files, memory buffers, and the kernel image.

**Important APIs/types/functions:** `BUILD_ID_SIZE_MAX` is 20. APIs include `build_id_parse()`, `build_id_parse_file()`, `build_id_parse_nofault()`, `build_id_parse_buf()`, optional `vmlinux_build_id`, `init_vmlinux_build_id()`, and the `struct freader` abstraction with `freader_init_from_file()`, `freader_init_from_mem()`, `freader_fetch()`, and `freader_cleanup()`.

**Control flow, state, persistence:** `freader` carries temporary read state for either a file-backed folio mapping or an in-memory buffer, including error state and fault policy. Parsed build IDs are copied into caller-provided buffers; the optional vmlinux build ID persists as global kernel state.

**Dependencies/integration:** Depends on VMA, file, folio, and ELF note parsing implementation. Used by stack traces, vmcore metadata, perf/BPF, and diagnostics that identify binaries.

**Risks and test signals:** Risks include faulting in no-fault paths, stale folio mappings, wrong buffer bounds, and assuming all build IDs are SHA1-sized despite the max constant. Test signals include parsing valid/malformed ELF notes, nofault VMA tests, file-backed and memory-backed readers, vmcore/stacktrace build-ID output, and cleanup leak checks.
