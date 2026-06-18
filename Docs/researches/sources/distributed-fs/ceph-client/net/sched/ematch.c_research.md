
# sources/distributed-fs/ceph-client/net/sched/ematch.c

## Purpose

`ematch.c` is the core extended-match framework for traffic-control classifiers. It registers ematch kinds, validates netlink ematch trees, owns module references and per-match private data, dumps trees, destroys trees, and evaluates boolean ematch expressions with AND/OR/END/inversion/container semantics.

## Important APIs, Types, and Functions

Global state is `ematch_ops`, protected by `ematch_mod_lock`. Public exports are `tcf_em_register()`, `tcf_em_unregister()`, `tcf_em_tree_validate()`, `tcf_em_tree_destroy()`, `tcf_em_tree_dump()`, and `__tcf_em_tree_match()`. `tcf_em_validate()` validates one match attribute, loads modules when needed, handles container references, invokes kind-specific `change()`, or copies simple/raw data. `tcf_em_match()` applies inversion around a kind-specific match result.

## Control Flow

Registration inserts a unique kind with a required `match()` callback. Validation parses tree header/list attributes, allocates an array sized by `nmatches`, requires match attributes to be numbered sequentially, validates each match, and verifies the actual count equals the header. Container matches store a forward-only reference to another sequence; backward/self references are rejected to avoid loops. Unknown kinds may trigger module autoload by temporarily dropping RTNL and then returning `-EAGAIN` so the request can be replayed.

Destroy walks each match, calls kind-specific destroy or default `kfree()` for non-simple copied data, releases the module reference, and frees the match array. Dump emits the tree header and each match as a nested, sequential netlink attribute, delegating kind-specific payloads when available. Matching interprets the flat match array as a stack-based expression: containers push the current index and jump to a referenced sequence, markers/operators decide early end, and stack pop restores the caller sequence. Stack overflow fails closed with a ratelimited warning.

## State and Persistence Behavior

The registry persists for loaded ematch modules. Each validated tree owns a match array, module references for concrete kinds, copied or kind-managed data, and its header. Trees are immutable while in use; callers are expected to validate into a temporary tree and then publish safely in their classifier private state.

## Dependencies and Integration Points

It depends on RTNL, module loading, netlink attribute parsing/dumping, `tcf_ematch_ops` supplied by individual ematch modules, `struct tcf_proto` for net namespace access, and `CONFIG_NET_EMATCH_STACK` for expression evaluation depth. Classifiers such as basic/cgroup users can attach ematch trees through `tcf_em_tree_validate()` and evaluate them through the wrapper around `__tcf_em_tree_match()`.

## Risks and Edge Cases

Module reference ownership is delicate: after `tcf_em_lookup()` succeeds, validation must not drop the reference except through destroy. Container references must remain forward-only or expressions can loop. Attribute numbering and `nmatches` mismatch are rejected because evaluation trusts array indexes. Stack depth is bounded by `CONFIG_NET_EMATCH_STACK`; too much nesting returns `-1`. This local source contains an apparent duplicated `if (data_len < sizeof(u32))` line in simple-data validation, which is a compile/review risk.

## Test Signals

Test registration duplicate rejection, unknown-kind autoload/retry, malformed tree headers/lists, sequential attribute numbering, forward and invalid container references, simple and non-simple data ownership, dump round trips, inversion, AND/OR/END expression behavior, and stack-overflow handling.
