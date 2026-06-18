<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen1.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen1.c

## Purpose
Implements common VFE generation-1 streaming and buffer handling used by older Qualcomm CAMSS VFE hardware families such as 4.1/4.7/4.8. It bridges the generic VFE line and video-node code to generation-specific register operations supplied through `struct vfe_hw_ops_gen1`.

## Important APIs, Types, And Functions
- Exports `vfe_gen1_enable()`, `vfe_gen1_disable()`, `vfe_gen1_halt()`, `vfe_word_per_line()`, `vfe_isr_ops_gen1`, and `vfe_video_ops_gen1`.
- Uses `struct vfe_line`, `struct vfe_output`, `struct vfe_device`, and `struct camss_buffer` from the shared CAMSS VFE/video layers.
- Key helpers reserve write masters, initialize ping/pong addresses, program frame-drop patterns, update active buffers, and translate hardware interrupts into VB2 buffer completion.

## Control Flow
Stream-on increments `vfe->stream_count`, enables common IRQ/write-interface state on the first stream, reserves one or more write masters depending on pixel format, primes up to two buffers, configures RDI or PIX blocks, and triggers a register update. Stream-off waits for a next SOF and register-update acknowledgement, disables write masters, disconnects RDI or stops CAMIF for PIX, releases output resources, and disables the write interface when the last stream stops. Interrupt flow is split through `vfe_isr_ops_gen1`: SOF completes pending shutdown waits, register-update completes synchronization or restarts queued captures after stopping, WM-done advances ping/pong buffers and calls `vb2_buffer_done()`, and composite-done routes PIX completion.

## State And Persistence
All state is in-memory driver state: `stream_count`, `output->state`, pending buffer lists, ping/pong slots, `last_buffer`, frame-drop update index, `sequence`, and completion objects. No persistent storage is touched. Concurrency is protected with `stream_lock` and `output_lock`; completion waits synchronize with ISR callbacks.

## Dependencies And Integration Points
Depends on V4L2 media graph sensor discovery for frame-skip information, VB2 for buffer lifecycle, and hardware-specific Gen1 callbacks for bus, CAMIF, WM, IRQ, scaler/crop, and QoS programming. It is selected by SoC VFE resource tables in `camss.c` through `vfe_ops_4_1`, `vfe_ops_4_7`, or `vfe_ops_4_8` implementations.

## Risks And Edge Cases
Timeouts on SOF, register update, or halt indicate stuck hardware and only log or return errors depending on path. Buffer starvation drives frame-drop patterns and delayed `last_buffer` completion, so state transitions around `STOPPING`, `SINGLE`, and `CONTINUOUS` are sensitive. Multi-plane formats depend on correct WM count and address indexing. The disabled `active_buf` mismatch check (`&& 0`) hides a potential hardware/status inconsistency.

## Test Signals
Useful signals are successful stream-on/off on RDI and PIX lines, correct frame sequence/timestamps, no missing-buffer or unmapped-WM ratelimited errors, no SOF/reg-update/halt timeouts, and VB2 buffers returning `DONE` or expected error states under queue starvation and stream stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen1.c -->
