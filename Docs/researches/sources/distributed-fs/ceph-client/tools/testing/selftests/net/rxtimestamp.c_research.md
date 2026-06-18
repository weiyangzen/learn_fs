<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rxtimestamp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rxtimestamp.c

## Purpose

`rxtimestamp.c` validates receive timestamp socket options and control messages across raw IP, UDP, and TCP sockets over IPv4 and IPv6 loopback. It checks legacy `SO_TIMESTAMP`, `SO_TIMESTAMPNS`, and `SO_TIMESTAMPING` flag combinations.

## Important APIs, Types, and Functions

Core data structures are `struct options`, `struct tstamps`, `struct socket_type`, `struct test_case`, and `struct sof_flag`. Static arrays enumerate socket types and timestamping test cases. Important functions are `print_test_case`, `do_send`, `do_recv`, `config_so_flags`, `run_test_case`, and `main`.

The key kernel APIs are `socket`, `bind`, `listen`, `connect`, `accept`, `setsockopt(SO_TIMESTAMP/SO_TIMESTAMPNS/SO_TIMESTAMPING/SO_REUSEADDR)`, `recvmsg`, ancillary data parsing with `CMSG_FIRSTHDR`/`CMSG_NXTHDR`, and `struct scm_timestamping` from `linux/net_tstamp.h`.

## Control Flow

`main` parses long options to select protocols, address families, test number, payload size, strict mode, or list mode. It iterates selected socket types and test cases for IPv4 and/or IPv6. `run_test_case` creates source and destination sockets, binds destination loopback, listens and accepts for TCP, configures timestamp options on the receive socket, sends a payload, and validates the received control messages.

## State and Persistence Behavior

Global mutable state includes `next_port`, `op_size`, and enabled flags inside the static test and socket arrays. Runtime socket state is short-lived per case. Timestamp configuration is per-socket and released on close. The program does not persist files or kernel configuration.

## Dependencies and Integration Points

It uses kselftest helpers for `ARRAY_SIZE` and standard Linux timestamping ABI headers. `rxtimestamp.sh` runs it inside a fresh namespace. It depends on loopback networking, raw socket permissions for IP tests, and kernel support for the timestamp options being validated.

## Risks and Edge Cases

Raw IPv4 receives include the IPv4 header and therefore adjust expected payload size. `SO_TIMESTAMPING` setup is followed by a fixed sleep because option effects can be asynchronous. Hardware timestamp tests on loopback expect no hardware timestamp. `warn_on_fail` softens one software timestamping case unless strict mode is requested.

## Test Signals

Success prints `PASSED.` with zero failures. Failures identify missing or unexpected cmsgs, truncation, wrong payload size, or nonzero timestamp slots where none are expected. `--list_tests` is a useful inventory signal for the encoded test matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rxtimestamp.c -->
