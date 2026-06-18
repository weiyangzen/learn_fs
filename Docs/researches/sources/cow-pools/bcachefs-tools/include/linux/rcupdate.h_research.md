# File Research: sources/cow-pools/bcachefs-tools/include/linux/rcupdate.h

This header adapts kernel RCU APIs to Userspace RCU. It includes `<urcu.h>`, maps RCU dereference/access/update pointer helpers to URCU or `READ_ONCE`/`WRITE_ONCE`, and maps `kfree_rcu`/`kvfree_rcu` variants directly to `kfree()` with comments noting the simplification.

It defines `rcu_head_init()` and `rcu_head_after_call_rcu()` for checking whether a callback has been queued. It also defines an `rcu` cleanup guard around `rcu_read_lock()`/`rcu_read_unlock()`.
