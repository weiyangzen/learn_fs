# sources/distributed-fs/ceph-client/drivers/net/can/slcan/slcan.h

Purpose: small internal header joining SLCAN core and ethtool implementation.

Important APIs/types/functions: declares `slcan_err_rst_on_open()`, `slcan_enable_err_rst_on_open()`, and `extern const struct ethtool_ops slcan_ethtool_ops`.

Control flow: no executable flow. The declarations let `slcan-ethtool.c` call core helpers and let core attach ethtool ops during ldisc open.

State and persistence: no state in this header.

Dependencies/integration: requires callers to include netdevice-compatible type declarations before use; both SLCAN objects include it.

Risks: changing prototypes requires synchronized updates to both compilation units. The flag semantics are not visible here beyond helper names.

Test signals: compile/link test of `CONFIG_CAN_SLCAN`; unresolved symbols indicate header/object mismatch.
