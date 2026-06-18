<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/notif-wait.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/notif-wait.h

Purpose: declares the notification wait data structures and caller-facing helpers.

Important APIs/types: `struct iwl_notif_wait_data` contains the wait list, spinlock, and waitqueue. `struct iwl_notification_wait` contains the list node, predicate, predicate data, up to `MAX_NOTIF_CMDS` command ids, and triggered/aborted flags. Inline `iwl_notification_notify()` and `iwl_notification_wait_notify()` combine match evaluation with waitqueue wakeup.

Control flow: the header documents the intended sequence: allocate a wait entry on the stack, initialize/register it, cause firmware to notify, then wait or explicitly remove it. Sparse annotations model acquire/release ownership of the wait entry.

State and persistence: only in-memory synchronization state; no durable persistence.

Dependencies/integration: includes waitqueue support and `iwl-trans.h` for RX packet and command definitions. Used by PNVM and other firmware flows.

Risks/test signals: since waits are stack based, callers must not return before removal. Test compile annotations, max command count behavior, inline notify path, and all users for balanced init/wait/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/notif-wait.h -->
