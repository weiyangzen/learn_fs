# sources/distributed-fs/ceph-client/kernel/bpf/preload/bpf_preload.h

Purpose: defines the small kernel interface by which the preload module exposes preloaded BPF links to the core BPF filesystem machinery. The source was read as a complete 16-line file.

Important APIs/types: `struct bpf_preload_info` with `link_name` and `struct bpf_link *link`, `struct bpf_preload_ops` with `preload` callback and module owner, external `bpf_preload_ops`, and constant `BPF_PRELOAD_LINKS` set to 2.

Control flow: no executable flow. The active module installs a `bpf_preload_ops` implementation; callers invoke `preload` to obtain named links.

State and persistence: the global `bpf_preload_ops` pointer is runtime state owned by the loaded module. Returned links are persistent BPF link objects until module unload or link release.

Dependencies/integration: depends on `struct bpf_link` and module ownership. It integrates `bpf_preload_kern.c` with BPF FS link pinning/introspection code.

Risks and edge cases: `BPF_PRELOAD_LINKS` must match the module's populated link array. `link_name[16]` bounds names such as `maps.debug` and `progs.debug`; longer names would be truncated by callers using `strscpy`.

Test signals: module load/unload, preload callback returning two valid links, link names matching bpffs expectations, and safe behavior when `bpf_preload_ops` is NULL.
