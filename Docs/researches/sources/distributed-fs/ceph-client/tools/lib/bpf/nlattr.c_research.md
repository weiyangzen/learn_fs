<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/nlattr.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/nlattr.c

## Purpose
This file implements netlink attribute parsing, validation, nested parsing, and extended-ack error message extraction for libbpf's netlink code.

## APIs, Types, and Functions
Static helpers include `nla_attr_minlen[]`, `nla_next()`, `nla_ok()`, `nla_type()`, `validate_nla()`, and `nlmsg_len()`. Public internal functions are `libbpf_nla_parse()`, `libbpf_nla_parse_nested()`, and `libbpf_nla_dump_errormsg()`.

## Control Flow, State, and Persistence
`libbpf_nla_parse()` clears the caller-provided table, iterates attributes with `libbpf_nla_for_each_attr()`, ignores types above `maxtype`, validates each attribute against an optional policy, warns on duplicates while replacing the table entry with the later attribute, and returns the first validation error. `validate_nla()` derives minimum length from explicit policy or type defaults, enforces max length, and ensures string attributes end in NUL. `libbpf_nla_parse_nested()` parses the payload of a nested attribute as a new attribute stream. `libbpf_nla_dump_errormsg()` checks `NLM_F_ACK_TLVS`, accounts for capped versus uncapped embedded request length, parses `NLMSGERR_ATTR_MSG` and `NLMSGERR_ATTR_OFFS`, and logs the kernel error string when present.

The file has no persistent state except immutable minimum-length table data. All parse output is written into caller-owned arrays.

## Dependencies and Integration
It depends on Linux rtnetlink/netlink structures, local `nlattr.h` declarations, and `libbpf_internal.h` logging. `netlink.c` uses it to parse route and generic-netlink responses and extack errors.

## Risks and Test Signals
Risks include duplicate attribute replacement semantics, missing warning context, out-of-bounds calculations for malformed extended-ack messages, string policy behavior on zero-length payloads, ignoring leftover trailing bytes after the attribute loop, and accepting unknown high attributes for compatibility. Test signals should include valid and malformed attribute streams, min/max length policies, non-NUL strings, duplicates, nested parse fixtures, extack messages with and without `NLM_F_CAPPED`, and fuzzing truncated netlink payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/nlattr.c -->
