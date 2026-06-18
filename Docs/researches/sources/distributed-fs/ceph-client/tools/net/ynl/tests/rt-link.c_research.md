# sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-link.c

Purpose: rtnetlink link selftest for generated `rt-link` bindings, including dump parsing, netkit link creation, nested type-value data, and extack path rendering.

Important APIs/functions: `rt_link_print()` formats link attributes, alternate names, link kind, and nested netkit data/policy. `netkit_create()` builds a `newlink` request with `NLM_F_CREATE | NLM_F_ECHO`, kind `netkit`, and generated netkit policy setter; it consumes `RTM_NEWLINK` notification to return ifindex. `netkit_delete()` deletes by ifindex.

Control flow: `dump` allocates and performs `getlink` dump. `netkit` creates a netkit link, dumps links, finds the returned ifindex, prints it, then deletes it. `netkit_err_msg` intentionally sends invalid policy `10` and asserts the YNL error message contains the nested bad-attribute path.

State/dependencies: mutates kernel link state and uses generated request/free helpers. Requires netkit support and permissions. The error-message test depends on kernel extack wording/path stability.

Risks/test signals: strong coverage for sub-message/nested selector generation, notification wrappers, nlmsg flags setters, and bad attribute path construction. Cleanup risk exists if deletion is skipped after intermediate assertions.
