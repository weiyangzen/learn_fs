# sources/distributed-fs/ceph-client/drivers/virtio/virtio_mem.c

## Purpose
`virtio_mem.c` is the Linux virtio-mem driver. It exposes hypervisor-controlled memory as Linux hotplug memory, reconciles the device `requested_size` with the guest's `plugged_size`, and makes unplugged ranges inaccessible or fake-offline so the kernel never allocates memory that the device has not actually plugged. It supports two operating models: sub-block mode (SBM), where a Linux memory block is tracked as multiple virtio-mem subblocks, and big-block mode (BBM), where each tracked unit spans one or more Linux memory blocks.

## Important APIs, types, and functions
- Module parameters `unplug_online`, `force_bbm`, and `bbm_block_size` influence unplug policy and block-mode selection.
- `struct virtio_mem` owns the virtio device, virtqueue, config cache, memory-hotplug state, retry timer, notifier blocks, parent resource, memory group id, kdump vmcore callback state, and either `sbm` or `bbm` tracking arrays.
- `enum virtio_mem_sbm_mb_state` and `enum virtio_mem_bbm_bb_state` model Linux memory-block and big-block lifecycle states.
- `virtio_mem_probe()`, `virtio_mem_init()`, `virtio_mem_init_hotplug()`, `virtio_mem_remove()`, and the `virtio_driver` table implement the virtio lifecycle.
- `virtio_mem_run_wq()` is the central reconciliation loop for config changes, cleanup, plug requests, unplug requests, retry backoff, and fatal error handling.
- `virtio_mem_send_request()`, `virtio_mem_send_plug_request()`, `virtio_mem_send_unplug_request()`, `virtio_mem_send_unplug_all_request()`, and kdump-only `virtio_mem_send_state_request()` are the guest-to-host request path over the single virtqueue.
- SBM helpers maintain `mb_states` and `sb_states`, prepare tracking arrays, plug/unplug subblocks, add/remove memory blocks, and react to online/offline notifications.
- BBM helpers maintain `bb_states`, plug/add big blocks, fake-offline online pages, remove Linux memory, and unplug whole big blocks.
- `virtio_mem_memory_notifier_cb()` and `virtio_mem_online_page_cb()` integrate with Linux memory hotplug and online-page handling.
- `virtio_mem_fake_offline()`, `virtio_mem_fake_online()`, `virtio_mem_set_fake_offline()`, and notifier helpers implement the PG_offline/page-ref choreography for unplugging online memory safely.

## Control flow
Probe allocates `struct virtio_mem`, initializes the virtqueue and synchronization objects, reads immutable config fields (`plugged_size`, `block_size`, NUMA node, address range), and either enters kdump mode or normal hotplug mode. Hotplug initialization chooses SBM when the virtio device block size and pageblock granularity allow subblocks inside a Linux memory block; otherwise it uses BBM with a power-of-two big block size. It reserves the device address range as a parent `System RAM` resource, registers a dynamic memory group, registers memory and PM notifiers, installs the shared online-page callback, marks the device ready, and queues initial work.

The workqueue cancels pending retry timers, refreshes device config when `config_changed` is set, cleans up previously half-failed plug/unplug state, then compares `requested_size` and `plugged_size`. If the host requests more memory, SBM first fills partially plugged online/offline memory blocks, then reuses unused blocks, then prepares new blocks; BBM reuses or prepares whole big blocks. If the host requests less memory, SBM prioritizes offline and partially plugged memory, then movable online memory, then kernel memory if `unplug_online` permits; BBM first removes offline blocks, then movable blocks, then any online block if allowed. Busy host/device states, busy guest pages, and allocation pressure map to retry behavior through an hrtimer with exponential backoff.

Memory online/offline callbacks serialize state changes with `hotplug_mutex`. Going online is rejected for unexpected SBM states. Onlining converts offline states to kernel or movable states based on the target zone, and the online-page callback only releases actually plugged subblocks while keeping unplugged ranges fake-offline. Offlining transitions online states back to offline and may schedule immediate work if unplugging offline-only memory. Device config changes only set an atomic flag and queue the workqueue; the main loop then rereads size and usable-range fields.

Kdump mode is special: hotplug is disabled, the device is marked ready, and `/proc/vmcore` callbacks query per-device-block state from the host so crash dump code can identify RAM without plugging or unplugging anything.

## State and persistence behavior
All persistent state is in memory and device config, not on disk. `plugged_size` is the driver's reflection of successful host plug/unplug requests, while `requested_size` and `usable_region_size` are refreshed from device config. SBM persists one byte per tracked Linux memory block plus a bitmap of plugged subblocks; counters summarize states and `have_unplugged_mb` records cleanup debt. BBM persists one byte per big block plus counters. `offline_size` throttles how much newly added but not-yet-onlined memory can accumulate. `parent_resource`, `resource_name`, and `mgid` tie device memory into the Linux resource and memory-group model.

Removal prevents new work, cancels work/timers, removes partially plugged offline SBM blocks, unregisters callbacks, and only releases the parent resource and memory group if no system RAM from the device remains. If memory is still added, the driver warns because Linux has no reliable way to remove all added memory during device removal. Suspend resets queues unless persistent suspend is supported and blocks unsafe suspend/hibernation with plugged memory.

## Dependencies and integration points
The file integrates the virtio core, virtqueue API, Linux memory hotplug, memory groups, resource management, NUMA/ACPI PXM translation, page allocator `alloc_contig_range()`, `generic_online_page()`, PM notifiers, kdump vmcore callbacks, RCU for the global device list, and the virtio-mem UAPI config/request structures. It relies on `VIRTIO_MEM_F_UNPLUGGED_INACCESSIBLE`, optional `VIRTIO_MEM_F_ACPI_PXM`, and optional `VIRTIO_MEM_F_PERSISTENT_SUSPEND`.

## Risks and test signals
Main risks are races with memory onlining/offlining, partially successful host plug/unplug requests, MM cleanup gaps after `add_memory_driver_managed()` failures, retry loops under host busy or guest memory pressure, unsafe forced module removal with memory still added, and PG_offline/page reference accounting mistakes. BBM also relies on section-sized fake-offline chunks and can be coarse. Test signals include probe on aligned and misaligned regions, SBM and BBM selection, requested-size grow/shrink, offline threshold behavior, online-page treatment of unplugged ranges, `unplug_online=0`, ZONE_MOVABLE unplug success, busy page retry, config-change during unplug, kdump `/proc/vmcore` RAM filtering, suspend/restore behavior, and clean remove after all memory is unplugged.
