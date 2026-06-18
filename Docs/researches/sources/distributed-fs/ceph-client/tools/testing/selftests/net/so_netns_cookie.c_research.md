<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_netns_cookie.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_netns_cookie.c

## Purpose

`so_netns_cookie.c` tests `SO_NETNS_COOKIE`, ensuring sockets report nonzero cookies and distinct network namespaces have distinct cookie values.

## Important APIs, Types, and Functions

It uses `socket(AF_INET, SOCK_STREAM)`, `getsockopt(SOL_SOCKET, SO_NETNS_COOKIE)`, `unshare(CLONE_NEWNET)`, and 64-bit cookie storage. A fallback `#define SO_NETNS_COOKIE 71` supports older headers.

## Control Flow

The program creates a TCP socket in the initial namespace, reads and validates its cookie, unshares into a new network namespace, creates another TCP socket, reads and validates its cookie, then verifies the two cookies differ.

## State and Persistence Behavior

The only kernel state is a new network namespace and two sockets. Cookies are kernel-assigned namespace identifiers and persist for namespace lifetime, not beyond this process after exit.

## Dependencies and Integration Points

It depends on permission to `unshare(CLONE_NEWNET)` and kernel support for `SO_NETNS_COOKIE`. It integrates with socket namespace metadata and getsockopt ABI compatibility.

## Risks and Edge Cases

Unprivileged namespace restrictions can cause skip-like environmental failure, but the program returns a normal error. Header fallback can compile even when the running kernel lacks support, in which case getsockopt fails.

## Test Signals

Zero exit means both cookies are nonzero and distinct. Error output includes function/line and `errno` text through `pr_err`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_netns_cookie.c -->
