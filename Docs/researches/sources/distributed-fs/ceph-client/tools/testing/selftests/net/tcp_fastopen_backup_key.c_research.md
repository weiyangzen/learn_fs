# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_fastopen_backup_key.c

## Purpose
`tcp_fastopen_backup_key.c` stress-tests TCP Fast Open key rotation. It simulates multiple `SO_REUSEPORT` listeners behind a load balancer and verifies that staged primary/backup key rotation does not cause clients to present invalid cookies.

## Important APIs, Types, And Functions
Key functions are `get_keys()`, `set_keys()`, `build_rcv_fd()`, `connect_and_send()`, `is_listen_fd()`, `rotate_key()`, `run_one_test()`, `parse_opts()`, and `main()`. It uses `TCP_FASTOPEN`, `TCP_FASTOPEN_KEY`, `SO_REUSEPORT`, `MSG_FASTOPEN`, epoll, and optionally `/proc/sys/net/ipv4/tcp_fastopen_key`.

## Control Flow
`main()` parses `-4`, `-6`, `-s`, and `-r`, opens the proc fastopen key file, seeds random keys, and runs IPv4 or IPv6. `build_rcv_fd()` creates ten reuseport listeners, enables TFO, and installs the same initial key on each. `run_one_test()` loops 10000 times, sends one byte with `MSG_FASTOPEN`, accepts and receives the connection through epoll, and periodically rotates one listener. Rotation first installs a new backup key across listeners, then swaps backup and primary keys across listeners.

## State, Persistence, And Dependencies
State includes listener fds, process flags, current key length, random key material, and the proc fd. When not using socket options, the test writes the namespace-wide proc TFO key. It depends on TFO support, loopback networking, `SO_REUSEPORT`, and the wrapper script for namespace/sysctl setup and counter verification.

## Integration Points
This file is paired with `tcp_fastopen_backup_key.sh`, which runs it across IPv4/IPv6 and procfs/socket-option key paths. It exercises kernel TFO cookie validation while key rotation is partially rolled out across listeners.

## Risks
The test is randomized and long-running enough to expose race windows but may be sensitive to slow machines. Procfs writes use a fixed 128-byte buffer size rather than exact string length, which matches existing selftest behavior but is a point to watch. Key rotation state is static inside `rotate_key()`.

## Test Signals
The C program prints `PASS` on successful completion. The stronger end-to-end signal is the wrapper observing `TcpExtTCPFastOpenPassiveFail == 0` after each run mode.
