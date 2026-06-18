# sources/distributed-fs/ceph-client/samples/bpf/lathist_user.c

Purpose: userspace display for the preemption latency histogram BPF sample.

Important APIs/types/functions: `struct cpu_hist`, `stars`, `print_hist`, `get_data`, and `main` using libbpf program attach and map lookup APIs.

Control flow: opens and loads the kernel object, attaches programs, repeatedly reads histogram map entries, computes per-CPU maxima, and prints ASCII bar charts.

State and persistence: process-local `cpu_hist` mirrors BPF map data; BPF links live until process exit.

Dependencies and integration: pairs with `lathist_kern.c`, requires libbpf and kprobe permissions.

Risks: fixed CPU and bucket counts must match kernel side. Continuous terminal printing can obscure errors. No explicit signal cleanup path beyond process termination.

Test signals: attach successfully, induce preemption-off activity, and verify histogram bars grow.
