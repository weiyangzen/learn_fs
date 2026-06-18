
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-17x.c

## Purpose
Implements VFE 17x hardware ops for a newer bus-oriented VFE generation. It focuses on RDI write-master streaming, bus IRQ/status handling, reset acknowledgement, register updates, and buffer completion.

## Important APIs, Types, and Functions
Exports `vfe_ops_170`. Important functions include `vfe_global_reset()`, `vfe_wm_start()`, `vfe_wm_update()`, `vfe_reg_update()`, `vfe_enable_irq_common()`, `vfe_isr()`, `vfe_get_output()`, `vfe_enable()`, `vfe_isr_reg_update()`, and `vfe_isr_wm_done()`. It installs `vfe_isr_ops_170` and `vfe_video_ops_170`.

## Control Flow
Reset masks reset ack and writes broad reset bits. Enabling the first stream enables common IRQs, reserves one WM for the line, and calls generic v2 output enable. WM start configures debug/status, address sync, CGC override, burst, default width/stride, packer, and MIPI RAW mode. IRQ handling clears top and bus statuses, dispatches reset ack, RDI reg-update, RDI SOF, composite done, and WM done. WM done timestamps and sequences the completed buffer, rotates queued buffers, updates the next address, and completes the vb2 buffer.

## State and Persistence
Uses `vfe->reg_update`, `stream_count`, `wm_output_map`, and each line's `vfe_output` buffers/state. There is no durable state outside registers and in-memory queues.

## Dependencies and Integration Points
Depends on generic VFE helpers in `camss-vfe.c`, v2 queue/output helpers, vb2 completion, and CAMSS PM-domain functions. It is selected through SoC resource `vfe_hw_ops`.

## Risks and Test Signals
The ISR checks `STATUS_1_RDI_SOF()` against `status0`, which is suspicious because that macro belongs to status1. WM done requires correct `wm_output_map` before dereferencing. Test reset completion, RDI register update completion, buffer rotation under empty queue, stream_count unwind, and overflow/violation visibility.
