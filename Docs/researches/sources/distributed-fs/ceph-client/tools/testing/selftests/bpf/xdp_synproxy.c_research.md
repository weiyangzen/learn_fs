# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_synproxy.c

## Purpose

`xdp_synproxy.c` is a userspace controller for an XDP/TC SYN-cookie proxy BPF program. It can attach the companion BPF object to an interface, discover an already attached program by ID, update TCP/IP option and allowed-port maps, and periodically report the total number of generated SYNACKs.

## Important APIs, Types, and Functions

Global state tracks `ifindex`, `attached_prog_id`, and whether a TC hook was attached. Key functions are `cleanup`, `usage`, `parse_arg_ul`, `parse_options`, `syncookie_attach`, `syncookie_open_bpf_maps`, and `main`. It uses libbpf BPF object loading, `bpf_xdp_attach`, `bpf_xdp_query_id`, `bpf_tc_hook_create`, `bpf_tc_attach`, `bpf_tc_hook_destroy`, `bpf_prog_get_info_by_fd`, `bpf_map_get_info_by_fd`, and map update/lookup APIs.

## Control Flow

CLI parsing requires either `--iface` or `--prog`, validates optional `--mss4/--mss6/--wscale/--ttl` as an all-or-nothing TCP/IP option tuple, parses comma-separated `--ports`, and handles `--single`/`--tc`. If no program ID is provided, it queries an existing XDP program or loads `<argv0>_kern.bpf.o` and attaches `syncookie_xdp` or `syncookie_tc`. It opens maps named `values` and `allowed_ports`, updates requested options/ports, then either exits after configuration or loops reading counter key `1`.

## State and Persistence Behavior

External state includes XDP or TC ingress attachments and BPF map contents. Signal cleanup detaches only programs attached by this process; map updates persist while the BPF program/map lives.

## Dependencies and Integration Points

It depends on a companion kernel object with `syncookie_xdp`/`syncookie_tc`, maps named `values` and `allowed_ports`, libbpf, netdev ifindex resolution, and privileges for XDP/TC/map operations.

## Risks and Test Signals

Risks include map-name coupling, stale TC hook if attach partially fails, conflicting existing XDP programs, port-list overflow relative to map size, and option packing assumptions. Signals are successful attach/discover, map fd discovery, printed port/option updates, increasing SYNACK counters, and clean detach on SIGINT/SIGTERM for process-owned attachments.
