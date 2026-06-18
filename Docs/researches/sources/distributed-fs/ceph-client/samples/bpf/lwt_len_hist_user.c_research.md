# sources/distributed-fs/ceph-client/samples/bpf/lwt_len_hist_user.c

Purpose: reads and prints the packet-length histogram map for the LWT sample.

Important APIs/types/functions: `stars` helper and `main` that opens a pinned/known BPF map FD and iterates `MAX_INDEX` buckets.

Control flow: parses the map path or FD input, reads each bucket with `bpf_map_lookup_elem`, computes the maximum, and prints scaled ASCII bars.

State and persistence: no persistent state; reads map contents maintained by the attached BPF program.

Dependencies and integration: paired with `lwt_len_hist.bpf.c` and script setup, depends on libbpf/bpf syscall headers and a live histogram map.

Risks: assumes bucket count and value type match the BPF program. Output is only meaningful after traffic traverses the route.

Test signals: after LWT traffic, buckets corresponding to packet sizes show increasing counts.
