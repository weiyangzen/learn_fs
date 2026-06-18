# sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/driver.c

## Purpose
Implements the Arm FF-A core interface driver. It discovers firmware version/capabilities, maps RX/TX buffers, enumerates FF-A partitions as bus devices, exposes messaging/memory/CPU/notification ops to clients, and manages notification interrupts and callbacks.

## APIs, Types, And Functions
The central runtime object is global `struct ffa_drv_info`, containing firmware version, local VM ID, RX/TX buffer locks and pages, feature flags, notification IRQ/workqueue state, partition xarray, and notification callback hash. Exported client-facing behavior is grouped into `struct ffa_ops`: info ops (`api_version_get`, `partition_info_get`), message ops (`sync_send_receive`, `indirect_send`, `sync_send_receive2`, `mode_32bit_set`), memory ops (`memory_share`, `memory_lend`, `memory_reclaim`), CPU op (`run`), and notifier ops.

## Control Flow
`ffa_init()` obtains the transport call function, allocates `drv_info`, negotiates FF-A version, gets the local VM ID, sizes and maps RX/TX buffers, initializes locks and feature flags, sets up notifications, and enumerates partitions. Partition discovery uses either buffer-based `FFA_PARTITION_INFO_GET` or register-based `FFA_PARTITION_INFO_GET_REGS`, then registers `struct ffa_device` entries on the FF-A bus and tracks per-partition callback records in an xarray.

Direct messaging packages arguments into FF-A direct request calls and waits through `FFA_INTERRUPT`/`FFA_YIELD` by issuing `FFA_RUN`. Indirect messaging writes an `ffa_indirect_msg_hdr` and payload into the TX buffer. Memory share/lend builds an FF-A memory region descriptor from endpoint attributes and scatterlists, fragments it across TX buffer limits, and transmits through `MEM_SHARE`/`MEM_LEND`, with reclaim using the returned global handle.

Notification setup creates a bitmap when supported, maps schedule-receiver and notification-pending interrupts, registers per-CPU IRQ handlers, creates a workqueue, and enables CPU hotplug callbacks. Notification callbacks are registered in a hash table, bound/unbound with firmware for normal notifications, and invoked from bitmap retrieval or framework RX-buffer notifications.

## State, Persistence, And Dependencies
State is runtime-only: RX/TX pages shared with firmware, mapped FF-A buffers, partition device registrations, xarray/list callback records, notification hash entries, per-CPU IRQ registrations, CPU hotplug state, workqueue work items, and feature flags. No disk persistence exists. Dependencies include SMCCC transport, FF-A public ABI, device core, xarray, hashtable, scatterlist/DMA page helpers, OF/ACPI IRQ mapping, CPU hotplug, and workqueues.

## Integration Points
The driver registers at `rootfs_initcall()` so FF-A devices appear early. It integrates with `arm_ffa` bus helpers, client drivers through `struct ffa_ops`, firmware via `invoke_ffa_fn`, IRQ infrastructure for donated interrupt IDs, and bus notifiers to resolve UUIDs on FF-A v1.0 systems that only expose partition IDs initially.

## Risks And Test Signals
High-risk areas include RX/TX buffer locking, RX release timing, memory descriptor fragmentation, native vs 32-bit FF-A response packing, partition discovery format differences across FF-A versions, notification callback lifetime under interrupts, IRQ cleanup on partial setup, and host partition registration failures. Test signals are FF-A firmware boot logs, partition device sysfs entries, direct/indirect message round trips, memory share/lend/reclaim exercises, notification bind/send/callback tests, CPU hotplug with per-CPU IRQs, and module unload cleanup. Static analysis should also inspect the notification loop bounds and error unwind paths.
