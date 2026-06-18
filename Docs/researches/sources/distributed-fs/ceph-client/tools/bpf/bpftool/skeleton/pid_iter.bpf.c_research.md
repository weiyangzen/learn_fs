# sources/distributed-fs/ceph-client/tools/bpf/bpftool/skeleton/pid_iter.bpf.c

Purpose: BPF iterator program used by bpftool to discover processes holding BPF object file descriptors. It runs over `iter/task_file`, filters files by BPF object type, and emits `pid_iter_entry` records.

Important APIs, types, and functions: Defines local CO-RE compatible representations for perf links/events and a local link-type enum. `obj_type` is a volatile rodata selector matching bpftool object types. `get_obj_id()` reads ids from `bpf_prog`, `bpf_map`, `bpf_link`, or `btf`. `get_bpf_cookie()` extracts the perf event cookie from perf-event links. `iter()` is the iterator entrypoint and writes records with `bpf_seq_write()`.

Control flow: For each task/file pair, `iter()` rejects null entries, selects expected `file_operations` symbol for the requested object type, handles weak `bpf_link_fops_poll`, filters non-matching files, fills pid, object id, optional perf-event BPF cookie, and comm, then emits the fixed record.

State and persistence: No persistent state. Runtime state is only the current iterator context and `obj_type` configured by userspace before loading.

Dependencies and integration points: Depends on kernel BTF for CO-RE reads, ksyms for BPF file operation symbols, `pid_iter.h` record layout, and bpftool userspace reader. It integrates with bpftool PID reference reporting.

Risks: Relies on kernel internal layout and symbol availability. Weak `bpf_link_fops_poll` support covers newer kernels but missing symbols or changed link internals can suppress records. `comm` is fixed to 16 bytes.

Test signals: Load iterator for each object kind, hold BPF object fds in test processes, and confirm emitted pid/id/comm records and perf-event cookie presence for perf links.
