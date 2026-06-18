# sources/distributed-fs/ceph-client/include/video/metronomefb.h

## Purpose
`metronomefb.h` defines the memory layout and board callback contract for the Metronome e-paper framebuffer controller.

## Important APIs, Types, and Functions
`struct metromem_cmd` describes a 64-byte command packet with opcode, argument words, and checksum. `struct metronomefb_par` stores command, waveform, image, checksum, DMA, framebuffer, board, waitqueue, frame count, size, and timing data. `struct metronome_board` provides reset/standby, cleanup, event wait, interrupt setup, framebuffer and I/O setup, panel type query, shared memory pointer, framebuffer dimensions, waveform size, and host framebuffer pointer.

## Control Flow
The driver asks the board to set up I/O, framebuffer memory, IRQs, and panel metadata; then it fills command/image/waveform memory, computes checksums, toggles reset/standby lines, waits for controller events, and coordinates with the host LCD controller when present.

## State and Persistence Behavior
Runtime state includes DMA-backed metronome memory, frame counters, checksums, waitqueue state, and board callbacks. E-paper display contents can remain visible without refresh, but software state is transient and must be rebuilt after device reset.

## Dependencies and Integration Points
It integrates fbdev, DMA memory, wait queues, board/platform code, IRQ setup, and optional host LCD controller state. Board callbacks hide GPIO, memory-mapping, and event-delivery details.

## Risks and Test Signals
Risks include checksum mismatch, DMA buffer layout errors, incorrect waveform size, event wait deadlocks, reset/standby polarity mistakes, and host framebuffer coordination failures. Test signals include command checksum validation, full/partial update events, interrupt and polling wait paths, suspend/resume, cleanup after failed setup stages, and visual e-paper refresh correctness.
