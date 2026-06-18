# sources/distributed-fs/ceph-client/tools/perf/util/dso.h

## Purpose
This header defines the DSO object model used throughout perf. It exposes binary type classification, namespace-aware symbol/data access, build identity, data caching APIs, refcounted lifetime helpers, and a large set of inline accessors for `struct dso`.

## Important APIs And Types
Major enums include `dso_binary_type`, `dso_space_type`, `dso_swap_type`, `dso_data_status`, `dso_type`, and `dso_load_errno`. Core data structures include `struct dso_id`, `struct dso_cache`, `struct dso_data`, `struct dso_bpf_prog`, `struct kmod_path`, and the refcount-checked `struct dso`. The header declares construction/lifetime functions, name/id mutation, build-id APIs, module parsing/decompression, DSO data fd/read/cache APIs, ELF machine helpers, map/kernel helpers, symbol/source dump helpers, debuginfo access, and symbol-byte reading.

## Control Flow And Integration
Consumers create or find DSOs through machine/dsos code, mutate identity as more mmap2/build-id data appears, read data through `dso__data_*`, and release references with `dso__put()` or `dso__zput()`. Inline accessors use `RC_CHK_ACCESS()` to support reference-count checking builds. Generic mapping, annotation, symbol loading, auxtrace, BPF, libdw, and srcline code all depend on this contract.

## State And Persistence
The DSO carries persistent in-memory state for symbol trees, source-line trees, inlined nodes, global/data type trees, names, file-descriptor cache metadata, BPF ids, build id, namespace info, binary/symtab type, and warning flags. The backing binary/debug file is not owned; only temporary decompressed module files are created and removed by implementation code.

## Risks And Test Signals
Risks include direct field access bypassing inline/refcount checks, callers forgetting to pair `dso__data_get_fd()` with `dso__data_put_fd()`, ownership confusion for allocated versus borrowed names, and misclassifying binary types. Tests should compile with refcount checking and optional feature combinations, verify `DSO__SWAP` behavior, exercise inline flag setters/getters, pair fd-lock annotations, and validate kmod parsing and data cache APIs through the implementation.
