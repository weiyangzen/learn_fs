# sources/distributed-fs/ceph-client/drivers/scsi/isci/isci.h

## Purpose

`isci.h` is the common constants, status-code, timer, and base state-machine header for the Intel C600 SAS driver. It defines global hardware limits, BAR layout, queue sizes, completion-frame limits, transfer limits, SCI status enumerations, endian conversion helper, IRQ prototypes, and the minimal state-machine abstraction used by host, phy, port, device, and request code.

## Important APIs, Types, and Functions

Important constants include `DRV_NAME`, BAR indexes and sizes, MSI-X vector counts, `ISCI_CAN_QUEUE_VAL`, controller stop timeout, invalid IO tag value, and all `SCI_MAX_*` limits for phys, ports, SMP phys, remote devices, IO requests, sequence numbers, controllers, domains, scatter-gather elements, and completion queue sizing. The SCU queue definitions combine critical notifications, events, unsolicited frames, IO requests, and scratch entries into `SCU_MAX_COMPLETION_QUEUE_ENTRIES`.

`check_sizes()` provides compile-time assertions that event, unsolicited-frame, completion-queue, IO-request, and sequence limits remain power-of-two where required. `enum sci_status` defines generic controller/device/request statuses; `enum sci_io_status` and `enum sci_task_status` map IO and task-specific names onto those generic values. `sci_swab32_cpy()` converts dword-swapped SCU frame data to standard memory layout. `struct sci_timer` wraps `timer_list` with a cancel flag and helpers `sci_init_timer()`, `sci_mod_timer()`, and `sci_del_timer()`. `struct sci_base_state_machine` and `struct sci_base_state` define the enter/exit callback table model, with `sci_init_sm()` and `sci_change_state()` implemented in `host.c`.

## Control Flow

The header does not own runtime flow, but its types shape all driver state machines. Callers initialize a `sci_base_state_machine` with a state table and initial ID, then transition through `sci_change_state()`, which calls exit and enter hooks. Timer users call `sci_mod_timer()` to arm and `sci_del_timer()` to set `cancel` before deleting; callbacks check `cancel` under the relevant lock. Status values returned from controller, phy, port, device, IO, and task functions determine whether callers continue posting hardware commands, wait for async completion, retry, or fail upward to libsas/SCSI.

## State and Persistence Behavior

`isci.h` defines no persistent storage. Its constants are compile-time state shaping DMA allocations, queue masks, tag encoding, and firmware-visible limits. `struct sci_timer.cancel` is transient synchronization state that prevents callbacks deleted under `scic_lock` from acting on stale timers.

## Dependencies and Integration Points

The header includes Linux interrupt and type definitions. It integrates with the rest of the driver through shared constants and status values, with hardware register code through SCU limits, with libsas and SCSI through queue depths and protocol status mapping, and with IRQ setup through the `isci_msix_isr()`, `isci_intx_isr()`, and `isci_error_isr()` prototypes.

## Risks and Edge Cases

Changing any `SCI_MAX_*` value can break power-of-two assumptions, tag bit packing, completion queue masks, DMA table sizes, or hardware capacity comparisons. `SCU_MAX_COMPLETION_QUEUE_SHIFT` uses `ilog2()` on the computed entry count and expects the compile-time checks to keep that count a power of two. `sci_timer` deletion is not equivalent to `timer_delete_sync()` in all paths; users must honor the cancellation convention. Status enums are shared across layers, so adding or reordering values can affect IO/task aliases.

## Test Signals

Build-time `BUILD_BUG_ON*` checks are the first signal. Runtime signals include stable tag sequence masking, completion queue wraparound behavior, timers not firing after cancellation, and consistent status propagation from low-level SCI functions to libsas task completion and error handling.
