<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_fanout.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_fanout.c

## Purpose

`psock_fanout.c` validates AF_PACKET `PACKET_FANOUT` control rules and datapath distribution. It checks illegal fanout creation/join combinations, unique group ID allocation, maximum-member handling, and packet distribution for HASH, HASH with rollover, load-balance, CPU, rollover, CBPF, EBPF, and unique-ID fanout modes.

## Important APIs, Types, and Functions

Important helpers are `loopback_set_up_down`, `sock_fanout_open`, `sock_fanout_set_cbpf`, `sock_fanout_set_ebpf`, `sock_fanout_getopts`, `sock_fanout_open_ring`, `sock_fanout_read_ring`, `test_unbound_fanout`, `test_control_single`, `test_control_group`, `test_control_group_max_num_members`, `test_unique_fanout_group_ids`, `test_datapath`, and `set_cpuaffinity`. It uses `PF_PACKET` raw sockets, `SOL_PACKET`/`PACKET_FANOUT`, `PACKET_FANOUT_DATA`, `PACKET_RX_RING`, `TPACKET_V2`, `mmap`, classic BPF, `bpf(BPF_PROG_LOAD)` socket filters, and helpers from `psock_lib.h`.

## Control Flow

Main first runs control-plane tests that expect specific fanout errors or successes, including link-down join behavior and unique ID behavior. It then uses `test_datapath` to create two packet sockets in one fanout group, attach optional CBPF/EBPF selectors, map RX rings, create two UDP socket pairs, send known payload counts, and verify that ring queue lengths match expected distributions. HASH mode may retry with different UDP ports to avoid hash collisions. CPU mode pins execution to CPU 0 and, if possible, CPU 1.

## State and Persistence Behavior

State is transient packet sockets, mapped rings, loaded BPF programs, UDP sockets, and temporary loopback up/down changes. BPF program FDs are closed after being attached through `PACKET_FANOUT_DATA`. All sockets and mappings are closed or unmapped before returning.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include AF_PACKET, packet fanout support, TPACKET rings, loopback, BPF syscall support for EBPF cases, CPU affinity, and enough privileges for raw packet sockets and interface flag toggling. Integration is with packet socket fanout group semantics and BPF fanout selectors. Risks include hash collisions exhausting retries, CPU affinity not allowing CPU 1, queue overflow assumptions, exact group-option behavior changing, and environmental capability failures. Signals are expected create/join failures, unique IDs distinct and joinable only correctly, expected ring counts printed as `count=..., expect=...`, and final `OK. All tests passed`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_fanout.c -->
