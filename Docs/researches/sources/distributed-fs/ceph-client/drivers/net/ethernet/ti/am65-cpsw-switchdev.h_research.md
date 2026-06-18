# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-switchdev.h

## Purpose
Provides the optional switchdev interface for the AM65 CPSW NUSS driver. It lets the main driver set skb offload-forward marks and register/unregister switchdev notifiers while compiling cleanly when switchdev support is disabled.

## Important APIs, Types, and Functions
When `CONFIG_TI_K3_AM65_CPSW_SWITCHDEV` is enabled, it declares `am65_cpsw_switchdev_register_notifiers`, `am65_cpsw_switchdev_unregister_notifiers`, and defines `am65_cpsw_nuss_set_offload_fwd_mark` to set `skb->offload_fwd_mark`. When disabled, notifier registration returns `-EOPNOTSUPP`, unregister is a no-op, and the skb mark helper is a no-op.

## Control Flow
The only runtime logic is compile-time selected inline behavior. The enabled mark helper is called from the RX path before GRO so packets forwarded by hardware can be marked for bridge/switchdev semantics. The notifier functions are called by the main driver's registration and remove paths.

## State and Persistence
No state is stored in the header. The enabled skb helper mutates transient packet metadata. Switchdev persistent state is created in `am65-cpsw-switchdev.c` through ALE programming.

## Dependencies and Integration Points
Includes `linux/skbuff.h` and relies on `struct am65_cpsw_common` from includers. It is included by `am65-cpsw-nuss.c` and implemented by `am65-cpsw-switchdev.c`.

## Risks and Test Signals
Risks are configuration mismatches: the main driver should not fail single-port or non-switchdev systems because registration is unavailable, and skb marking must only be meaningful in switch mode. Test signals are switchdev-enabled and disabled builds, RX bridge forwarding tests that inspect `offload_fwd_mark`, and probe/remove on configurations where switchdev is not reachable.
