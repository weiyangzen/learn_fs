<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skc_to_unix_sock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skc_to_unix_sock.c

Purpose: this test validates the `bpf_skc_to_unix_sock()` conversion path for Unix sockets by triggering a Unix listen operation and checking that the BPF program captured the abstract socket path.

Important APIs/types/functions: `test_skc_to_unix_sock()` opens `test_skc_to_unix_sock.skel.h`, sets rodata `my_pid`, loads and attaches the skeleton, creates an `AF_UNIX` stream socket, binds it to an abstract path, calls `listen()`, and compares skeleton BSS `path` with `sock_path`.

Control flow: open skeleton, set PID filter, load, attach, create Unix socket, initialize `sockaddr_un` with `sun_path[0] = '\0'` for abstract namespace, bind, listen, assert the captured path string matches `"@skc_to_unix_sock"`, then close/destroy.

State and persistence: state is one Unix socket FD, skeleton rodata/BSS, and transient abstract Unix namespace entry. No filesystem socket path is created because the address is abstract.

Dependencies: requires the paired BPF skeleton, Unix domain sockets, BPF attach point used by the BPF program for `unix_listen`, and kernel support for converting `sock_common` to `unix_sock`.

Integration points: exercises BTF/kfunc or helper-based socket type conversion from a kernel socket context into Unix-specific fields, using a real userspace bind/listen trigger.

Risks: abstract Unix path formatting is subtle: the userspace string stores `"@..."` but the sockaddr uses a leading NUL. If BPF-side path normalization changes, the string comparison will fail. The socket FD is initialized to `0`, so cleanup closes it only after successful positive FD creation.

Test signals: successful load/attach, successful abstract Unix bind/listen, and exact BSS path match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skc_to_unix_sock.c -->
