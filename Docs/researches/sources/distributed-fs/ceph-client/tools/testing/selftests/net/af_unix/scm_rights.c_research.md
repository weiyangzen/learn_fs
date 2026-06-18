# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/scm_rights.c

Purpose: Stress-tests AF_UNIX file-descriptor passing and garbage collection, including self-references, strongly connected components, listener sockets, stream/datagram variants, OOB sends, and the `SO_PASSRIGHTS` disable path.

Important APIs/types/functions: Uses `SCM_RIGHTS`, `SO_PASSRIGHTS`, `MSG_OOB`, `socketpair()`, unnamed bound/listening AF_UNIX sockets, `unshare(CLONE_NEWNET)`, and `/proc/net/protocols` socket counts.

Control flow: Fixture enters a new network namespace and, unless the disabled variant is being tested, asserts the relevant UNIX protocol socket count starts at zero. Helpers create socket pairs or listener/client pairs, send two copies of an inflight socket fd using `sendmsg()`, and close all local descriptors. Tests construct graph patterns: self reference, triangle cycles, cross edges, and backtracking from strongly connected components. Disabled variants expect `sendmsg()` with `SCM_RIGHTS` to fail with `EPERM`.

State and persistence behavior: Fixture stores up to 32 fds. The important state under test is in-flight file references held by AF_UNIX queues and kernel garbage collection. The teardown sleeps briefly then checks `/proc/net/protocols` count returns to zero.

Dependencies and integration points: Requires AF_UNIX fd passing, network namespaces, OOB support for OOB variants, and `/proc/net/protocols` visibility.

Risks: Socket-count assertions can be sensitive to unrelated AF_UNIX sockets in the same namespace, hence the test unshares netns. The cleanup check depends on GC completing within one second. Disabled listener variants only set `SO_PASSRIGHTS` on the receiver side selected by the test helper.

Test signals: Passing results indicate AF_UNIX GC collects cyclic in-flight references and enforces `SO_PASSRIGHTS=0` for fd passing.
