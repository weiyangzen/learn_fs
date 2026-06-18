# sources/distributed-fs/ceph-client/include/linux/rcu_notifier.h

Purpose: declares optional RCU CPU stall notifier registration APIs without forcing inclusion of the full RCU update header.

Important APIs and types: action constants `RCU_STALL_NOTIFY_NORM` and `RCU_STALL_NOTIFY_EXP` distinguish normal and expedited stall notifications. When stall notifier support is enabled, `rcu_stall_chain_notifier_register()` and `rcu_stall_chain_notifier_unregister()` register a notifier block; otherwise inline fallbacks return `-EEXIST` and `-ENOENT`.

Control flow: diagnostics or platform code register a notifier to observe RCU stall warnings. RCU stall detection invokes the chain with the appropriate action when configured.

State and persistence: notifier-chain state is owned by RCU internals when enabled. This header has no persistence.

Dependencies and integration points: depends conditionally on notifier and type headers, and on `CONFIG_RCU_STALL_COMMON` plus `CONFIG_RCU_CPU_STALL_NOTIFIER`.

Risks and test signals: risks include code assuming registration succeeds in Tiny/disabled configs, notifier callback deadlocks during stall handling, and action-code drift. Test config-enabled/disabled builds, register/unregister error handling, induced RCU stalls, and notifier callback robustness under distressed systems.
