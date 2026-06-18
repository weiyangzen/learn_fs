# sources/distributed-fs/ceph-client/samples/bpf/lwt_len_hist.sh

Purpose: setup script for the lightweight tunnel packet-length histogram sample.

Important APIs/types/functions: uses `ip` route commands to attach/detach BPF programs and invokes the user helper to display map contents.

Control flow: configures a route with BPF LWT program, triggers or expects traffic through that route, invokes the userspace map reader, and provides cleanup path for route state.

State and persistence: modifies routing table state and may pin/load BPF objects depending on invocation.

Dependencies and integration: pairs with `lwt_len_hist.bpf.c` and `lwt_len_hist_user.c`, requires iproute2 with BPF LWT support and administrative privileges.

Risks: route changes can affect host networking. Cleanup must run to restore route state. The script is sensitive to interface/address arguments.

Test signals: route attachment succeeds, traffic reaches the route, histogram output is nonzero, and cleanup removes the BPF route.
