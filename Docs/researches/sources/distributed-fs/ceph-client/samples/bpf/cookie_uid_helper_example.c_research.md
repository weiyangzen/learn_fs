# sources/distributed-fs/ceph-client/samples/bpf/cookie_uid_helper_example.c

Purpose: demonstrates `bpf_get_socket_cookie` and `bpf_get_socket_uid` helpers for per-socket traffic accounting through a socket filter attached via iptables `xt_bpf`.

Important APIs/types/functions: defines `struct stats`, `maps_create`, `prog_load`, `prog_attach_iptables`, `print_table`, `udp_client`, `finish`, and `main`. Uses manual BPF instruction macros, `BPF_MAP_TYPE_HASH`, `BPF_PROG_TYPE_SOCKET_FILTER`, `bpf_obj_pin`, `iptables -m bpf --object-pinned`, UDP sockets, and `SO_COOKIE`.

Control flow: creates a hash map keyed by socket cookie, loads a hand-written BPF program that looks up or creates stats and atomically increments packet/byte counters, pins the program, attaches an iptables OUTPUT rule, then either prints map contents until signaled or sends loopback UDP packets and verifies per-cookie stats.

State and persistence: BPF map and program FDs live in process state. The pinned program and iptables rule can persist if not cleaned by the wrapper script; the sample closes FDs but does not remove iptables rules itself.

Dependencies and integration: requires libbpf, xt_bpf-capable iptables, BPF filesystem pinning, root privileges, and `run_cookie_uid_helper_example.sh` for setup/cleanup.

Risks: invokes `system("iptables ...")` with a path-length check but still depends on shell/iptables behavior. Cleanup is external. Manual BPF instructions and atomic map updates require verifier compatibility. The map key is `uint32_t` while socket cookies are read as `uint64_t` in the UDP client, which is sample-specific and can be confusing.

Test signals: run the wrapper with `-s` to confirm UDP cookie stats and with `-t` to observe live traffic counters; verify iptables and BPF pin cleanup after signals.
