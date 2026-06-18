# sources/distributed-fs/ceph-client/block/blk-wbt.h

Purpose: exposes the small writeback-throttling control surface to the rest of the block layer and provides no-op stubs when `CONFIG_BLK_WBT` is disabled.

Important APIs: `wbt_init_enable_default()` creates and enables the default WBT policy when queue attributes allow it. `wbt_disable_default()` disables a default-enabled policy without removing it. `wbt_enable_default()` checks or flips default enablement. `wbt_get_min_lat()`, `wbt_disabled()`, and `wbt_set_lat()` query and set the latency target.

Control flow and integration: disk setup and sysfs latency handlers call these functions to install or adjust `RQ_QOS_WBT`. Elevator switching and queue setup can disable or avoid default WBT. With the config disabled, only the default enable/disable functions are present as empty stubs, so callers must not rely on query functions unless `CONFIG_BLK_WBT` is enabled.

State and persistence: the header owns no storage. All state lives in `struct rq_wb` inside `blk-wbt.c` and the queue rq-qos chain.

Risks and test signals: prototypes must match callers and the disabled-config surface must compile across queue setup paths. Test build matrices with `CONFIG_BLK_WBT=y/n`, sysfs latency operations, default policy activation, and scheduler interactions that call enable/disable hooks.
