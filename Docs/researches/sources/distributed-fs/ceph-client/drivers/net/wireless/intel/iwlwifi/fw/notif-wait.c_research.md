<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/notif-wait.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/notif-wait.c

Purpose: one-shot wait framework for firmware notifications.

Important APIs/functions: exported functions are `iwl_notification_wait_init()`, `iwl_notification_wait()`, `iwl_abort_notification_waits()`, `iwl_init_notification_wait()`, `iwl_remove_notification()`, and `iwl_wait_notification()`.

Control flow: callers initialize a stack `iwl_notification_wait`, register command ids and an optional predicate, trigger the firmware action, and then call `iwl_wait_notification()`. RX notification handling calls `iwl_notification_wait()`, which matches wide or legacy command ids under a spinlock, runs the predicate if present, marks entries triggered, and returns whether waiters should be woken. Waiting removes the entry and maps abort to `-EIO`, timeout to `-ETIMEDOUT`.

State and persistence: `struct iwl_notif_wait_data` owns a spinlocked list and waitqueue. Each wait entry stores command ids, predicate data, and triggered/aborted flags. Entries are intended to be stack allocated and one-shot.

Dependencies/integration: used by PNVM loading and other firmware command flows that need a completion notification. Depends on RX packet headers and command id macros.

Risks/test signals: races around abort, repeated notification callbacks, and stack lifetime are the main risks. Test notification-before-timeout, predicate false then true, abort wakeup, legacy command id matching, max command truncation warning, and removal under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/notif-wait.c -->
