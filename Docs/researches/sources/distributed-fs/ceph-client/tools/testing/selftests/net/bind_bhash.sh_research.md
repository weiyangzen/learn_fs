# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_bhash.sh

Purpose: Sets up a controlled namespace and invokes the `bind_bhash` microbenchmark for IPv4 or IPv6.

Important APIs/types/functions: Parses `-6`, `-4`, `-p`, and `-a`; creates a temporary netns with veth devices; configures loopback/veth addresses; sets `ulimit -n 32768`; runs `./bind_bhash`.

Control flow: Defaults to IPv6 port 443 and address `2001:0db8:0:f101::1`. Setup creates namespace and veth pair, brings devices up, and configures either IPv6 on veth0 or IPv4 on loopback. It then executes the benchmark inside the namespace with selected family and address, followed by namespace cleanup.

State and persistence behavior: Creates one temporary namespace and veth pair; cleanup deletes the namespace.

Dependencies and integration points: Requires root, `ip`, built `bind_bhash`, and enough file descriptor limit and memory for many sockets.

Risks: No trap is installed, so failures before cleanup can leave the namespace. It does not check return codes before cleanup. IPv4 setup uses loopback address while veth devices are also created.

Test signals: The child program's `time spent` output is the primary benchmark signal.
