<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_features.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_features.c

## Purpose
This XDP feature test program validates different XDP actions and redirect paths using recognizable UDP echo packets exchanged between tester and device-under-test addresses.

## Important APIs, Types, and Functions
It defines stats maps `stats` and `dut_stats`, `cpu_map`, and `dev_map`, plus volatile config globals `tester_addr` and `dut_addr`. Helpers include `bpf_redirect_map`, tracepoint BPF_PROG wrappers, and atomic `__sync_add_and_fetch`. Shared helpers `xdp_process_echo_packet()` and `xdp_update_stats()` parse IPv4/IPv6 UDP packets carrying `CMD_ECHO` from `xdp_features.h`.

## Control Flow
Tester programs count TX/RX echo packets and pass them. DUT programs pass, drop, abort, TX by swapping Ethernet addresses, or redirect to CPUMAP/DEVMAP after validating the echo packet. Tracepoint programs for `xdp_exception` and `xdp_cpumap_kthread` increment DUT stats. The cpumap program swaps MAC addresses and redirects to a devmap.

## State and Persistence
Array maps persist counters. Volatile global addresses configure packet matching. Packet mutation occurs in TX and cpumap redirect paths through Ethernet MAC swaps.

## Dependencies and Integration Points
The program integrates with XDP feature selftests, CPUMAP/DEVMAP infrastructure, and BTF tracepoints. It depends on `xdp_features.h` for TLV command definitions and ports.

## Risks
Strict packet matching means unrelated packets are ignored or passed. The code assumes simple IPv4/IPv6 UDP without extension headers. Counters are updated atomically but are simple 32-bit values.

## Test Signals
Userspace should see expected stats increments in `stats`/`dut_stats` for pass/drop/aborted/tx/redirect paths and tracepoint activity for exceptions or cpumap processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_features.c -->
