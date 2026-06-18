# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/dlpar.c

Purpose: Provides common Dynamic Logical Partitioning support for pseries CPU, memory, persistent memory, and device-tree hotplug. It parses RTAS configure-connector output, applies dynamic OF changesets, acquires/releases DRCs, dispatches hotplug error logs, and exposes a sysfs control entry.

Important APIs/types/functions: Defines `struct pseries_hp_work`, `struct cc_workarea`, property/node parsing helpers, `dlpar_configure_connector()`, `dlpar_attach_node()`, `dlpar_detach_node()`, `dlpar_acquire_drc()`, `dlpar_release_drc()`, `dlpar_unisolate_drc()`, DRC lookup helpers, `handle_dlpar_errorlog()`, `queue_hotplug_event()`, command parsers, `dlpar_workqueue_init()`, and the `/sys/kernel/dlpar` attribute.

Control flow: `dlpar_configure_connector()` repeatedly calls RTAS `ibm,configure-connector`, interpreting return codes as node, sibling, child, property, parent, complete, or error operations. DRC acquire/release validates entity state and sets allocation/isolation indicators. Hotplug error logs dispatch to memory, CPU, PMEM, or device-tree handlers. Sysfs commands parse `<resource> <action> <id_type> <id>` into the same error-log shape. Queued firmware events run through an ordered workqueue.

State and persistence: Persistent state is the ordered workqueue and sysfs attribute. Dynamic OF nodes/properties allocated from configure-connector are either attached to the live tree or freed. DRC allocation/isolation state persists in firmware.

Dependencies and integration points: Depends on RTAS tokens, RTAS work areas, dynamic Open Firmware changesets, pseries hotplug resource handlers, kernel hotplug locking, and kernel object sysfs.

Risks: Configure-connector parsing is stateful and can leak or corrupt a node tree if sibling/parent sequencing is unexpected. Rollback must free unattached dynamic nodes but not live tree nodes. Sysfs parser rejects PMEM even though dispatcher handles it. DRC state changes require correct rollback on subsequent attach/online failure.

Test signals: Manual `/sys/kernel/dlpar` add/remove for memory, CPU, and device-tree resources, firmware hotplug event queueing, configure-connector failure injection, OF changeset validation, DRC acquire/release traces, and hotplug rollback tests are useful.

Source read size: 827 lines, 16792 bytes.
