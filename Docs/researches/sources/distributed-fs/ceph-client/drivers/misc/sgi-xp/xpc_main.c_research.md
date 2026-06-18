# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_main.c

Purpose: implements the XPC module core: heartbeat thread, discovery thread, partition activation manager, channel-manager/kthread lifecycle, sysctl tunables, reboot/die notifiers, module init, and orderly exit.

Important APIs/functions: exports devices `xpc_part` and `xpc_chan`, global `xpc_arch_ops`, wake/IRQ state, and helpers such as `xpc_kzalloc_cacheline_aligned()`, `xpc_activate_partition()`, `xpc_activate_kthreads()`, `xpc_create_kthreads()`, and `xpc_disconnect_wait()`. Internal key functions include `xpc_hb_checker()`, `xpc_channel_mgr()`, `xpc_setup_ch_structures()`, `xpc_activating()`, `xpc_kthread_start()`, `xpc_setup_partitions()`, `xpc_do_exit()`, and notifier callbacks.

Control flow: init selects UV operations, allocates partition structures, registers sysctls, sets up the local reserved page, registers reboot/die notifiers, starts heartbeat and discovery kthreads, then installs XP-facing XPC entry points. The heartbeat checker increments local heartbeat, checks remote heartbeats, and processes activation IRQs. Partition activation spawns a per-partition kthread that sets up channels, makes first contact, marks active, and runs the channel manager until deactivation. Channel worker kthreads issue connected/disconnecting callouts and deliver payloads until the channel disconnects.

State and persistence: module-global volatile state includes tunables, timers, completions, IRQ counters, partition array, architecture ops, and `xpc_exiting`. Sysctl changes persist only while loaded. Reserved-page timestamp advertises local XPC readiness to peers.

Dependencies and integration: depends on XP base, `xpc_partition.c`, `xpc_channel.c`, UV-specific `xpc_uv.c`, Linux kthreads/timers/sysctl/reboot/die notifiers, and architecture callbacks.

Risks: shutdown must coordinate discovery, heartbeat, active partitions, engagement timeouts, callouts, and XP interface clearing. Die notifier paths use polling/udelay and intentionally bypass normal sleep-heavy teardown. Kthread creation failures can disconnect channels or abort init. CPU pinning to CPU 0 for heartbeat checking is topology-sensitive.

Test signals: module load/unload, sysctl bounds, heartbeat timeout behavior, discovery completion, partition activation/deactivation, kthread limit behavior, reboot/die notifier deactivation, and disengage timeout logging.
