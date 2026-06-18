# sources/distributed-fs/ceph-client/drivers/most/core.c

## Purpose
This file implements the MOST core bus, interface/channel registration, component linking, channel configuration, buffer-object allocation, enqueueing, completion routing, and exported APIs consumed by MOST components and hardware-dependent modules.

## Important APIs, types, and functions
- `struct most_channel` wraps a Linux `struct device` plus per-channel config, linked components (`pipe0`/`pipe1`), buffer FIFOs, trash/halt queues, starvation state, enqueue thread, locks, completion, and counters.
- `struct interface_private` stores the generated device id, name, channel array, and channel list for each `struct most_interface`.
- Exported configuration/link APIs include `most_set_cfg_*()`, `most_add_link()`, `most_remove_link()`, and `most_cfg_complete()`.
- Exported buffer/channel APIs include `most_start_channel()`, `most_stop_channel()`, `channel_has_mbo()`, `most_get_mbo()`, `most_put_mbo()`, `most_submit_mbo()`, `most_register_component()`, `most_deregister_component()`, `most_register_interface()`, `most_deregister_interface()`, `most_stop_enqueue()`, and `most_resume_enqueue()`.
- `mostbus` is a custom bus with interface and channel devices plus sysfs/driver attributes for links, components, channel capabilities, and selected settings.

## Control flow
`most_init()` initializes the component list and ID allocator, registers the `most` bus and core driver, then initializes configfs static groups. Hardware modules call `most_register_interface()` with an initialized `struct most_interface`. The core validates callbacks, allocates an interface-private object and ID, adds the parent interface device to the MOST bus, creates one child channel device per advertised channel, initializes locks/FIFOs/config, and calls `most_interface_register_notify()` so configfs-created links can bind to newly available interfaces.

Components register through `most_register_component()` and are later linked to channels by `most_add_link()`, which locates the channel and component, assigns an empty pipe slot, and calls the component's `probe_channel()`. Starting a channel via `most_start_channel()` acquires the HDM module, calls the interface `configure()` callback with current channel config, allocates MBOs and coherent buffers, starts an enqueue kthread, partitions buffers between two component pipes, and increments the calling component's ref count.

For TX, components take buffers from `most_get_mbo()`, fill them, and submit through `most_submit_mbo()`, which queues to `halt_fifo` for the HDM enqueue thread. TX completion recycles buffers through `arm_mbo()`. For RX, buffers are initially queued to the HDM; `most_read_completion()` routes received MBOs to linked component `rx_completion()` callbacks or requeues them. Stopping a channel stops the enqueue thread, module-puts the HDM, poisons the channel, calls `poison_channel()`, flushes FIFOs/trash, waits for MBO cleanup, and decrements pipe refs.

## State and persistence
State is in memory only: bus devices, channel config, component links, buffer pools, FIFO lists, IDA IDs, kthreads, and module references. There is no disk persistence. Sysfs exposes current capabilities/settings but does not store them.

## Dependencies and integration points
The file depends on Linux device/bus/sysfs APIs, kthreads, wait queues, lists, spinlocks, mutexes, completions, atomic counters, DMA helpers, IDA, and MOST public types from `<linux/most.h>`. It integrates with configfs through `configfs_init()` and `most_interface_register_notify()`.

## Risks and edge cases
- Component list and link operations are not guarded by an obvious global mutex; runtime safety depends on higher-level registration/link sequencing.
- Two components may share one channel through `pipe0` and `pipe1`; buffer partitioning and ref counting need careful testing.
- `most_stop_channel()` decrements refs after teardown decisions; incorrect caller pairing can underflow pipe refs.
- MBO cleanup waits on `mbo_ref`; leaks or missing completion callbacks can hang stop.
- `most_register_interface()` error cleanup must unwind partially registered channel devices correctly.

## Test signals
Test component registration/deregistration, interface registration with 0/1/many channels, configfs link creation before and after interface registration, start/stop with one and two components, RX/TX completion routing, starvation reporting, `most_stop_enqueue()`/`most_resume_enqueue()`, HDM enqueue failure, poison cleanup, sysfs `links`/`components`, and module unload ordering.
