# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/reconfig.c

Purpose: Provides the legacy `/proc/powerpc/ofdt` write interface for dynamic Open Firmware device-tree node and property reconfiguration.

Important APIs/types/functions: Implements node add/remove helpers, property list parsing/allocation/freeing, command handlers for `add_node`, `remove_node`, `add_property`, `remove_property`, `update_property`, `ofdt_write()`, and proc registration.

Control flow: A privileged write is blocked under device-tree lockdown, copied from userspace as a nul-terminated command buffer, split into command and payload, parsed into paths/phandles/properties, and applied using OF attach/detach/add/remove/update APIs. Updating `slb-size` or `ibm,slb-size` also calls `slb_set_size()`.

State and persistence: Mutates the live dynamic OF tree. Allocated `struct property` objects are attached to nodes on success or freed on failure. No separate persistent state exists.

Dependencies and integration points: Depends on OF dynamic APIs, security lockdown, procfs, usercopy, `pseries_of_derive_parent()`, and MMU SLB sizing.

Risks: The binary/text hybrid property parser is fragile and legacy. Some handlers leak node references on early returns. Property removal passes `of_find_property()` results directly and must handle absent properties through OF core behavior. Lockdown is essential because this mutates hardware description.

Test signals: Proc command tests for add/remove/update paths, malformed property buffers, lockdown enforcement, child-node busy removal, SLB-size update, reference leak detection, and OF reconfig notifier effects.

Source read size: 414 lines, 10664 bytes.
