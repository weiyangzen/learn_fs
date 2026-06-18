
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nk_netns.py`

## Purpose
Selftests `NetDrvContEnv` by verifying IPv6 connectivity between a remote endpoint, the physical NIC, and a netkit-backed namespace created by the environment.

## Important APIs, Types, And Functions
- `test_ping(cfg)` requires IPv6, then runs one ping from the remote host to `cfg.nk_guest_ipv6` and one ping from the test netns to `cfg.remote_addr_v['6']`.
- `main()` creates `NetDrvContEnv(__file__)` and runs `test_ping`.

## Control Flow
Environment creation sets up the netkit pair, namespace routes, and tc BPF forwarding. The test then performs both traffic directions to prove forwarding and route setup work.

## State And Persistence
No local state is created beyond what `NetDrvContEnv` owns. Cleanup is delegated to the context manager, which removes tc filters, netkit links, namespace attachment, and IPv6 sysctl changes.

## Dependencies And Integration Points
Depends on `NetDrvContEnv`, `cmd`, remote command support, IPv6 configuration, and `nk_forward.bpf.o`. It is a small integration smoke test for the larger netkit queue lease setup.

## Risks
The test only sends one packet per direction, so it catches gross connectivity failures but not sustained forwarding, queue selection, or packet loss under load.

## Test Signals
Success is zero exit from both ping commands. `cfg.require_ipver("6")` produces a ksft skip if IPv6 endpoint data is missing.
