# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat_inject.c

Purpose: implements heartbeat failure injection for debug/test builds. It deliberately makes a selected AE/thread look stalled to exercise heartbeat error detection and reset paths.

Important APIs: `adf_heartbeat_inject_error(struct adf_accel_dev *accel_dev)` is called from debugfs. Helpers set the firmware heartbeat timer to maximum, optionally stop the platform timer, disable arbitration for one AE/thread via `adf_disable_arb_thd`, and mutate heartbeat DMA counters to satisfy the failure predicate.

Control flow and state: chooses a random active AE and random heartbeat thread, prevents firmware from updating counters, disables scheduling for the chosen thread, then changes live and last counter values so future status checks see `req != resp` and unchanged response. It writes directly into heartbeat DMA memory and changes `heartbeat->hb_timer`.

Dependencies and integration: depends on admin heartbeat timer command, hardware arbitration control, random bytes, and heartbeat counter layout.

Risks and test signals: intended destructive behavior can make a device require reset; should only be reachable under error-injection config. Test debugfs injection returns errors on unsupported admin/arbiter paths and triggers heartbeat failure on the next valid poll.
