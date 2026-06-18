# sources/distributed-fs/ceph-client/samples/bpf/sampleip_user.c

Purpose: userspace loader that attaches `sampleip` BPF program to perf sampling events and prints top sampled kernel IPs.

Important APIs/types/functions: `sampling_start`, `sampling_end`, `struct ipcount`, `count_cmp`, `print_ip_map`, `int_exit`, and CLI parsing in `main`. Uses `perf_event_open`, libbpf program attach to perf event FDs, and trace helper symbol lookup.

Control flow: parses frequency and duration, loads BPF object, finds map/program, opens per-CPU software/hardware perf events, attaches the BPF program, sleeps, detaches, reads the map, sorts counts, and prints symbolized IPs.

State and persistence: perf event FDs and BPF links are live during sampling; counts are in the BPF map until object close.

Dependencies and integration: pairs with `sampleip_kern.c`, depends on perf_event support, libbpf, kallsyms/trace helpers, and root or perf permissions.

Risks: high sampling frequency can add overhead. Symbolization depends on kernel symbols. CPU hotplug or large CPU counts can affect per-CPU setup.

Test signals: default run prints top IP samples after five seconds; changing frequency/duration changes count volume.
