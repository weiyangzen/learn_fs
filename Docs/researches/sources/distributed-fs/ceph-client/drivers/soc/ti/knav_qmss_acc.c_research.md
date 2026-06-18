# sources/distributed-fs/ceph-client/drivers/soc/ti/knav_qmss_acc.c

## Purpose
This file implements accumulator-backed notification support for Keystone QMSS queue ranges. Accumulator firmware running on a PDSP writes descriptor lists into DMA memory and signals interrupts; this driver converts those lists into per-queue software descriptor rings and invokes queue notifiers.

## Important APIs, Types, And Functions
The exported entry point is `knav_init_acc_range`. Range operations are `knav_acc_set_notify`, `knav_acc_init_queue`, `knav_acc_open_queue`, `knav_acc_close_queue`, `knav_acc_init_range`, and `knav_acc_free_range`. Core helpers are `knav_acc_int_handler`, `knav_range_setup_acc_irq`, `knav_acc_write`, `knav_acc_setup_cmd`, `knav_acc_start`, and `knav_acc_stop`.

## Control Flow
`knav_init_acc_range` parses the `accumulator` property, finds a started PDSP, validates channel/pacing/multi-queue constraints, allocates one or more double-buffered accumulator lists, maps them for DMA, and installs accumulator range ops. Queue initialization allocates a 1024-entry software descriptor array. Opening the first queue requests the IRQ. The ISR handles retriggers first, then syncs the active list for CPU access, decodes entries, updates per-queue descriptor arrays and `desc_count`, notifies clients, clears the list, syncs back to device, flips buffers, resets the interrupt count, and writes EOI.

## State And Persistence
State is held in `range->acc`, `knav_acc_channel` list buffers, `list_index`, `open_mask`, `retrigger_count`, per-queue `descs/head/tail/count`, and PDSP command registers. Firmware configuration persists until channel stop/free.

## Dependencies And Integration Points
It depends on PDSP firmware having been loaded and started by the queue driver, IRQ mappings from the queue range, DMA mapping APIs, and `knav_queue_notify`. It is selected per queue range by the presence of the `accumulator` device-tree property and optional `multi-queue`.

## Risks And Test Signals
Risks include unbounded polling in `knav_acc_write`, dropped descriptors when the software ring reaches `ACC_DESCS_MAX`, malformed multi-queue entries, DMA sync mistakes, and IRQ affinity setup failure paths. Test signals include working accumulator IRQ delivery, correct descriptor count changes, notifier callbacks on pending descriptors, firmware command result `success`, and clean IRQ free/unmap during range teardown.
