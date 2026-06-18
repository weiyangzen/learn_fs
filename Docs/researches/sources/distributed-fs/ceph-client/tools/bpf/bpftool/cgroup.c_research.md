<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/cgroup.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/cgroup.c

Purpose: this implements `bpftool cgroup` commands for showing, tree-walking, attaching, and detaching BPF programs on cgroups.

Important APIs/functions: `parse_attach_type()` accepts libbpf attach type strings and legacy/prefix strings. `show_bpf_prog()` prints one attached program, resolving program names and optional attach BTF names from vmlinux BTF. `show_effective_bpf_progs()` and `show_attached_bpf_progs()` query attachment lists. `do_show()`, `do_show_tree()`, `do_attach()`, and `do_detach()` implement user commands. `find_cgroup_root()` finds the cgroup v2 mount from `/proc/mounts`.

Control flow: `do_cgroup()` dispatches subcommands. Show opens the requested cgroup, checks whether any supported attach type has programs, optionally starts JSON/table headers, loads vmlinux BTF, and iterates `cgroup_attach_types`. Tree show resolves a root path or cgroup v2 mount, then uses `nftw()` to visit directories and query attached programs. Attach/detach open the cgroup, parse attach type, parse a program handle through shared helpers, parse optional `multi`/`override` flags for attach, and call `bpf_prog_attach()` or `bpf_prog_detach2()`.

State and persistence: show commands are read-only. Attach and detach persist kernel cgroup BPF attachment state. Static state includes `query_flags`, `btf_vmlinux`, and `btf_vmlinux_id` for the current command; program and cgroup FDs are closed after use.

Dependencies and integration points: it depends on libbpf string helpers, BPF cgroup attach/query syscalls, shared program parsers from `common.c`, bpftool JSON output, BTF lookup, `/proc/mounts`, and cgroup v2 filesystem paths.

Risks: the fixed arrays for queried program IDs and attach flags hold 1024 entries; more attachments can be truncated depending on kernel query behavior. `btf_vmlinux` is assigned repeatedly and not freed in this file, relying on process lifetime or libbpf ownership assumptions. Attach flag parsing permits both `multi` and `override` together even if the kernel rejects the combination. Tree walking can be expensive on large cgroup hierarchies and races with cgroup deletion.

Test signals: tests should cover show/list and tree with and without effective mode, JSON/plain output, all accepted attach type aliases, attach and detach with id/name/tag/pinned program handles, multi/override flags, absent cgroup v2 mount, unsupported attach types returning `EINVAL`, and BTF attach-name resolution for fentry/fexit-like cgroup programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/cgroup.c -->
