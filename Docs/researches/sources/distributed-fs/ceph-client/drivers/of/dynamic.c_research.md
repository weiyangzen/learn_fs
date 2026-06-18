# sources/distributed-fs/ceph-client/drivers/of/dynamic.c

## Purpose
`dynamic.c` implements runtime devicetree mutation. It owns node reference APIs, OF reconfiguration notifier registration, attach/detach operations, dynamic node/property allocation and free paths, and transactional changeset apply/revert helpers used by overlays and other dynamic DT clients.

## Important APIs, types, and functions
Exports include `of_node_get()`, `of_node_put()`, `of_reconfig_notifier_register()`, `of_reconfig_notifier_unregister()`, `of_reconfig_get_state_change()`, `of_detach_node()`, `of_changeset_create_node()`, `of_changeset_init()`, `of_changeset_destroy()`, `of_changeset_apply()`, `of_changeset_revert()`, `of_changeset_action()`, and property-construction helpers for string, string-array, u32-array, bool, and string update actions. Core internal helpers include `__of_attach_node()`, `__of_detach_node()`, `__of_prop_dup()`, `__of_node_dup()`, and changeset entry apply/revert/notify functions.

## Control flow and state
Node references are backed by embedded kobjects. Reconfiguration events flow through a blocking notifier chain and use `struct of_reconfig_data`. Attach parses `name` and phandle properties, links the node into its parent's child list, clears `OF_DETACHED`, marks the fwnode as not a device, and attaches sysfs. Detach unlinks from siblings, marks `OF_DETACHED`, invalidates the phandle cache, and detaches sysfs.

Changesets collect ordered `struct of_changeset_entry` items. Apply runs entries forward under `of_mutex`, reverts already-applied entries if an apply step fails, then emits notifiers with the mutex dropped. Revert runs entries in reverse and reapplies on revert failure. Destroy waits for pending device-link removals before releasing entries to avoid freeing nodes still referenced by devices.

## Dependencies and integration
This file relies on property mutation helpers in `base.c`, sysfs hooks in `kobj.c`, fwnode link cleanup, device-link removal, OF overlay flags, and notifier consumers such as OF platform population.

## Risks and test signals
Risk is high around reference balance, overlay lifetime flags, mutation while readers traverse under `devtree_lock`, notifier failures after structural changes, and changeset rollback leaving unknown state when both apply and revert fail. Test signals include overlay KUnit tests, dynamic reconfiguration device add/remove behavior, kobject underflow warnings, and memory leak diagnostics in `of_node_release()`.
