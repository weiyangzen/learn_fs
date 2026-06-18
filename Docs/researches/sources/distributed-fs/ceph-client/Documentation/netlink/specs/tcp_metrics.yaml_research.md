# sources/distributed-fs/ceph-client/Documentation/netlink/specs/tcp_metrics.yaml

Purpose: this generic-netlink legacy schema documents the TCP metrics management interface: retrieving cached destination metrics and deleting them.

Important APIs, types, and functions: family metadata uses `tcp-metrics-genl-name`, `tcp-metrics-genl-version`, `max-by-define`, and a global kernel policy. The constant `tcp-fastopen-cookie-max` is 16. Attribute set `tcp-metrics` includes destination and source IPv4/IPv6 addresses, age, nested metric values, Fast Open MSS, SYN drop counters/timestamp, Fast Open cookie, and padding. Nested `metrics` contains RTT, RTT variance, ssthresh, cwnd, reordering, RTT in microseconds, and RTT variance in microseconds; the file notes metric attribute numbers are offset from kernel `TCP_METRIC_*` enum names.

Control flow: `get` accepts destination/source address selectors and returns address identity, age, metric values, and Fast Open state; it supports dumps. `del` is admin-only and deletes matching metrics using the same selectors. Both disable strict/dump validation for compatibility with legacy behavior.

State and persistence: TCP metrics live in the kernel TCP metrics cache and change as connections update route/destination performance data. Entries age out or are deleted by the admin operation.

Dependencies and integration: depends on the generic netlink legacy family, TCP metrics cache internals, and Fast Open state. Userspace diagnostics and cleanup tools consume this ABI.

Risks: the intentionally offset metric numbering is easy to mis-generate. The attribute `reodering` appears misspelled in the schema and likely mirrors ABI naming or an existing typo. Fast Open cookie length uses `min-len` rather than exact length. Test signals include get/dump decoding, delete permission checks, IPv4/IPv6 selector coverage, metric numbering parity tests, and compatibility checks for non-strict validation.
