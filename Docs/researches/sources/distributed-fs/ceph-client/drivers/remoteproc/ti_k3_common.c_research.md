# sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_common.c

## Purpose
Shared implementation for TI K3 remoteproc drivers. It handles mailbox callbacks/kicks, TI-SCI and reset-controller sequencing, prepare/unprepare, start/stop, IPC-only attach/detach, loaded resource-table lookup, device-address translation, internal SRAM mapping, reserved-memory setup, and cleanup helpers.

## Important APIs, Types, And Functions
Exports `k3_rproc_mbox_callback()`, `k3_rproc_kick()`, `k3_rproc_reset()`, `k3_rproc_release()`, `k3_rproc_request_mbox()`, `k3_rproc_prepare()`, `k3_rproc_unprepare()`, `k3_rproc_start()`, `k3_rproc_stop()`, `k3_rproc_attach()`, `k3_rproc_detach()`, `k3_get_loaded_rsc_table()`, `k3_rproc_da_to_va()`, `k3_rproc_of_get_memories()`, `k3_mem_release()`, `k3_reserved_mem_init()`, and `k3_release_tsp()`.

## Control Flow
Mailbox callback handles crash and echo messages specially, ignores ready/control messages, drops unknown values above `max_notifyid`, and routes queue IDs to `rproc_vq_interrupt()`. Kicks send the vqid over the mailbox. Reset/release choose local reset control or TI-SCI module get/put depending on `uses_lreset`.

Prepare skips detached IPC-only cores; otherwise it asserts local reset when applicable, verifies assertion, and deasserts module reset through TI-SCI so internal RAM can be loaded. Unprepare asserts module reset unless detaching. Start releases reset; stop asserts reset. Attach/detach are NOPs for IPC-only mode. Memory setup maps named internal resources and reserved memory; reserved index 0 is the vring DMA pool and later regions are static carveouts.

## State And Persistence Behavior
`struct k3_rproc` stores internal and reserved memory mappings, TI-SCI handles, reset control, mailbox, device pointer, and SoC data. Most resources are devm-managed. IPC-only mode assumes the resource table is at reserved memory region 1 base and returns a fixed 256-byte window.

## Dependencies And Integration Points
Depends on TI-SCI device/processor control, reset controller, OMAP mailbox constants, reserved-memory DT entries, platform memory resources named by SoC data, and remoteproc core/virtio. DSP and M4 drivers compose this layer with their own compatible-specific memory tables and boot rules.

## Risks
Crash mailbox messages are logged but do not call `rproc_report_crash()`, and K3 wrappers disable recovery. IPC-only resource table size is hard-coded to 256 bytes and assumes reserved-memory ordering. Reserved-memory device addresses truncate to 32-bit physical starts. Address range checks should be reconsidered if future 64-bit addresses are allowed. Mailbox filtering relies on `max_notifyid` initialization.

## Test Signals
Test mailbox echo/ready/queue/crash/unknown messages, local-reset and module-reset platforms, prepare/unprepare balance, internal SRAM and reserved DDR translation, IPC-only resource-table discovery, too few reserved-memory regions, mailbox deferral, and repeated boot/stop cycles with TI-SCI tracing.
