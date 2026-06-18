# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_rcfw.c

## Purpose
`qplib_rcfw.c` implements the RDMA controller firmware communication channel. It allocates and maps CMDQ/CREQ rings, posts firmware commands into 16-byte command slots, waits for or polls completions, dispatches async function and QP events, initializes/deinitializes firmware, and manages CREQ interrupts.

## Important APIs, types, and functions
The main public APIs are `bnxt_qplib_alloc_rcfw_channel()`, `bnxt_qplib_enable_rcfw_channel()`, `bnxt_qplib_rcfw_send_message()`, `bnxt_qplib_init_rcfw()`, `bnxt_qplib_deinit_rcfw()`, `bnxt_qplib_rcfw_start_irq()`, `bnxt_qplib_rcfw_stop_irq()`, `bnxt_qplib_disable_rcfw_channel()`, and `bnxt_qplib_free_rcfw_channel()`. Internal helpers cover return-code mapping during device detach, firmware-stall detection, sleep wait, busy blocking wait, polling wait, command posting, no-wait cleanup commands, CREQ processing, and QP-event table lookup.

## Control flow
Channel allocation creates CREQ and CMDQ HWQs plus the shadow response table. Enabling maps the CMDQ mailbox on BAR0, maps the CREQ consumer doorbell on BAR2, installs the CREQ MSI-X handler, initializes the nonblocking command semaphore, and writes the firmware channel init structure. A caller prepares a command and response buffer, then `bnxt_qplib_rcfw_send_message()` throttles nonblocking commands, validates firmware state, copies request bytes into CMDQ slots, stamps a cookie, rings mailbox registers, and waits through blocking, interrupt-driven wait, or polling mode. CREQ tasklets validate completions, copy responses to waiter buffers, advance CMDQ consumers, wake waiters, dispatch async QP/function events, and ring the CREQ consumer doorbell.

## State and persistence
`struct bnxt_qplib_rcfw` stores the PCI device, resource pointer, CMDQ/CREQ contexts, command response table, QP lookup table, timeout/stall flags, inflight semaphore, interrupt-enabled counter, last firmware-seen timestamp, and feature flags such as RoCE mirror. Firmware initialization writes context table addresses and flags to hardware and persists until deinitialize or device reset.

## Dependencies and integration points
The file depends on qplib resource HWQ allocation, `roce_hsi.h` command/CREQ layouts, qplib fast-path QP error marking, qplib slow-path command users, Linux IRQ/tasklet/waitqueue/semaphore APIs, PCI BAR mapping, and the AEQ callback supplied by `main.c`.

## Risks
Timeout handling is subtle: `-ENODEV` firmware stall is collapsed to `-ETIMEDOUT` for callers while also setting `FIRMWARE_STALL_DETECTED`. `bnxt_qplib_map_rc()` intentionally returns success for destroy-like commands during device detach, which can hide real cleanup failures outside recovery. Late successful `CREATE_AH` completions are followed by no-wait `DESTROY_AH`; a failed destroy can leak firmware AH state. `bnxt_qplib_map_creq_db()` logs missing BAR base but does not immediately return before computing `bar_reg`. Command response table entries rely on cookie reuse only after completions advance. CREQ QP events trust qp table hashing and firmware QP IDs.

## Test signals
Test command send before and after firmware initialization, nonblocking semaphore throttling, CMDQ full, interrupt-enabled wait, polling wait with interrupts disabled, blocking wait, firmware detach, firmware stall, late waiter death for create AH, CREQ IRQ restart, async QP error dispatch, function event dispatch, initialize/deinitialize flags, and BAR mapping failures. Fault injection around wait timeouts and response status is especially valuable.
