<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/nlattr.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/nlattr.h

## Purpose
This internal header defines libbpf's netlink attribute type policy model, request buffer type, iteration macros, payload accessors, and inline request-building helpers.

## APIs, Types, and Functions
It defines `LIBBPF_NLA_*` validation type constants and `LIBBPF_NLA_TYPE_MAX`, `struct libbpf_nla_policy` with type/minlen/maxlen, and `struct libbpf_nla_req`, which contains a `nlmsghdr`, a union for `ifinfomsg`, `tcmsg`, or `genlmsghdr`, and a fixed 128-byte attribute buffer. Iteration and accessor APIs include `libbpf_nla_for_each_attr`, `libbpf_nla_data()`, typed getters for u8/u16/u32/u64/string, `libbpf_nla_len()`, parser declarations, `libbpf_nla_dump_errormsg()`, `nla_data()`, `req_tail()`, `nlattr_add()`, `nlattr_begin_nested()`, and `nlattr_end_nested()`.

## Control Flow, State, and Persistence
Inline getters compute payload addresses relative to `NLA_HDRLEN` and read values directly without byte-order conversion. `nlattr_add()` checks that the aligned request length plus aligned new attribute fits in `sizeof(struct libbpf_nla_req)`, rejects mismatched data/length pairs, writes type and length, copies payload if present, and advances `nlmsg_len`. `nlattr_begin_nested()` records the current tail and adds a zero-length nested attribute with `NLA_F_NESTED`; `nlattr_end_nested()` fills its final length from the current request tail. No persistent state is maintained beyond the caller-owned request object.

## Dependencies and Integration
The header depends on standard integer/string/errno headers and Linux netlink, rtnetlink, and generic-netlink UAPI headers. It is included by `nlattr.c` and `netlink.c` to construct and parse netlink requests for XDP and TC operations.

## Risks and Test Signals
Risks include the small fixed request buffer limiting future attributes, direct unaligned typed reads on architectures sensitive to alignment, no endian conversion for netlink payload values, caller responsibility for valid nested begin/end pairing, and the deliberate `__LINUX_NETLINK_H` define potentially interacting with kernel header feature guards. Test signals should include buffer-boundary request-building tests, invalid data/length combinations, nested attribute length checks, typed getter alignment fixtures, and compile checks across kernel header versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/nlattr.h -->
