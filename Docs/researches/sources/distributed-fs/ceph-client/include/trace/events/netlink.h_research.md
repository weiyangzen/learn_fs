# sources/distributed-fs/ceph-client/include/trace/events/netlink.h

Purpose: Defines a compact tracepoint for netlink extended-ack messages. It records human-readable extack text emitted by netlink validation and policy code.

Important APIs/types/functions: `netlink_extack` takes a `const char *msg`, stores it with `__string`, and prints it as `msg=%s`.

Control flow: Netlink code calls the tracepoint when an extack diagnostic is set. The trace event copies the message into the tracing buffer so later output does not depend on the original string lifetime.

State and persistence: No persistent state. It observes transient extack text associated with one netlink request.

Dependencies and integration points: Depends on tracepoints and integrates with generic netlink/rtnetlink diagnostics, policy validation, and userspace-visible error reporting.

Risks and test signals: Risks include tracing sensitive messages, missing NULL handling at call sites, and high event volume from malformed request storms. Test invalid rtnetlink/generic-netlink operations, policy failures, namespace-specific extacks, and tracing while fuzzing netlink parsers.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/netlink.h` completely for this pass (29 lines, 485 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/netlink.h_research.md`.
