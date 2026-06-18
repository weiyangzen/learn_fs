# sources/distributed-fs/ceph-client/net/phonet/sysctl.c

## Purpose
`sysctl.c` implements `/proc/sys/net/phonet/local_port_range`, the runtime tunable used by Phonet automatic port allocation.

## Important APIs, types, and functions
`phonet_get_local_port_range()` exports a lockless-reader API using a seqlock. `proc_local_port_range()` validates sysctl reads/writes with `proc_dointvec_minmax()`, enforces `min <= max`, and updates the range via `set_local_port_range()`. `phonet_sysctl_init()` and `phonet_sysctl_exit()` register/unregister the sysctl table.

## Control flow and state
The default dynamic range is `0x40..0x7f`, with accepted values bounded by `0..1023`. Readers loop with `read_seqbegin()`/`read_seqretry()` until they see a consistent range. Writers copy through a temporary table so invalid writes do not partially update global state, then publish both values under `write_seqlock()`.

## State and persistence behavior
`local_port_range` is global in-memory state for init_net sysctl registration. It affects future automatic port allocation in `pn_sock_get_port()` but does not rebind existing sockets. It is not persistent across reboot/module unload unless userspace reapplies sysctl settings.

## Dependencies and integration points
The main consumer is `pn_sock_get_port()` in `socket.c`. The sysctl path is registered by `phonet_init()` in `af_phonet.c` and removed during module exit.

## Risks and edge cases
Risks include invalid range handling, seqlock misuse, and namespace expectations. The sysctl is registered under `init_net`, so it is global rather than per network namespace. Port range changes can cause allocation failures if all ports in the range are occupied.

## Test signals
Read/write `/proc/sys/net/phonet/local_port_range`, reject reversed ranges and values outside `0..1023`, verify concurrent readers see consistent pairs, and confirm autobind chooses ports within the configured range.
