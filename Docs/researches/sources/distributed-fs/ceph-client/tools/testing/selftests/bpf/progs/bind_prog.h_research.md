<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind_prog.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind_prog.h

## Purpose

Shared constants for cgroup bind selftests, defining the target port range and interface index used by IPv4 and IPv6 bind hooks.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

Control starts at the cgroup bind hook. The program inspects `bpf_sock_addr`, optionally rewrites `user_ip*` and `user_port`, sets or reads socket options, and returns 1 to allow or 0 to deny. There is no loop or persistent per-socket state beyond socket option effects.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Integrates with cgroup bind4/bind6 attach points and socket option helpers.

## Risks and Edge Cases

Socket option rewrites must preserve endian handling and address family layout; deny hooks can make tests fail by blocking unrelated binds if attached too broadly.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Bind/connect attempts on allowed, rewritten, device-bound, reuseport, and denied cases should match expected errno and socket address results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind_prog.h -->
