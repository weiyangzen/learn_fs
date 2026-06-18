# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com.c

## Purpose

`efa_com.c` implements the EFA communication layer around device MMIO registers, admin submission/completion queues, asynchronous event queue, event queues, admin command execution, version/DMA capability validation, and device reset. It is the low-level command transport used by EFA probe and verbs command wrappers.

## Important APIs, Types, and Functions

- MMIO readless path: `efa_com_mmio_reg_read_init`, `efa_com_reg_read32`, `efa_com_mmio_reg_read_destroy`.
- Admin queue lifecycle: `efa_com_admin_init`, `efa_com_admin_destroy`, `efa_com_admin_init_sq`, `efa_com_admin_init_cq`, and `efa_com_admin_init_aenq`.
- Command contexts: `efa_comp_ctx`, `efa_com_alloc_comp_ctx`, `efa_com_dealloc_comp_ctx`, and command ID mapping helpers.
- Command execution: `efa_com_cmd_exec`, `efa_com_submit_admin_cmd`, `__efa_com_submit_admin_cmd`, `efa_com_wait_and_process_admin_cq`, and polling/interrupt wait variants.
- Interrupt/event handling: `efa_com_admin_q_comp_intr_handler`, `efa_com_aenq_intr_handler`, `efa_com_eq_comp_intr_handler`, and `efa_com_arm_eq`.
- Device control: `efa_com_validate_version`, `efa_com_get_dma_width`, `efa_com_dev_reset`, `efa_com_eq_init`, and `efa_com_eq_destroy`.

## Control Flow

Admin init first verifies device-ready status through the MMIO readless register path, sets queue depth and polling mode, initializes completion contexts and semaphore capacity, allocates coherent ASQ/ACQ/AENQ rings, programs their base/capability registers, unmasks admin interrupts, reads timeout capability, and marks the queue running.

`efa_com_cmd_exec` sleeps on the available-command semaphore, allocates a completion context, writes a command into the ASQ under the SQ lock, assigns a command ID that combines context index and producer-counter entropy, rings the producer doorbell, then waits for completion. Completion processing scans ACQ entries by phase bit under the CQ lock, validates command ID/status, copies the completion into the caller buffer, and completes the wait event unless polling mode is active. Timeouts clear the running bit to prevent further submissions.

AENQ/EQ interrupt handlers scan phase-valid entries, invoke registered callbacks, advance consumer counters/phase, and ring consumer/arm doorbells. Reset writes the reset reason to device control, restores the MMIO read response address, waits for reset-in-progress on/off, and refreshes admin timeout.

## State and Persistence Behavior

Persistent state includes coherent DMA rings for ASQ/ACQ/AENQ/EQs, completion context pool/status, queue producer/consumer counters, phase bits, admin running/polling state bits, semaphore slots, atomic admin stats, MMIO read response buffer/sequence number, and device DMA width. Hardware register programming persists until reset or device removal; reset clears MMIO response address and requires reprogramming.

## Dependencies and Integration Points

This file depends on EFA register definitions, admin descriptor/command definitions, DMA coherent allocation, completions, semaphores, spinlocks, MMIO `readl/writel`, and RDMA device logging. Higher-level command wrappers call `efa_com_cmd_exec`; PCI probe calls version/DMA/admin init and reset; IRQ handlers call the admin/AENQ/EQ handlers.

## Risks and Edge Cases

- `efa_com_alloc_ctx_id` assumes the semaphore prevents pool underflow/overflow; any caller bypassing `efa_com_cmd_exec` could corrupt `comp_ctx_pool_next`.
- `efa_com_admin_init` cleanup frees `comp_ctx` but not `comp_ctx_pool` on one error path, while destroy frees both; init failure paths need leak checks.
- The source contains duplicated statements (`comp_size` assignment and nested `if (err)`), harmless but a signal for generated-code review.
- Timeout paths clear the running bit, causing later commands to fail with `-ENODEV`; recovery must reset/reinitialize admin queues.
- MMIO readless polling busy-waits with `udelay(1)` up to 50 ms under a spinlock, serializing all register reads.
- EQ completion handler always arms the EQ even when no entries were processed; this is probably intentional but should be validated against interrupt moderation semantics.

## Test Signals

Tests should cover admin init/destroy success and each allocation failure path, command execution in polling and interrupt modes, missing MSI-X completion fallback, no-completion timeout, bad command ID completion, status-to-errno mapping, AENQ unknown group callback, EQ create/destroy/interrupt handling, MMIO read timeout/wrong-offset handling, version/DMA width validation, and reset timeout/error cases.
