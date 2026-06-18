# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_helper.c

## Purpose
`xdp_helper.c` is a userspace AF_XDP socket binder used by queue/XSK tests to verify kernel XDP socket state and optional zerocopy support.

## Important APIs and Functions
`main` accepts `ifindex queue_id [-z]`. It creates an `AF_XDP` socket, supports probe mode with `- -`, allocates UMEM with `mmap`, registers UMEM and fill/completion/RX rings through `setsockopt`, then binds `sockaddr_xdp` to the requested interface queue. `print_usage` documents syntax. It uses `ksft_ready` and `ksft_wait` for parent-controlled lifetime.

## Control Flow and State
After setup, `bind` is retried up to three times on `EBUSY`. In normal mode, successful bind reports readiness and blocks until the parent writes the wait byte. Runtime state is the AF_XDP socket, UMEM mapping, and ring configuration; no files are persisted.

## Dependencies and Integration
It depends on Linux AF_XDP, `linux/if_xdp.h`, `ksft.h`, and root/capabilities. Python background helpers can start it with readiness waits. Queue tests inspect kernel-visible XSK association while this process keeps the socket open.

## Risks and Test Signals
If the kernel lacks AF_XDP, socket creation returns `EAFNOSUPPORT` and the program exits `-1` to signal unsupported rather than generic failure. Most setup `setsockopt` calls are not checked, so failures may surface only at bind. Success signals are `AF_XDP support detected` in probe mode or a `ready\n` handshake after bind.
