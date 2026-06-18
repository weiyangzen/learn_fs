# sources/distributed-fs/ceph-client/net/iucv/iucv.c

## Purpose
Provides the low-level S390 z/VM IUCV infrastructure. It wraps CP B2F0 IUCV commands, manages per-CPU interrupt buffers and command parameter blocks, exposes an IUCV bus and exported interface, registers handlers, manages path tables, dispatches external interrupts to registered users, and exports message/path operations used by AF_IUCV and other IUCV clients.

## Important APIs, types, and functions
Exports `iucv_bus`, `iucv_alloc_device`, `iucv_register`, `iucv_unregister`, `iucv_path_accept`, `iucv_path_connect`, `iucv_path_quiesce`, `iucv_path_resume`, `iucv_path_sever`, `iucv_message_purge`, `__iucv_message_receive`, `iucv_message_receive`, `iucv_message_reject`, `iucv_message_reply`, `__iucv_message_send`, `iucv_message_send`, `iucv_message_send2way`, and `iucv_if`. Internal command layouts are `union iucv_param` and packed CP parameter structs. Interrupt data is represented by `struct iucv_irq_data` and per-event decoded structs.

## Control flow
Initialization requires `machine_is_vm`, enables the IUCV control bit, queries max path IDs, registers external IRQ handling, creates a root device, installs CPU hotplug states for per-CPU DMA-capable buffers, registers a reboot notifier, converts fixed error strings to EBCDIC, registers the IUCV bus, and marks the exported interface available. Handler registration enables IUCV on first user by allocating the path table, declaring buffers on online CPUs, and enabling interrupt masks; non-SMP handlers force interrupts to a single CPU.

CP commands are issued through inline assembly `__iucv_call_b2f0` and typed wrappers. Path connect/accept/quiesce/resume/sever fill command blocks, call CP, update path fields and handler lists, and manage `iucv_path_table`. Message send/receive/reply/reject/purge handle inline IPRM data, buffer-list flags, DMA32 addresses, message IDs, tags, classes, and residual/audit results.

External interrupts copy the per-CPU interrupt buffer into allocated queue entries. Path-pending work goes to a workqueue because it may call functions unsuitable for tasklet context; other events go to a tasklet. Dispatch decodes connection complete/sever/quiesce/resume and message pending/complete events, finds the path by ID, and invokes registered handler callbacks.

## State and persistence behavior
Runtime state includes `iucv_available`, root device/bus state, max pathid, path table, handler list, per-CPU IRQ data and command blocks, CPU masks for declared buffers and enabled IRQs, task/work queues, active CPU marker, non-SMP handler count, and reboot notifier. No durable persistence exists. Reboot blocks interrupts and severs active paths; exit frees queued work, unregisters hotplug states, root device, bus, and external IRQ.

## Dependencies and integration points
Depends on S390/z/VM machine support, CP B2F0 instruction, external IRQ `EXT_IRQ_IUCV`, CPU hotplug, DMA-addressable memory below 2G, EBCDIC helpers, device/bus core, reboot notifier, tasklets/workqueues, and exported `net/iucv/iucv.h` contracts. AF_IUCV consumes `iucv_if`.

## Risks and test signals
Risks include path-ID reuse races, stale queued interrupts after sever, CPU hotplug leaving no enabled IUCV CPU, non-SMP handler ordering constraints, DMA32 address misuse, CP return-code mapping, and tasklet/work locking deadlocks around `iucv_table_lock`. Test VM-only init failure on non-z/VM, CPU online/offline while paths exist, handler register/unregister transitions, path pending/accept/connect/sever, message send/receive/reply/purge with IPRM and buffer lists, reboot notifier path severing, and concurrent path teardown with queued interrupts.
