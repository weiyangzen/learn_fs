<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bridge_loop_avoidance.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/bridge_loop_avoidance.h research

Purpose: declares the BLA public interface and provides no-op stubs when `CONFIG_BATMAN_ADV_BLA` is disabled. It is the integration contract between BLA and routing, DAT, bridge ingress/egress, netlink, and hard-interface lifecycle code.

Important APIs and types: `batadv_bla_is_loopdetect_mac()` recognizes locally administered loopdetect source MACs beginning with `ba:be`. Enabled builds export RX/TX filters, backbone checks, duplicate-list checks, primary address updates, status updates, init/free, netlink dump functions, and DAT-only claim checks. `BATADV_BLA_CRC_INIT` defines the initial CRC value for claim table synchronization. Disabled builds inline safe defaults: filtering functions return false, dump functions return `-EOPNOTSUPP`, init returns success, and `batadv_bla_check_claim()` returns true.

Control flow and state behavior: the header has no storage, but its stubs define global feature behavior. With BLA off at compile time, callers can still invoke the same functions and will generally continue forwarding traffic without BLA filtering or diagnostics. With BLA on, callers must honor boolean return values: RX/TX paths treat true as consumed or handled.

Dependencies and integration: includes `main.h` and kernel network/skbuff/netlink types. DAT is conditionally coupled through `batadv_bla_check_claim()`, letting DAT avoid answering for clients claimed by another backbone gateway. Netlink command handlers depend on the dump prototypes.

Risks: the disabled stub for `batadv_bla_init()` returns `1`, which is non-negative and therefore treated as success by callers checking `< 0`; code that assumes exact zero would be wrong. The boolean contract differs by caller context, so documentation and tests need to verify whether true means "skb consumed" or simply "do not process further".

Test signals: build both with and without `CONFIG_BATMAN_ADV_BLA`; compile DAT combinations; verify non-BLA builds still link all callers; verify bridge traffic is not filtered by BLA stubs; verify netlink dump commands return unsupported when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bridge_loop_avoidance.h -->
