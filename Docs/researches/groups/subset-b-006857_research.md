# Research: subset-b-006857

This grouped report covers Linux kselftest source files from namespaces, NFC/NCI, AF_UNIX, net, BPF offload, and page-pool benchmark areas. Each section is source-tree aligned and intended to split directly into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/wrappers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/wrappers.h

Purpose: Provides a tiny compatibility wrapper for the `listns` namespace syscall used by namespace selftests. The file exists so tests can call a stable `sys_listns()` helper even when the userspace syscall number header does not yet define `__NR_listns`.

Important APIs/types/functions: Includes `<linux/nsfs.h>` for `struct ns_id_req`, `<linux/types.h>` for `__u64`, and syscall headers. It conditionally defines `__NR_listns` for alpha, MIPS o32/n32/n64, and default architectures, then exposes `static inline int sys_listns(const struct ns_id_req *req, __u64 *ns_ids, size_t nr_ns_ids, unsigned int flags)`.

Control flow: There is no runtime branching beyond the syscall itself. Compile-time preprocessor logic selects the numeric syscall constant, and `sys_listns()` forwards all arguments to `syscall(__NR_listns, ...)`.

State and persistence behavior: The wrapper owns no state. Any persistence is in kernel namespace state returned by the syscall into the caller-provided `ns_ids` buffer.

Dependencies and integration points: Depends on kernel UAPI types and libc `syscall()`. Integrated by namespace selftests that need to exercise new syscall behavior before all libc/kernel header combinations expose the number.

Risks: Hard-coded syscall numbers are architecture-sensitive; stale numbers would make tests fail with wrong syscalls or `ENOSYS`. The default number assumes most supported architectures use 470. It has no runtime feature detection.

Test signals: Successful consumers can compile without `__NR_listns` from libc and receive kernel return values from `listns`. Failures usually appear as build errors for missing `struct ns_id_req` or runtime syscall errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/wrappers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nci/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/nci/Makefile

Purpose: Builds the NFC Controller Interface selftest binary `nci_dev`.

Important APIs/types/functions: Adds linker and compiler flags via `CFLAGS += -Wl,-no-as-needed -Wall` and `LDFLAGS += -lpthread`, declares `TEST_GEN_PROGS := nci_dev`, and includes `../lib.mk`.

Control flow: Kselftest `lib.mk` consumes `TEST_GEN_PROGS` to compile `nci_dev.c` into a generated test program. `-lpthread` is required because the test uses worker threads to emulate virtual NCI device responses.

State and persistence behavior: Build-only file; generated binaries land in the kselftest output tree according to `lib.mk`.

Dependencies and integration points: Depends on the kselftest build framework and pthreads. It pairs with `config`, which requests NFC and virtual NCI kernel support.

Risks: `LDFLAGS` rather than target-specific `LDLIBS` may vary with kselftest make rules. Missing pthread linkage breaks the virtual device protocol helpers in `nci_dev.c`.

Test signals: `make -C tools/testing/selftests/nci` should produce `nci_dev`; running the test requires `/dev/virtual_nci` and NFC generic netlink support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nci/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/nci/config

Purpose: Declares the kernel configuration needed to run the NCI virtual-device selftest.

Important APIs/types/functions: Requests `CONFIG_NFC=y`, `CONFIG_NFC_NCI=y`, and `CONFIG_NFC_VIRTUAL_NCI=y`.

Control flow: Kselftest configuration tooling reads this file when preparing a kernel config for the `nci` test group.

State and persistence behavior: No runtime state. It influences kernel build configuration, enabling NFC core, NCI protocol support, and the virtual NCI character device.

Dependencies and integration points: Directly supports `nci_dev.c`, which opens `/dev/virtual_nci`, uses NFC generic netlink commands, and creates AF_NFC sockets.

Risks: If any option is built as absent, the test will fail early at device open, generic netlink family lookup, or AF_NFC socket creation.

Test signals: Presence of `/dev/virtual_nci`, NFC generic netlink family registration, and successful `nci_dev` execution confirm this config is effective.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nci/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nci/nci_dev.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/nci/nci_dev.c

Purpose: Exercises the Linux NFC/NCI stack through the virtual NCI device. It verifies device initialization/deinitialization, polling, target activation, AF_NFC raw socket connection, and Type 4 Tag read exchanges for both NCI 1.0 and NCI 2.0 command sequences.

Important APIs/types/functions: Uses generic netlink (`NETLINK_GENERIC`, `CTRL_CMD_GETFAMILY`, NFC generic netlink commands), `/dev/virtual_nci`, `IOCTL_GET_NCIDEV_IDX`, AF_NFC `SOCK_SEQPACKET` sockets, and kselftest harness fixtures. Helpers include `create_nl_socket()`, `send_cmd_mt_nla()`, `get_family_id()`, `send_cmd_with_idx()`, `get_nci_devid()`, `get_dev_enable_state()`, version-specific virtual-device responders (`virtual_dev_open*`, `virtual_deinit*`), polling helpers, tag discovery helpers, `read_write_nci_cmd()`, `read_tag()`, and `disconnect_tag()`.

Control flow: Fixture setup opens a generic netlink socket, resolves the NFC family and multicast group, opens `/dev/virtual_nci`, subscribes to events, gets the virtual device index, asserts the device is down, starts a responder thread, and sends `NFC_CMD_DEV_UP`. The responder reads exact NCI reset/init/discovery-map commands from the virtual device and writes canned responses. Tests then query state (`init`), start/stop polling (`start_poll`), simulate RF activation and Type 4 Tag APDU reads (`t4t_tag_read`), and explicitly power the device down (`deinit`). Teardown powers down the device if still open and closes descriptors.

State and persistence behavior: Fixture state tracks `virtual_nci_fd`, generic netlink socket, family id, pid, device index, protocol mask, NCI version, and whether the device is open. Kernel state under test includes NFC device powered state, poll state, target records, and AF_NFC socket lifecycle. No persistent files are written.

Dependencies and integration points: Requires `CONFIG_NFC`, `CONFIG_NFC_NCI`, `CONFIG_NFC_VIRTUAL_NCI`, NFC generic netlink, `/dev/virtual_nci`, pthreads, and kselftest harness. Integrates UAPI structures from `<linux/nfc.h>` and generic netlink headers.

Risks: The test uses exact byte-for-byte NCI command expectations, so benign kernel protocol changes can break it. Generic netlink attribute parsing is manual and lightly bounds-checked. Several helper functions return `0` on family lookup failure even though valid family id zero is unlikely; assertions only compare against `-1`. Thread status is cast through `void **`, which is conventional in this test but type-fragile. Closing `virtual_nci_fd` to test closed-device behavior leaves fixture teardown to handle `-1`.

Test signals: Passing assertions show device power transitions, NCI 1.0/2.0 startup handshakes, polling start/stop commands, target discovery, AF_NFC connect, APDU request/response flow, and down-state behavior. Failures identify mismatched NCI bytes, missing virtual device support, generic netlink errors, or unexpected powered state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nci/nci_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/Makefile

Purpose: Top-level build and run manifest for a broad set of networking selftests.

Important APIs/types/functions: Sets common `CFLAGS`, kernel header includes, `TEST_PROGS` shell/Python test scripts, `TEST_GEN_FILES` compiled helper binaries, `TEST_GEN_PROGS` harness binaries, `TEST_FILES`, YNL generation variables, target-specific `LDLIBS`/`CFLAGS`, and includes `../lib.mk`, `ynl.mk`, and `bpf.mk`.

Control flow: Kselftest `lib.mk` builds generated programs/files and arranges runnable scripts. The YNL section adds generated netlink tools (`busy_poller`, `netlink-dumps`, `tun`) before including `ynl.mk`. The final `include bpf.mk` builds BPF object files from `*.bpf.c`.

State and persistence behavior: Build outputs are placed under `$(OUTPUT)`. The Makefile itself is declarative and does not create runtime network state.

Dependencies and integration points: Coordinates many scripts in this subset (`altnames.sh`, `amt.sh`, `bareudp.sh`, `big_tcp.sh`, `bind_bhash.sh`, `bpf_offload.py`, bridge tests, broadcast tests, `busy_poll_test.sh`) and C programs (`bind_bhash`, `bind_timewait`, `bind_wildcard`). It also connects to kselftest forwarding library files and BPF/YNL build support.

Risks: Large manifests can drift when source files are added/removed. Some generated programs need optional libraries (`libcap`, `libnuma`, `pthread`, `crypto`), and missing dependencies surface at build time. BPF object generation depends on `clang`, libbpf, and kernel UAPI headers.

Test signals: A successful `make` in `tools/testing/selftests/net` builds all listed generated files and exposes scripts for `run_kselftest.sh`. Missing toolchain or library problems usually fail named target builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/Makefile

Purpose: Builds AF_UNIX-specific selftest binaries.

Important APIs/types/functions: Sets `top_srcdir`, includes `scripts/Makefile.compiler`, defines `cc-option`, adds `$(KHDR_INCLUDES) -Wall` and optional `-Wflex-array-member-not-at-end`, declares `TEST_GEN_PROGS` for `diag_uid`, `msg_oob`, `scm_inq`, `scm_pidfd`, `scm_rights`, `so_peek_off`, `unix_connect`, and `unix_connreset`, then includes `../../lib.mk`.

Control flow: Compiler feature detection adds a warning flag only when supported. Kselftest build rules compile each C file into a generated program.

State and persistence behavior: Build-only; generated binaries live under the kselftest output directory.

Dependencies and integration points: Requires kernel headers exposing newer AF_UNIX options such as `SO_PASSPIDFD`, `SO_PASSRIGHTS`, `SO_INQ`, `SO_PEEK_OFF`, and OOB support depending on individual tests.

Risks: Newer UAPI features can require up-to-date kernel headers; optional warning support avoids build failure on older compilers.

Test signals: Successful build produces all listed AF_UNIX test executables; runtime pass/fail is driven by each harness test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/config

Purpose: Declares kernel configuration needed by AF_UNIX selftests.

Important APIs/types/functions: Requests `CONFIG_AF_UNIX_OOB=y`, `CONFIG_UNIX=y`, and `CONFIG_UNIX_DIAG=m`.

Control flow: Consumed by kselftest config tooling.

State and persistence behavior: No runtime state. It ensures AF_UNIX sockets, urgent/OOB support, and UNIX socket diagnostic netlink are available.

Dependencies and integration points: Supports `msg_oob.c` for urgent data, `diag_uid.c` for `NETLINK_SOCK_DIAG`, and all AF_UNIX socket behavior tests.

Risks: If `UNIX_DIAG` is modular but not loaded, diagnostic tests may fail unless autoload works. Missing `AF_UNIX_OOB` breaks urgent-data semantics.

Test signals: Built kernel exposes AF_UNIX sockets, `SOCK_DIAG_BY_FAMILY` UNIX diagnostics, and OOB behavior required by this directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/diag_uid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/diag_uid.c

Purpose: Verifies that UNIX socket diagnostic netlink reports the owning UID for a selected AF_UNIX socket, both in the current user namespace and after `CLONE_NEWUSER`.

Important APIs/types/functions: Uses `NETLINK_SOCK_DIAG`, `SOCK_DIAG_BY_FAMILY`, `struct unix_diag_req`, `UNIX_DIAG_UID`, `SO_COOKIE`, `fstat()` inode lookup, and kselftest fixtures. Core helpers are `send_request()`, `receive_response()`, and `render_response()`.

Control flow: Fixture optionally unshares a user namespace, creates a netlink diagnostic socket and an AF_UNIX stream socket, records the socket inode and cookie, sends a targeted UNIX diag request with `UDIAG_SHOW_UID`, then receives one response and validates the UID attribute equals `getuid()`.

State and persistence behavior: State is limited to two file descriptors plus socket inode/cookie identifiers. It does not persist files or namespace state beyond process lifetime.

Dependencies and integration points: Requires `CONFIG_UNIX_DIAG`, AF_UNIX sockets, sock_diag netlink, and permission to unshare a user namespace for the second variant.

Risks: User namespace restrictions can make the unshare variant fail on hardened systems. The response parser assumes the first returned attribute is `UNIX_DIAG_UID` and only one matching message is returned.

Test signals: Passing output confirms UID rendering through UNIX diag and correct UID mapping after user namespace unshare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/diag_uid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/msg_oob.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/msg_oob.c

Purpose: Documents and verifies AF_UNIX stream `MSG_OOB` urgent-data behavior by comparing it against TCP behavior across normal, peek, inline, dropped, repeated, and reset scenarios.

Important APIs/types/functions: Uses `socketpair(AF_UNIX, SOCK_STREAM|SOCK_NONBLOCK)`, a loopback TCP pair, `MSG_OOB`, `MSG_PEEK`, `SO_OOBINLINE`, `SIOCATMARK`, `EPOLLPRI`, `SIGURG` via `FIOSETOWN` and `signalfd`, and kselftest fixtures. Helpers include `create_unix_socketpair()`, `create_tcp_socketpair()`, `setup_sigurg()`, `setup_epollpri()`, `__sendpair()`, `__recvpair()`, `__epollpair()`, `__siocatmarkpair()`, and `__resetpair()`.

Control flow: Fixture creates matching AF_UNIX and TCP endpoint pairs, registers SIGURG and EPOLLPRI on receivers, then each test sends normal or urgent bytes through both protocols. The helpers assert AF_UNIX return values, errno, data ordering, epoll readiness, and at-mark state, optionally relaxing TCP comparisons via `tcp_incompliant` for known TCP differences.

State and persistence behavior: Keeps four sockets, one signal fd, two epoll fds, and a `tcp_compliant` flag in fixture state. Urgent mark state and inline mode live in kernel socket state only.

Dependencies and integration points: Requires `CONFIG_AF_UNIX_OOB`, AF_UNIX stream OOB implementation, TCP loopback, epoll, signal delivery, and kselftest harness. The Makefile/config in the same directory expose the feature.

Risks: The test is intentionally semantic and strict; small changes in urgent pointer handling, reset behavior, or `SIOCATMARK` can break many cases. It uses nonblocking sockets and immediate `epoll_wait(..., timeout 0)`, so scheduling-sensitive signal delivery would be visible. TCP is used as a reference but has explicitly different behavior in several cases.

Test signals: Passing cases confirm `EPOLLPRI`, `SIGURG`, OOB read/drop, ordinary read break-at-OOB, repeated urgent-byte replacement, `SO_OOBINLINE`, `MSG_PEEK`, and reset semantics for AF_UNIX streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/msg_oob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/scm_inq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/scm_inq.c

Purpose: Tests `SO_INQ`/`SCM_INQ` ancillary reporting for AF_UNIX sockets and confirms it is stream-only.

Important APIs/types/functions: Uses `socketpair(AF_UNIX, type|SOCK_NONBLOCK)`, `setsockopt(SOL_SOCKET, SO_INQ)`, `recvmsg()` control messages, `SCM_INQ`, and `ioctl(SIOCINQ)`.

Control flow: The fixture runs variants for stream, datagram, and seqpacket socketpairs. The test enables `SO_INQ`; non-stream variants expect `ENOPROTOOPT`. For streams, it sends 100 chunks of 256 bytes, receives each with `recvmsg()`, extracts the `SCM_INQ` integer, and verifies it equals `SIOCINQ` after that receive.

State and persistence behavior: Only two socket descriptors. Queue depth is kernel socket receive buffer state.

Dependencies and integration points: Requires kernel support for AF_UNIX stream `SO_INQ` ancillary data and the kselftest harness.

Risks: The expected value depends on when `SCM_INQ` is sampled relative to the consumed message. Nonblocking sends assume the socket buffer can accept the configured total data.

Test signals: Passing stream test proves `SCM_INQ` is emitted and matches `SIOCINQ`; passing datagram/seqpacket variants prove unsupported types reject `SO_INQ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/scm_inq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/scm_pidfd.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/scm_pidfd.c

Purpose: Validates AF_UNIX `SCM_PIDFD`, `SO_PASSPIDFD`, and `SO_PEERPIDFD` behavior for live and exited peers over stream and datagram sockets with pathname and abstract addresses.

Important APIs/types/functions: Uses `SO_PASSCRED`, `SO_PASSPIDFD`, `SCM_CREDENTIALS`, `SCM_PIDFD`, `SO_PEERCRED`, `SO_PEERPIDFD`, pidfd fdinfo parsing, `PIDFD_GET_INFO`, shared `mmap()` for client addresses, `fork()`, `socket/bind/connect/listen/accept`, and kselftest fixtures.

Control flow: Parent creates and binds a server socket, forks a child client, and synchronizes through a pipe. The child connects, enables credential/pidfd passing, receives a byte from the parent, parses credentials and pidfd, and validates the pidfd points to the parent. It then sends a byte back and exits with a special success code. The parent waits for child exit, enables credential/pidfd passing on its endpoint, receives the child's message, and validates the received pidfd can report the dead child's exit code through `PIDFD_GET_INFO`.

State and persistence behavior: Fixture stores server fd, child pid, startup pipe, server address, and shared client address. Pathname socket files are unlinked in teardown; abstract sockets have no filesystem artifact.

Dependencies and integration points: Includes `../../pidfd/pidfd.h` for pidfd ioctl definitions. Requires modern AF_UNIX pidfd passing support and kernel pidfd info support.

Risks: Uses `/proc/self/fdinfo` text parsing to validate pidfds, so procfs availability matters. Teardown kills the child unconditionally; if it already exited, `kill()` may fail harmlessly but wait is still attempted. Datagram behavior differs from stream for peer credential getsockopt, and the code intentionally skips stream-only checks for datagrams.

Test signals: Passing variants confirm live peer pidfd delivery, credential co-delivery, dead process pidfd exit reporting, abstract/pathname address handling, and stream `SO_PEERPIDFD` parity with `SO_PEERCRED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/scm_pidfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/scm_rights.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/scm_rights.c

Purpose: Stress-tests AF_UNIX file-descriptor passing and garbage collection, including self-references, strongly connected components, listener sockets, stream/datagram variants, OOB sends, and the `SO_PASSRIGHTS` disable path.

Important APIs/types/functions: Uses `SCM_RIGHTS`, `SO_PASSRIGHTS`, `MSG_OOB`, `socketpair()`, unnamed bound/listening AF_UNIX sockets, `unshare(CLONE_NEWNET)`, and `/proc/net/protocols` socket counts.

Control flow: Fixture enters a new network namespace and, unless the disabled variant is being tested, asserts the relevant UNIX protocol socket count starts at zero. Helpers create socket pairs or listener/client pairs, send two copies of an inflight socket fd using `sendmsg()`, and close all local descriptors. Tests construct graph patterns: self reference, triangle cycles, cross edges, and backtracking from strongly connected components. Disabled variants expect `sendmsg()` with `SCM_RIGHTS` to fail with `EPERM`.

State and persistence behavior: Fixture stores up to 32 fds. The important state under test is in-flight file references held by AF_UNIX queues and kernel garbage collection. The teardown sleeps briefly then checks `/proc/net/protocols` count returns to zero.

Dependencies and integration points: Requires AF_UNIX fd passing, network namespaces, OOB support for OOB variants, and `/proc/net/protocols` visibility.

Risks: Socket-count assertions can be sensitive to unrelated AF_UNIX sockets in the same namespace, hence the test unshares netns. The cleanup check depends on GC completing within one second. Disabled listener variants only set `SO_PASSRIGHTS` on the receiver side selected by the test helper.

Test signals: Passing results indicate AF_UNIX GC collects cyclic in-flight references and enforces `SO_PASSRIGHTS=0` for fd passing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/scm_rights.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/so_peek_off.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/so_peek_off.c

Purpose: Verifies `SO_PEEK_OFF` offset advancement and reset semantics for AF_UNIX stream, datagram, and seqpacket sockets, including blocking receive paths.

Important APIs/types/functions: Uses `SO_PEEK_OFF`, `SO_RCVTIMEO_NEW`, `MSG_PEEK`, `socketpair()`, fork-based async send helper, and kselftest macros wrapping send/recv/getsockopt assertions.

Control flow: Fixture creates a socketpair for each type, sets a receive timeout, and initializes peek offset to zero. Tests send one or two chunks, perform peek reads to advance the offset, verify offset values, consume real data to reset or advance the offset, and use forked delayed sends to exercise blocking paths inside AF_UNIX receive logic.

State and persistence behavior: Only two socket fds. Kernel receive queues and the socket peek offset are the state under test. Child processes exit immediately after delayed sends.

Dependencies and integration points: Requires AF_UNIX `SO_PEEK_OFF` support and recent socket timeout option definitions.

Risks: The `async` macro forks inside tests and can complicate failure reporting. Timing uses `usleep(1000)` plus a 5-second receive timeout, so severe scheduling delays can stretch runtime. Stream and datagram/seqpacket expectations intentionally differ at skb boundaries.

Test signals: Passing cases prove peek offset increments across chunks, blocking receives resume correctly, stream reads fill buffers when possible, datagram/seqpacket preserve skb/message boundaries, and non-peek reads reset offset to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/so_peek_off.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/unix_connect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/unix_connect.c

Purpose: Tests AF_UNIX connect visibility across network namespace changes for pathname and abstract socket addresses.

Important APIs/types/functions: Uses `socket()`, `bind()`, `listen()`, `connect()`, `unshare(CLONE_NEWNET)`, `struct sockaddr_un`, pathname and abstract `sun_path`, and kselftest fixture variants.

Control flow: The server is bound in the original namespace. The test optionally unshares the network namespace before creating the client, then attempts to connect to the previously bound address. Pathname sockets are expected to remain reachable across netns because the filesystem path is shared, while abstract sockets in a new netns are expected to fail with `ECONNREFUSED`.

State and persistence behavior: Tracks server/client fds and removes the pathname socket file `test` in teardown. Abstract socket names are namespace-local and not persisted.

Dependencies and integration points: Requires AF_UNIX, network namespace support, and permissions to unshare.

Risks: Relative pathname `test` can collide if the test is run concurrently in the same directory. Abstract namespace behavior depends on network namespace isolation.

Test signals: Passing variants confirm expected connect behavior for stream/datagram, pathname/abstract, and same-netns/new-netns combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/unix_connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/unix_connreset.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/unix_connreset.c

Purpose: Documents AF_UNIX close/reset behavior for stream, datagram, and seqpacket sockets.

Important APIs/types/functions: Uses pathname AF_UNIX sockets, nonblocking clients, `listen()/accept()` for stream/seqpacket, `recv()`, and expected `EOF`, `ECONNRESET`, or `EAGAIN`.

Control flow: Fixture binds `/tmp/af_unix_connreset.sock`, listens for connection-oriented types, creates a nonblocking client, and connects. `eof` closes the peer normally and checks stream/seqpacket return EOF while datagram returns `EAGAIN`. `reset_unread_behavior` leaves unread data and checks stream/seqpacket `ECONNRESET` while datagram again sees `EAGAIN`. `reset_closed_embryo` closes the unaccepted server socket and expects reset for stream/seqpacket, marking datagram as XFAIL.

State and persistence behavior: Uses server, client, and accepted child descriptors. The socket pathname is unlinked before setup and in teardown.

Dependencies and integration points: Requires AF_UNIX connection semantics in the kernel and kselftest harness.

Risks: Uses a fixed `/tmp` socket path, so concurrent runs can interfere. Nonblocking datagram expectations rely on no queued data after server close.

Test signals: Passing tests confirm Linux's intended reset/EOF distinctions across AF_UNIX socket types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/unix_connreset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/altnames.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/altnames.sh

Purpose: Tests network device alternative names through `ip link property` and JSON `ip link show`.

Important APIs/types/functions: Sources forwarding `lib.sh`, defines `ALL_TESTS=altnames_test`, creates a dummy device, uses `ip link property add/del ... altname`, `ip -j -p link show`, `jq`, and kselftest `check_err/check_fail/log_test`.

Control flow: Setup creates `dummytest`. The test adds a short altname, verifies lookup by altname and JSON reporting, verifies lookup by original name, adds a long altname, verifies it appears as the second altname, deletes the short altname, and confirms lookup by the deleted name fails. Cleanup deletes the dummy device.

State and persistence behavior: Alters a temporary dummy netdevice's altname list. No persistent state remains after device deletion.

Dependencies and integration points: Requires iproute2 altname support, dummy netdevice support, `jq`, and forwarding lib helpers.

Risks: Assumes JSON altname array ordering matches insertion order. If cleanup fails, the dummy device can remain.

Test signals: Passing output confirms add/show/delete altname behavior and JSON visibility for short and long altnames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/altnames.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/amt.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/amt.sh

Purpose: End-to-end selftest for Automatic Multicast Tunneling (AMT) gateway/relay behavior with IPv4 and IPv6 multicast forwarding.

Important APIs/types/functions: Uses four network namespaces (`LISTENER`, `GATEWAY`, `RELAY`, `SOURCE`), veth links, bridge `br0`, AMT netdevices (`mode gateway` and `mode relay`), `smcrouted/smcroutectl`, iptables/ip6tables TTL/hop-limit mangling, `socat`, `nc`, `jq`, and `wait_local_port_listen` from `lib.sh`.

Control flow: The script checks iproute2 AMT support, creates namespaces, configures listener/gateway/relay/source topology, starts multicast routing, verifies gateway discovery reports the relay IP, runs IPv4 and IPv6 receive tests in the listener while source sends multicast datagrams, then sends larger repeated multicast traffic as torture. Cleanup deletes namespaces, kills `smcrouted`, and removes temp state.

State and persistence behavior: Creates temporary namespaces, veth devices, AMT devices, a bridge, multicast routes, firewall mangle rules, and a temp directory containing an AMT pid file. All are intended to be removed by trap cleanup.

Dependencies and integration points: Requires kernel AMT support, iproute2 AMT support, `smcrouted`, `socat`, `nc`, iptables/ip6tables, multicast routing, and root privileges.

Risks: External tools and timing dominate reliability. Background receive/send synchronization uses port-listen polling and timeouts. Torture traffic uses `/dev/urandom` and large sends, which can be slow. Cleanup depends on `ERR` and trap paths.

Test signals: OK messages for AMT discovery, IPv4 forwarding, IPv6 forwarding, and both torture sends indicate AMT tunnel setup and multicast forwarding work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/amt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/arp_ndisc_evict_nocarrier.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/arp_ndisc_evict_nocarrier.sh

Purpose: Tests IPv4 `arp_evict_nocarrier` and IPv6 `ndisc_evict_nocarrier` sysctls when a peer veth is brought down and the local link enters `NOCARRIER`.

Important APIs/types/functions: Uses `setup_ns/cleanup_ns` from `lib.sh`, veth pairs, `ip neigh get`, `ping`, per-interface and `all` sysctls for ARP/ND eviction, and root privilege checks.

Control flow: For IPv4 and IPv6 separately, setup creates veth connectivity, assigns addresses, applies the requested sysctl, establishes a neighbor entry by pinging, then brings the peer link down. Enabled tests expect the neighbor entry to be gone; disabled per-interface and disabled `all` tests expect it to remain. Cleanup resets sysctls to defaults and removes links/namespaces.

State and persistence behavior: Temporarily mutates host/network namespace sysctls, neighbor cache entries, veth devices, routes, and namespaces. Cleanup resets tested sysctls to `1`.

Dependencies and integration points: Requires root, `ip`, ping, veth, IPv6, and kselftest lib helpers.

Risks: IPv4 setup touches root namespace veth and default route, so failures before cleanup can disturb the environment. Neighbor creation can fail on systems with unusual MAC address policy, which the script notes. Sysctl inheritance from `all` can be subtle.

Test signals: `ok`/`failed` lines for six cases identify whether neighbor entries are evicted or preserved according to sysctl settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/arp_ndisc_evict_nocarrier.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/arp_ndisc_untracked_subnets.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/arp_ndisc_untracked_subnets.sh

Purpose: Tests acceptance of untracked ARP gratuitous updates and IPv6 unsolicited neighbor advertisements for same-subnet and off-subnet hosts.

Important APIs/types/functions: Uses `arp_accept`, `accept_untracked_na`, `drop_unsolicited_na`, `ndisc_notify`, veth namespaces, `arping`, `tc flower` counters for IPv6 NA observation, `ip neigh`, and `lib.sh` helpers.

Control flow: Command-line `-t` selects `arp`, `ndisc`, or both. ARP setup creates router/host namespaces, configures IPv4 addresses and router sysctl, sends gratuitous ARP from host, and verifies neighbor entry presence according to `arp_accept` values 0, 1, or 2 with same-subnet distinction. IPv6 setup creates veth namespaces, adds a `tc` ingress filter for NA packets, enables host notification, configures router forwarding and `accept_untracked_na`, waits for one NA packet, and verifies stale neighbor presence according to sysctl and subnet relation.

State and persistence behavior: Creates temporary namespaces, veths, sysctls, `tc` qdisc/filter state, and neighbor entries. Cleanup removes namespaces.

Dependencies and integration points: Requires root, `ip`, `tcpdump` presence check, `arping`, `tc`, IPv6, and `lib.sh`.

Risks: The IPv6 path relies on asynchronous unsolicited NA generation and `tc` packet counters. The script mutates global shell variables (`HOST_ADDR`, `HOST_ADDR_V6`) between cases, so cleanup/setup sequencing matters. It checks for `tcpdump` although it does not directly capture packets in this script.

Test signals: OK/FAIL lines for each ARP and ND combination show whether untracked neighbor advertisements are accepted only under configured modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/arp_ndisc_untracked_subnets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bareudp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bareudp.sh

Purpose: End-to-end test of BAREUDP tunnel devices transporting IPv4, IPv6, and MPLS over UDPv4 and UDPv6 underlays.

Important APIs/types/functions: Uses four namespaces, veth chain topology, `ip link add type bareudp`, `tc flower` + `tunnel_key` + `mirred` actions, MPLS sysctls/routes, IPv4/IPv6 forwarding sysctls, and ping reachability tests.

Control flow: The script checks iproute2 BAREUDP support and ping6 fallback, creates four namespaces in a chain, configures underlay veths and ingress qdiscs, sets overlay addresses/routes for IPv4, IPv6, and MPLS, then runs `test_overlay` for IPv4, IPv6, IPv4 multiproto, and MPLS unicast. Each overlay creates bareudp devices in the middle namespaces, programs encapsulation filters for UDPv4, pings, deletes filters, reprograms filters for UDPv6, pings again, then removes devices.

State and persistence behavior: Creates temporary namespaces, veths, bareudp devices, qdiscs, filters, routes, MPLS labels, and forwarding sysctls. Trap cleanup removes all namespaces.

Dependencies and integration points: Requires root, BAREUDP kernel/iproute2 support, `tc` tunnel actions, MPLS routing support for MPLS cases, IPv6, and kselftest `lib.sh`.

Risks: Multi-protocol tunnel behavior, MPLS support, and `tc` action availability vary by kernel config. The script sets `ERR=4` during setup so setup failures report SKIP rather than FAIL. Route/filter cleanup must run between underlay variants to avoid cross-test contamination.

Test signals: Printed `[ OK ]` ping tests for IPv4, IPv6, and MPLS over UDPv4/UDPv6 indicate successful encapsulation and decapsulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bareudp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/Makefile

Purpose: Kselftest manifest for networking benchmark tests, currently page-pool benchmark support.

Important APIs/types/functions: Sets `TEST_GEN_MODS_DIR := page_pool`, adds `test_bench_page_pool.sh` to `TEST_PROGS`, and includes `../../lib.mk`.

Control flow: Kselftest build rules descend into the `page_pool` module directory and expose the shell runner as a test program.

State and persistence behavior: Build artifacts include kernel module files under the output/module directory. No runtime state is created by the Makefile.

Dependencies and integration points: Integrates with `bench/page_pool/Makefile` to build `bench_page_pool.ko` and with `test_bench_page_pool.sh` to load it.

Risks: Requires a configured kernel build directory for module compilation. Benchmark modules may be skipped or fail on systems that cannot build/load modules.

Test signals: Successful build produces the page-pool module and test script in kselftest output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/Makefile

Purpose: Builds the `bench_page_pool.ko` kernel module from page-pool benchmark sources.

Important APIs/types/functions: Defines `KDIR ?= /lib/modules/$(shell uname -r)/build`, quiet/verbose `Q`, `obj-m += bench_page_pool.o`, and `bench_page_pool-y += bench_page_pool_simple.o time_bench.o`. `all` and `clean` invoke kernel module builds with `make -C $(KDIR) M=$(BENCH_PAGE_POOL_SIMPLE_TEST_DIR)`.

Control flow: Running `make` compiles the module against the selected kernel build tree; `clean` delegates cleanup to Kbuild.

State and persistence behavior: Produces module build artifacts in the source/output module directory depending on Kbuild invocation.

Dependencies and integration points: Requires a matching kernel build tree, module build support, and the two C files in this directory.

Risks: Building against headers for a different running kernel can produce an unloadable module. Tests require module load permissions.

Test signals: Presence of `bench_page_pool.ko` and successful `insmod` by the shell runner indicate build success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/bench_page_pool_simple.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/bench_page_pool_simple.c

Purpose: Kernel module benchmark for page-pool allocation and recycling paths, with baseline loop/atomic/spinlock measurements.

Important APIs/types/functions: Uses `page_pool_create()`, `page_pool_alloc_pages()`, `page_pool_recycle_direct()`, `page_pool_put_page()`, `page_pool_destroy()`, `in_serving_softirq()`, module params `run_flags` and `loops`, and timing helpers from `time_bench.h`. Benchmark functions include `time_bench_for_loop()`, `time_bench_atomic_inc()`, `time_bench_lock()`, `pp_fill_ptr_ring()`, `time_bench_page_pool()`, and wrappers for fast path, ptr_ring path, and page allocator slow path.

Control flow: On module init, the module validates `loops <= U32_MAX`, then `run_benchmark_tests()` conditionally runs baseline and page-pool benchmarks. `time_bench_page_pool()` creates a page pool, pre-fills its ptr_ring, times repeated allocation plus one of three return paths, destroys the pool, and logs per-element results.

State and persistence behavior: State is transient kernel module state, module parameters, allocated pages, a page_pool, and kernel log output. The module unload path only logs unload; benchmarks run at load time.

Dependencies and integration points: Requires kernel page_pool internals/helpers, module loading, and `time_bench.*`. The shell runner parses dmesg lines emitted by `time_bench_loop()`.

Risks: `page_pool_destroy(pp)` is called even after `page_pool_create()` returns an error pointer, which is risky if creation fails. Benchmarks are context-sensitive: comments note no-softirq context cannot activate the true fast path. Loop count can make module load slow.

Test signals: Dmesg lines named `for_loop`, `atomic_inc`, `lock`, `no-softirq-page_pool01`, `02`, and `03` with cycles/ns per element indicate benchmark execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/bench_page_pool_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/time_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/time_bench.c

Purpose: Provides reusable in-kernel timing and concurrent benchmark support for page-pool benchmarks.

Important APIs/types/functions: Implements `time_bench_PMU_config()`, `time_bench_calc_stats()`, `time_bench_loop()`, `time_bench_print_stats_cpumask()`, and `time_bench_run_concurrent()`. Uses TSC records from `time_bench.h`, wall-clock `timespec64`, optional perf/PMU counters, completions, atomics, CPU masks, and kthreads.

Control flow: `time_bench_loop()` initializes a record, calls a benchmark callback that wraps its own `time_bench_start/stop`, calculates stats, and logs per-call cycles and nanoseconds. Concurrent support spawns one kthread per selected CPU, pins each task, waits until all are ready, releases them with a completion, waits for completion counters to drop, then stops kthreads. PMU config attempts to create raw perf counters on the current CPU.

State and persistence behavior: Keeps static `perf_events[]` with saved perf_event pointers but does not use it in default page-pool benchmarks. Per-run state is held in `time_bench_record`, `time_bench_sync`, and `time_bench_cpu` structures. Output persists only in kernel logs.

Dependencies and integration points: Tightly paired with `time_bench.h` and benchmark modules. Depends on x86-like TSC helpers from the header, kernel timekeeping, kthreads, and perf events if PMU is enabled.

Risks: Comments mark PMU configuration as broken. TSC helpers are architecture-specific. `time_bench_run_concurrent()` returns immediately on kthread creation failure without stopping already-created tasks. Division logic requires loop counts under 2^32 and over 1000 for loop stats.

Test signals: Log lines with `Type:<name> Per elem:` and optional PMU IPC lines are consumed by `test_bench_page_pool.sh` and by humans comparing cycles/ns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/time_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/time_bench.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/time_bench.h

Purpose: Header API for in-kernel benchmark timing records, CPU concurrency records, and low-level timestamp helpers.

Important APIs/types/functions: Defines `struct time_bench_record`, measurement flags (`TIME_BENCH_LOOP`, `TIME_BENCH_TSC`, `TIME_BENCH_WALLCLOCK`, `TIME_BENCH_PMU`), `struct time_bench_sync`, `struct time_bench_cpu`, TSC helpers `tsc_start_clock()` and `tsc_stop_clock()`, PMU helpers (`p_rdpmc()`, `pmc_inst()`, `pmc_clk()`), prototypes for the C implementation, and inline `time_bench_start()` / `time_bench_stop()`.

Control flow: Benchmark callbacks call `time_bench_start()` before their measured loop and `time_bench_stop()` afterward with the invocation count. The inline helpers record wall-clock time, optional PMU counters, and serialized TSC values.

State and persistence behavior: No global state except constants and inline code. Records are caller-owned and later consumed by `time_bench_calc_stats()`.

Dependencies and integration points: Used by `bench_page_pool_simple.c` and implemented by `time_bench.c`. Depends on kernel `BIT`, atomics, completions, task structs, x86 asm instructions (`CPUID`, `RDTSC`, `RDTSCP`, `RDPMC`), and timekeeping APIs.

Risks: The TSC/PMU inline asm is not portable to all architectures and comments acknowledge guest/CPU flag constraints. PMU helpers require counters to be configured externally or by incomplete code. Some comments use outdated timekeeping API references.

Test signals: Correct integration yields populated records with TSC cycles, wall-clock intervals, and optional PMU counters printed by the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/time_bench.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/test_bench_page_pool.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/test_bench_page_pool.sh

Purpose: Runs the page-pool benchmark kernel module and extracts key result lines from `dmesg`.

Important APIs/types/functions: Uses `rmmod`, `insmod`, `dmesg | tail -10`, and grep regexes for `no-softirq-page_pool01/02/03` result lines.

Control flow: `run_test()` removes any existing module, inserts `./page_pool/bench_page_pool.ko`, captures recent kernel log output, prints it, then extracts fast path, ptr_ring, and slow path benchmark summaries. The script runs once and exits 0 if commands under `set -e` succeed.

State and persistence behavior: Loads a kernel module and leaves it loaded unless subsequent `rmmod` removes it on the next run. Kernel logs persist benchmark output.

Dependencies and integration points: Requires root/module load permission, the built module at the expected relative path, and `dmesg` visibility. Consumes output generated by `time_bench_loop()` in the module.

Risks: `dmesg | tail -10` can miss lines if other kernel logs interleave. The script does not unload the module after a successful run. Grep failures under `set -e` can fail the script if expected benchmark lines are absent.

Test signals: Printed result blocks for fast, ptr_ring, and slow path with cycles/ns values demonstrate module execution and expected log format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/test_bench_page_pool.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/big_tcp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/big_tcp.sh

Purpose: Tests IPv4 and IPv6 BIG TCP/GRO/GSO behavior across a routed three-namespace topology, including netfilter conntrack trimming interaction via `tc ct`.

Important APIs/types/functions: Uses client/router/server namespaces, veths, `gro_ipv4_max_size`, `gso_ipv4_max_size`, `gro_max_size`, `gso_max_size`, `ethtool -K` toggles, `tc flower action ct`, iptables/ip6tables raw length counters, `netserver`, and `netperf`.

Control flow: Setup configures namespaces, addresses, routes, BIG TCP device limits, forwarding, and conntrack `tc` filters, then starts `netserver`. For IPv4 and IPv6, `testup()` runs five combinations of client TSO, router GRO/GSO, and server GRO. Each `do_test()` enables counters for packets larger than 65535 bytes, runs a large-write TCP_STREAM netperf, verifies large packets appeared at router and server, removes counters, and reports pass/fail.

State and persistence behavior: Creates namespaces, veths, qdiscs/filters, netfilter raw rules, sysctls, netserver process, and offload settings. Trap cleanup kills netserver and removes namespaces/links.

Dependencies and integration points: Requires `netperf/netserver`, iproute2 support for BIG TCP link attributes, ethtool offload control, iptables/ip6tables, `tc ct`, IPv4/IPv6 forwarding, and root.

Risks: External netperf availability and timing affect results. The script uses `ip net exec` forms; environment must support that alias. Cleanup assumes router links exist. Counters are textual parsed with grep/awk, which can be brittle.

Test signals: PASS rows for all toggle combinations under `NF=4` and `NF=6`, followed by `***v4 Tests Done***` and `***v6 Tests Done***`, indicate large TCP packets traversed expected points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/big_tcp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_bhash.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_bhash.c

Purpose: Microbenchmark for measuring bind time when a port's bind hash table already contains many sockets.

Important APIs/types/functions: Uses pthreads, `getaddrinfo()`, `socket()`, `setsockopt(SO_REUSEPORT)`, `bind()`, `listen()`, `clock()`, and large constants `MAX_THREADS=600`, `MAX_CONNECTIONS=40`.

Control flow: Main parses port, address family, and bind address. It first binds and listens on loopback with `SO_REUSEPORT`, then starts 600 threads, each binding 40 additional `SO_REUSEPORT` sockets to the same setup address/port. After population, it times a bind without reuse options to a different provided address and prints elapsed CPU time.

State and persistence behavior: Holds up to 24,000 sockets plus a listener. No files are persisted. The wrapper script runs it in a network namespace with a raised fd limit.

Dependencies and integration points: Built as `bind_bhash` by the net Makefile and invoked by `bind_bhash.sh`.

Risks: Cleanup loop has an apparent bug: inner loop condition/increment use `i` instead of `j`, so descriptor cleanup is incorrect and can loop unexpectedly or skip closes. Global `ret` is written by threads without synchronization. Resource use is intentionally heavy and depends on `ulimit -n`.

Test signals: `time spent = <seconds>` indicates benchmark completion. Failures usually come from socket/bind/listen/resource exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_bhash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_bhash.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_bhash.sh

Purpose: Sets up a controlled namespace and invokes the `bind_bhash` microbenchmark for IPv4 or IPv6.

Important APIs/types/functions: Parses `-6`, `-4`, `-p`, and `-a`; creates a temporary netns with veth devices; configures loopback/veth addresses; sets `ulimit -n 32768`; runs `./bind_bhash`.

Control flow: Defaults to IPv6 port 443 and address `2001:0db8:0:f101::1`. Setup creates namespace and veth pair, brings devices up, and configures either IPv6 on veth0 or IPv4 on loopback. It then executes the benchmark inside the namespace with selected family and address, followed by namespace cleanup.

State and persistence behavior: Creates one temporary namespace and veth pair; cleanup deletes the namespace.

Dependencies and integration points: Requires root, `ip`, built `bind_bhash`, and enough file descriptor limit and memory for many sockets.

Risks: No trap is installed, so failures before cleanup can leave the namespace. It does not check return codes before cleanup. IPv4 setup uses loopback address while veth devices are also created.

Test signals: The child program's `time spent` output is the primary benchmark signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_bhash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_timewait.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_timewait.c

Purpose: Verifies that binding a new TCP socket to a port still occupied by a TIME_WAIT socket fails with `EADDRINUSE`.

Important APIs/types/functions: Uses IPv4 TCP sockets, kselftest fixture variants for `INADDR_LOOPBACK` and `INADDR_ANY`, `bind()`, `listen()`, `connect()`, `accept()`, `getsockname()`, and `errno`.

Control flow: Fixture initializes an ephemeral IPv4 address. Helper `create_timewait_socket()` binds/listens, connects a client, accepts, then closes child/client/server to create TIME_WAIT state. The test then opens a new TCP socket and attempts to bind to the same address/port, expecting `-1` and `EADDRINUSE`.

State and persistence behavior: TIME_WAIT state is held by the kernel TCP stack after sockets close. No persistent files.

Dependencies and integration points: Requires IPv4 loopback TCP support and kselftest harness.

Risks: TIME_WAIT ownership can depend on close ordering and TCP state transitions, but the test intentionally closes accepted child before client/server. Ephemeral port assignment is updated through `getsockname()`.

Test signals: Passing assertions prove bind conflict accounting includes TIME_WAIT sockets for both loopback and wildcard cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_timewait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_wildcard.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_wildcard.c

Purpose: Exhaustive matrix test for IPv4/IPv6 wildcard, loopback, v4-mapped, and `IPV6_V6ONLY` TCP bind conflict behavior, with and without `SO_REUSEADDR`/`SO_REUSEPORT`.

Important APIs/types/functions: Uses many fixture variants encoding two initial bind addresses, expected errno arrays for eight follow-up bind targets, optional `IPV6_V6ONLY`, and tests `plain`, `reuseaddr`, and `reuseport`. Helpers include `setup_addr()` and `bind_socket()`.

Control flow: Fixture prepares two variant-defined addresses and six canonical test addresses (`0.0.0.0`, `127.0.0.1`, `::`, `::1`, `::ffff:0.0.0.0`, `::ffff:127.0.0.1`). Each test iterates all eight binds on the same ephemeral port, sets v6-only/reuse options where applicable, binds, and checks success or `EADDRINUSE` against the variant's expected matrix. The first successful bind fixes the port via `getsockname()`.

State and persistence behavior: Uses up to eight socket descriptors per test. Kernel bind table conflict state is the target. No persistent files.

Dependencies and integration points: Requires IPv4, IPv6, v4-mapped address behavior, and kselftest harness.

Risks: Large variant matrix is maintenance-heavy; expectations encode Linux semantics in detail. Teardown closes all fd slots even if some were never assigned after failed setup paths.

Test signals: Passing across all variants demonstrates correct bind conflict resolution for wildcard/local/v4mapped/v6only combinations and reuse options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_wildcard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bpf.mk -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bpf.mk

Purpose: Shared make rules for building BPF object files and a local libbpf for networking selftests.

Important APIs/types/functions: Defines `CLANG`, `SCRATCH_DIR`, `BUILD_DIR`, `BPFDIR`, `APIDIR`, include paths, `BPFOBJ`, `MAKE_DIRS`, `get_sys_includes`, `CLANG_TARGET_ARCH`, `CLANG_SYS_INCLUDES`, `BPF_PROG_OBJS`, pattern rule for `$(OUTPUT)/%.o`, libbpf build rule, and `EXTRA_CLEAN`.

Control flow: It creates build directories, extracts host compiler include paths with `clang -v -E` and adds them as `-idirafter` for BPF target builds, handles cross-compile clang target selection, builds all `*.bpf.c` files into BPF ELF objects, and builds/installs libbpf headers into scratch output first.

State and persistence behavior: Writes generated BPF objects and scratch libbpf build/install output under `$(OUTPUT)/tools`. `EXTRA_CLEAN` removes scratch state.

Dependencies and integration points: Included by net Makefile. Requires clang with BPF target support, kernel UAPI headers, tools/lib/bpf, and make.

Risks: Host include extraction is shell/clang-output dependent. Cross-compilation target inference from `CROSS_COMPILE` is simple. RISC-V handling injects `__riscv_xlen`/`__BITS_PER_LONG` macros from clang preprocessing.

Test signals: Successful `BPF_PROG` and `MAKE libbpf` build lines and resulting `$(OUTPUT)/*.o` files indicate BPF selftest objects are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bpf.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bpf_offload.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bpf_offload.py

Purpose: Comprehensive Python selftest for BPF offload behavior using `netdevsim`, covering TC and XDP offload, extack messages, pinned programs/maps, device-bound metadata, namespace moves, map operations, and multi-device ASIC constraints.

Important APIs/types/functions: Wraps shell tools (`bpftool`, `ip`, `tc`, `ethtool`) and imports `NetdevSim`/`NetdevSimDev` from `lib.py`. Key classes are `DebugfsDir`, `BpfNetdevSimDev`, and `BpfNetdevSim`. Helper functions handle logging, skip/fail, command execution, bpftool lists and loads, netns creation, pinned program/map management, extack/verifier checks, multi-XDP checks, and cleanup.

Control flow: After root/tool/netdevsim/debugfs/sample checks, the script creates simulated devices and executes a long sequential suite: generic XDP destruction, TC non-offloaded and offloaded cases, default offload behavior, cBPF bytecode behavior, chain rejection, replace semantics, extack cleanliness, verifier failure path, TC offload metadata, disabling offloads with filters, qdisc/device destruction cleanup, XDP attach/replace/MTU/dev-bound/offload errors, multi-attachment XDP modes, TC/XDP mixing rejection, pinned program reuse, verifier-delay removal synchronization, map-backed offload reporting across namespaces and removed devices, map update/dump/getnext/delete behavior, map creation failure, and multi-device ASIC program/map reuse and destruction semantics.

State and persistence behavior: Creates netdevsim devices, debugfs control state, optional network namespaces, pinned BPF files under `/sys/fs/bpf`, loaded programs/maps, TC filters, XDP attachments, and log files. Global `devs`, `files`, and `netns` lists drive `finally` cleanup.

Dependencies and integration points: Requires root, `bpftool`, `ip`, `tc`, `ethtool`, `netdevsim`, debugfs, sample BPF objects (`sample_ret0.bpf.o`, `sample_map_ret0.bpf.o`), libbpf/bpftool JSON behavior, and iproute2 extack support for strict message checks.

Risks: The test is long and stateful; a missed cleanup can leave pinned objects or devices. It depends on specific netdevsim debugfs knobs and extack text. Some failure checks parse JSON error output or stderr exact strings. Busy-wait during verifier-delay test spins until bound-prog count changes.

Test signals: Each `start_test()` print indicates progress. Final `<script>: OK` means all BPF offload semantics passed. Failures include stack traces and optional org-mode log details.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bpf_offload.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bridge_stp_mode.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bridge_stp_mode.sh

Purpose: Tests bridge `stp_mode` netlink attribute behavior for user, kernel, and auto STP modes.

Important APIs/types/functions: Uses `ip link ... type bridge stp_mode/stp_state`, JSON `ip -d -j link show`, `jq`, kselftest `lib.sh` defer cleanup, and test functions listed in `ALL_TESTS`.

Control flow: After verifying iproute2 advertises `stp_mode`, setup creates a namespace. Tests check default `auto`, setting user/kernel/auto modes, rejecting mode changes while STP is active, allowing idempotent active-mode set and simultaneous disable+mode change, user mode in netns producing `stp_state=2`, kernel mode producing `stp_state=1`, auto fallback in netns, atomic mode+state setting, and mode persistence across disable/enable cycles.

State and persistence behavior: Creates temporary bridges inside one namespace and mutates bridge STP attributes. Defer scopes delete bridges and cleanup removes namespace.

Dependencies and integration points: Requires bridge driver support for `IFLA_BR_STP_MODE`, iproute2 support for the option, `jq`, and root namespace operations.

Risks: Exact JSON field names (`stp_mode`, `stp_state`) are iproute2-dependent. Tests assume no userspace `/sbin/bridge-stp` interaction inside non-init netns for auto mode.

Test signals: `log_test` results for nine cases validate mode defaults, transitions, rejection rules, and state mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bridge_stp_mode.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bridge_vlan_dump.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bridge_vlan_dump.sh

Purpose: Verifies bridge VLAN dump range grouping only combines consecutive VLANs whose per-VLAN options are identical.

Important APIs/types/functions: Uses `bridge vlan add/set/show`, `bridge mdb add/del`, bridge VLAN filtering with multicast snooping, `neigh_suppress`, `mcast_max_groups`, `mcast_n_groups`, `mcast_snooping`, kselftest `lib.sh`, and deferred cleanup.

Control flow: Setup creates a namespace, bridge `br0` with VLAN/multicast snooping enabled, and a dummy port. Each test adds VLANs 10 and 11, configures differing option values, checks `bridge -d vlan show` does not contain range `10-11` while individual entries exist, then makes option values match and checks the range appears.

State and persistence behavior: Creates bridge, dummy device, VLAN entries, MDB entries, and global bridge VLAN settings in a temporary namespace. Deferred cleanup removes added entries and namespace.

Dependencies and integration points: Requires iproute2 bridge support for per-VLAN neighbor suppression and multicast attributes, bridge VLAN filtering, and root.

Risks: Output parsing with grep regexes depends on bridge command formatting. It verifies only two adjacent VLANs and specific fields, not all possible VLAN dump attributes.

Test signals: Four `log_test` cases passing show range grouping respects `neigh_suppress`, `mcast_max_groups`, `mcast_n_groups`, and inherited multicast-enabled state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/bridge_vlan_dump.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/broadcast_ether_dst.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/broadcast_ether_dst.sh

Purpose: Ensures IPv4 broadcast packets are emitted with Ethernet destination `ff:ff:ff:ff:ff:ff`.

Important APIs/types/functions: Uses two namespaces with a veth pair, static ARP entry, `tcpdump` capture/readback, broadcast `ping -b`, and `lib.sh` helpers.

Control flow: Setup creates client/server namespaces, configures client IPv4 address and default route through a synthetic gateway MAC. The test starts tcpdump in the client namespace, sends one broadcast ping to `255.255.255.255`, waits for capture, reads Ethernet destination from the pcap, and compares it to the broadcast MAC.

State and persistence behavior: Creates temporary namespaces, veths, temp capture/output files, route and ARP entry. Cleanup removes files, link, and namespaces.

Dependencies and integration points: Requires `tcpdump`, root, ping, veth, and kselftest lib.

Risks: Capture timing uses a 2-second timeout and `slowwait` for tcpdump readiness. Temp filenames are generated with `mktemp -u`, which is race-prone but scoped to test usage.

Test signals: `[ OK ]` indicates captured Ethernet destination matched broadcast MAC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/broadcast_ether_dst.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/broadcast_pmtu.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/broadcast_pmtu.sh

Purpose: Tests that a broadcast route's MTU is respected for large broadcast pings.

Important APIs/types/functions: Uses two namespaces, veth with mismatched MTUs, local broadcast route manipulation, `ping -f -M want -s 8000 -b`, and ICMP broadcast response sysctl.

Control flow: Setup creates client/server namespaces and veth, sets client MTU 9000 and server MTU 1500, configures addresses, reads the client's local broadcast route, deletes it, re-adds it with MTU 1500, and enables broadcast echo replies on the server. The final command sends a large broadcast ping and the script exits with that result.

State and persistence behavior: Creates namespaces, veths, routes, and a server sysctl. Cleanup deletes link and namespaces.

Dependencies and integration points: Requires root, IPv4, ping supporting `-M want`, and route MTU handling.

Risks: It lacks explicit SKIP handling for missing tools. It relies on parsing `ip route show table local type broadcast` into an array and reusing it exactly.

Test signals: Exit status 0 from the large broadcast ping indicates route MTU behavior allowed correct fragmentation/PMTU handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/broadcast_pmtu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/busy_poll_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/busy_poll_test.sh

Purpose: Tests busy-poll socket receive behavior over linked `netdevsim` devices, including suspend timeout and threaded NAPI mode.

Important APIs/types/functions: Uses `netdevsim` sysfs (`new_device`, `del_device`, `link_device`, `unlink_device`), namespaces, `busy_poller` generated helper, `socat`, `md5sum`, NAPI/busy-poll parameters, and `wait_local_port_listen`.

Control flow: The script loads `netdevsim`, creates two simulated devices, moves them into server/client namespaces, assigns IP addresses, opens namespace fds and gets ifindexes, links the simulated devices through sysfs, then runs three tests. Each `test_busypoll()` creates random data, starts `busy_poller` server with configured busy-poll/suspend/threaded options, sends data via `socat`, waits for completion, and compares input/output MD5 sums. It unlinks/deletes devices and removes namespaces/module at the end.

State and persistence behavior: Creates netdevsim devices, sysfs link state, namespaces, namespace file descriptors, temp data files, and a loaded kernel module. Cleanup paths remove namespaces and module, though early failures perform partial cleanup.

Dependencies and integration points: Requires root, `netdevsim`, generated `busy_poller` binary from YNL build, `socat`, `md5sum`, `udevadm`, and sysfs netdevsim control files.

Risks: No global trap covers all failures; early exits may leave netdevsim devices or module loaded. Random ID selection can collide. `modprobe -r netdevsim` can fail if devices remain. Data transfer uses 30-second timeout.

Test signals: All three transfer MD5 comparisons passing and exit 0 validate ordinary busy poll, busy poll with suspend, and threaded NAPI busy-poll mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/busy_poll_test.sh -->
