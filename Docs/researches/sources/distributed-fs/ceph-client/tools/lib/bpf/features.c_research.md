# sources/distributed-fs/ceph-client/tools/lib/bpf/features.c

## Purpose
`features.c` implements libbpf's runtime kernel feature detection cache. Each feature probe performs a small BPF syscall, BTF load, link creation, helper call, or verifier-log check to infer whether a kernel capability is available, optionally through a BPF token FD.

## APIs, Types, and Functions
The public functions are `probe_fd()` and `feat_supported()`. Most of the file is a table of `feature_probe_fn` callbacks in `feature_probes[__FEAT_CNT]`, keyed by `enum kern_feature_id`. Probes cover program names, global data, minimal BTF, BTF funcs/global funcs/datasecs/qmark datasecs/floats/decl tags/type tags/enum64/layout, mmapable arrays, expected attach type, `bpf_probe_read_kernel`, `BPF_PROG_BIND_MAP`, module BTF, perf links, BPF cookies, syscall wrappers, multi-uprobe links with PID-filter sanity checks, `__arg_ctx`, full-range LDIMM64 map-value offsets, and the x86 uprobe syscall.

## Control Flow, State, and Persistence
Each probe is intentionally small and closes any FD it opens through `probe_fd()` or explicit cleanup. `feat_supported()` uses a provided `struct kern_feature_cache` or a static global cache, checks `cache->res[feat_id]` with `READ_ONCE`, runs the probe only for `FEAT_UNKNOWN`, stores `FEAT_SUPPORTED` or `FEAT_MISSING` with `WRITE_ONCE`, and logs probe errors as missing features. Token-aware probes set `.token_fd` and `BPF_F_TOKEN_FD` on map/prog/BTF operations when the cache supplies a token.

## Dependencies and Integration
The file depends on low-level libbpf syscall wrappers from `bpf.h`, raw BTF load helpers, BPF instruction macros from Linux filter headers, feature IDs and cache definitions from `libbpf_internal.h`, and external probes such as `probe_memcg_account()` and `probe_kern_syscall_wrapper()`. Object loading, skeleton loading, CO-RE setup, attach selection, and compatibility fallbacks query this cache before using newer kernel features.

## Risks and Test Signals
Risks include probes that require privileges or token permissions and therefore can report missing despite kernel support, verifier-log string matching in `probe_ldimm64_full_range_off()`, architecture-specific syscall numbering for x86 uprobes, kernel behavior changes that alter expected errno values, and global cache reuse when different token FDs would produce different answers. Test signals are feature selftests across old and new kernels, unprivileged/tokenized loading, expected FD cleanup under failure, verifier-log variants for LDIMM64 behavior, multi-uprobe PID-filter detection, and cache behavior when probes return negative errors.
