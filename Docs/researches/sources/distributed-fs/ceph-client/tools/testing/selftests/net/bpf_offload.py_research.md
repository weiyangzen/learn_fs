# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bpf_offload.py

Purpose: Comprehensive Python selftest for BPF offload behavior using `netdevsim`, covering TC and XDP offload, extack messages, pinned programs/maps, device-bound metadata, namespace moves, map operations, and multi-device ASIC constraints.

Important APIs/types/functions: Wraps shell tools (`bpftool`, `ip`, `tc`, `ethtool`) and imports `NetdevSim`/`NetdevSimDev` from `lib.py`. Key classes are `DebugfsDir`, `BpfNetdevSimDev`, and `BpfNetdevSim`. Helper functions handle logging, skip/fail, command execution, bpftool lists and loads, netns creation, pinned program/map management, extack/verifier checks, multi-XDP checks, and cleanup.

Control flow: After root/tool/netdevsim/debugfs/sample checks, the script creates simulated devices and executes a long sequential suite: generic XDP destruction, TC non-offloaded and offloaded cases, default offload behavior, cBPF bytecode behavior, chain rejection, replace semantics, extack cleanliness, verifier failure path, TC offload metadata, disabling offloads with filters, qdisc/device destruction cleanup, XDP attach/replace/MTU/dev-bound/offload errors, multi-attachment XDP modes, TC/XDP mixing rejection, pinned program reuse, verifier-delay removal synchronization, map-backed offload reporting across namespaces and removed devices, map update/dump/getnext/delete behavior, map creation failure, and multi-device ASIC program/map reuse and destruction semantics.

State and persistence behavior: Creates netdevsim devices, debugfs control state, optional network namespaces, pinned BPF files under `/sys/fs/bpf`, loaded programs/maps, TC filters, XDP attachments, and log files. Global `devs`, `files`, and `netns` lists drive `finally` cleanup.

Dependencies and integration points: Requires root, `bpftool`, `ip`, `tc`, `ethtool`, `netdevsim`, debugfs, sample BPF objects (`sample_ret0.bpf.o`, `sample_map_ret0.bpf.o`), libbpf/bpftool JSON behavior, and iproute2 extack support for strict message checks.

Risks: The test is long and stateful; a missed cleanup can leave pinned objects or devices. It depends on specific netdevsim debugfs knobs and extack text. Some failure checks parse JSON error output or stderr exact strings. Busy-wait during verifier-delay test spins until bound-prog count changes.

Test signals: Each `start_test()` print indicates progress. Final `<script>: OK` means all BPF offload semantics passed. Failures include stack traces and optional org-mode log details.
