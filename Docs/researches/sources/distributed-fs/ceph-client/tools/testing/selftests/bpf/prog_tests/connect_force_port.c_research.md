# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/connect_force_port.c

## Purpose
Tests cgroup connect/getpeername/getsockname programs that rewrite or report forced local and peer ports for IPv4/IPv6 TCP and UDP sockets.

## Important APIs, types, and functions
Uses `bpf_object__open_file()` to load either `connect_force_port4.bpf.o` or `connect_force_port6.bpf.o`, finds `.bss` initial value, attaches programs with `bpf_prog_attach()` to connect/getpeername/getsockname cgroup attach types, and checks sockets with `getsockname()`/`getpeername()`. `verify_ports()` compares host-order expected ports.

## Control flow and state
`test_connect_force_port()` joins `/connect_force_port`, starts four servers (IPv4/IPv6, stream/datagram), and runs `run_test()` for each. `run_test()` seeds BSS with the real server port before load, attaches three cgroup programs, connects, verifies expected local port 22222/22223 and peer port 60000, then closes the BPF object.

## Dependencies and integration points
Requires cgroup connect hooks, cgroup sock address hooks for name queries, IPv4/IPv6 sockets, and external `.bpf.o` files instead of skeletons. Integrated as a cgroup network selftest.

## Risks and test signals
Risk comes from port availability, BSS initial-value manipulation before load, and attach cleanup relying on object close. Passing signals are successful connection and exact observed local/peer port rewrites for all families/types.
