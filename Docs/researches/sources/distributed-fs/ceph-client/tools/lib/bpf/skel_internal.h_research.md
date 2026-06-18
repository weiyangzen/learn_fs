## sources/distributed-fs/ceph-client/tools/lib/bpf/skel_internal.h

Purpose: Provides the runtime support header embedded by generated lightweight BPF skeletons (`*.lskel.h`) for both user-space and kernel/preload contexts.

Important APIs/types: `struct bpf_map_desc`, `struct bpf_prog_desc`, `struct bpf_loader_ctx`, and `struct bpf_load_and_run_opts` define loader I/O. Inline wrappers include `skel_sys_bpf()`, map operations, raw tracepoint/link creation, map data preparation/finalization/freeing, and `bpf_load_and_run()`.

Control flow: Generated skeletons allocate context/data, create a loader array map, populate/freeze it in user space, load a `BPF_PROG_TYPE_SYSCALL` loader program, run it with `BPF_PROG_RUN`, then close transient FDs. Map data handling differs by build: kernel uses `kvmalloc` and direct array value access, user space uses anonymous mmap then MAP_FIXED remap to the BPF map.

State/persistence: Loader state is transient. File descriptors keep maps/programs alive while open. Generated skeleton structures store map/prog FDs and mapped data pointers.

Dependencies/integration: Integrates with raw `bpf()` syscall, generated bpftool skeleton code, optional signatures/keyrings, kernel-only close/allocation APIs, and userspace mmap.

Risks: This is explicitly feature/layout dependent. Incorrect `union bpf_attr` sizing, MAP_FIXED misuse, unsupported signatures in kernel mode, or map-data lifetime confusion can break skeleton loading. `skel_closenz()` ignores fd 0, which is intentional but can surprise callers.

Test signals: Generated skeleton load/run tests should exercise user and kernel modes, rodata/bss remapping, loader error strings, signature/keyring paths, map freeze/info calls, and cleanup after partial failures.
