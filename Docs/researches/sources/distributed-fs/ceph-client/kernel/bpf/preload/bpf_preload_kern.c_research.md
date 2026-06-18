# sources/distributed-fs/ceph-client/kernel/bpf/preload/bpf_preload_kern.c

Purpose: kernel module implementation that loads the embedded iterator BPF skeleton, attaches map and program iterators, converts their link FDs into kernel `bpf_link` refs, and exposes them as `maps.debug` and `progs.debug` through `bpf_preload_ops`. The source was read as a complete 94-line file.

Important APIs/functions: `load_skel`, `free_links_and_skel`, `preload`, module `load`, and `fini`. Important state includes `maps_link`, `progs_link`, `skel`, and static `struct bpf_preload_ops ops`.

Control flow: `load_skel` opens the endian-specific `iterators_bpf` skeleton, loads it, attaches both iterator programs, converts skeleton link FDs to kernel links, closes the original FDs to avoid stealing init's standard descriptors, and leaves the links referenced globally. On module init, successful skeleton load publishes `bpf_preload_ops`. On module exit, the global ops pointer is cleared and links/skeleton are destroyed. The `preload` callback fills two `bpf_preload_info` entries with stable link names and link pointers.

State and persistence: `maps_link`, `progs_link`, and `skel` persist for the module lifetime. `bpf_preload_ops` is the externally visible registration pointer. No file-backed state is written by this file directly; BPF FS consumers use the exposed links.

Dependencies/integration: includes generated little- or big-endian lightweight skeleton header by compile-time byte order, uses `bpf_link_get_from_fd`, `bpf_link_put`, `close_fd`, late init/module exit, and imports `BPF_INTERNAL` namespace.

Risks and edge cases: any skeleton load/attach failure must clean up partial state. Closing skeleton FDs after taking link refs is required to avoid FD ownership side effects. `bpf_preload_ops` publication must happen only after both links are valid. Generated skeleton/API drift can break module load.

Test signals: module insertion/removal, presence and readability of `maps.debug`/`progs.debug` in bpffs, failure-injection through skeleton load/attach, fd-leak checks, and endian-specific build coverage.
