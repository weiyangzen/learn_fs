<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf.h

## Purpose
`bpf.h` is libbpf's public low-level BPF syscall API header. It exposes C declarations and option structs for creating/manipulating BPF maps, programs, links, BTF objects, pinned objects, tokens, and related metadata without using the higher-level ELF/object loader.

## Important APIs, types, and functions
Important option structs include `bpf_map_create_opts`, `bpf_prog_load_opts`, `bpf_btf_load_opts`, `bpf_map_batch_opts`, `bpf_obj_pin_opts`, `bpf_obj_get_opts`, `bpf_prog_attach_opts`, `bpf_prog_detach_opts`, `bpf_link_create_opts`, `bpf_link_update_opts`, `bpf_prog_query_opts`, `bpf_raw_tp_opts`, `bpf_get_fd_by_id_opts`, `bpf_test_run_opts`, `bpf_token_create_opts`, `bpf_prog_stream_read_opts`, and `bpf_prog_assoc_struct_ops_opts`. Each struct carries a `sz` field and a `__last_field` macro for forward/backward compatibility. APIs are marked `LIBBPF_API`.

## Control flow
The header defines the contract used by `bpf.c`: callers zero/initialize option structs, set `sz`, pass fds/pointers/counts, and receive fds, counts, logs, durations, revisions, or negative errors. Batch functions treat `count` as both input and output.

## State and persistence behavior
The header owns no state. It describes kernel object lifetimes mediated by fds and bpffs pins. `libbpf_set_memlock_rlim()` affects process-global behavior implemented in `bpf.c`.

## Dependencies and integration points
It includes Linux BPF UAPI types plus `libbpf_common.h` and `libbpf_legacy.h`. It is installed as a public `include/bpf/bpf.h` header and is consumed by both libbpf internals and external applications.

## Risks and edge cases
Option struct compatibility depends on callers setting `sz` correctly, usually through libbpf option macros. Some unions provide legacy aliases such as `replace_prog_fd`/`replace_fd`, so field misuse can be subtle. Documentation comments warn that batch `count` is unreliable on `EFAULT`.

## Test signals
Compile external low-level API users against the installed header, run ABI symbol checks against `libbpf.map`, and execute syscall wrapper tests from `bpf.c` for all option structs and legacy aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf.h -->
