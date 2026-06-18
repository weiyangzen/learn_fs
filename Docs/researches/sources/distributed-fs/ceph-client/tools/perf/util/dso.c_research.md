# sources/distributed-fs/ceph-client/tools/perf/util/dso.c

## Purpose
This file implements perf's DSO object lifecycle, identity, binary-path resolution, file descriptor cache, data cache, module compression handling, build-id helpers, ELF-machine detection, and symbol-byte reading. It is the central backing store for maps, symbols, annotation, build-id processing, namespace-aware file access, BPF JIT code, and kernel module handling.

## Important APIs, Types, And Functions
Key lifecycle APIs are `dso__new_id()`, `dso__new()`, `dso__get()`, `dso__put()`, and `dso__delete()`. Identity/name APIs include `dso_id__cmp()`, `__dso__improve_id()`, `dso__set_short_name()`, `dso__set_long_name()`, and build-id helpers. File/data APIs include `dso__read_binary_type_filename()`, `dso__data_get_fd()`, `dso__data_put_fd()`, `dso__data_close()`, `dso__data_size()`, `dso__data_read_offset()`, `dso__data_read_addr()`, cache-write helpers, `dso__e_machine()`, `dso__read_symbol()`, and `dso__debuginfo()`. Module helpers include `is_kernel_module()`, `__kmod_path__parse()`, `dso__set_module_info()`, and decompression APIs.

## Control Flow
New DSOs initialize refcounted state, rb-trees, lock, names, default binary/symtab type, file data state, and architecture assumptions. File opening resolves a path from the current binary type, optional symfs/root namespace, debuglink/build-id/debug-info locations, guest roots, kcore, or module paths; compressed modules are decompressed to a temporary file and unlinked after opening/using. Data reads first ensure file size, then use 4 KiB rb-tree cache chunks populated from file, BPF program info, or synthetic OOL data. File descriptors are globally LRU-managed under `_dso__data_open_lock`, capped at half `RLIMIT_NOFILE`.

## State, Dependencies, And Integration
`struct dso` owns symbol/source/type rb-trees, name strings, namespace info, auxtrace/libdw/a2l handles, `struct dso_data`, build identity, BPF metadata, load error state, and many one-bit flags. Global state includes the open-DSO list, open count, lazily initialized open lock, and cached fd limit. Dependencies include namespace switching, symfs path helpers, compression backends, build-id/debuglink readers, map address translation, libbpf/perf env, auxtrace, libdw, srcline, symbol trees, and machine root metadata.

## Risks And Test Signals
Risks include lock-order mistakes between DSO locks and the global open lock, stale `errno` leading to wrong load errors, temporary decompression cleanup failures, DSO renames invalidating sorted `dsos` arrays, partial ID comparison treating missing IDs as equal, cache writes changing only memory not backing files, and build option differences for zlib/lzma/libbpf/libdw. Tests should cover fd LRU under low `RLIMIT_NOFILE`, namespace path fallback, all binary-type path constructors, compressed and uncompressed module handling, DSO id improvement/sorting, cache read/write across chunk boundaries, ELF endianness/e_machine parsing, BPF program reads, refcount deletion cleanup, and `dso__strerror_load()` mapping.
