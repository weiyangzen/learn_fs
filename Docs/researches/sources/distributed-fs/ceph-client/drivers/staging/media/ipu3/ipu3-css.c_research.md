# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css.c

## Purpose
`ipu3-css.c` is the main IPU3 CSS control layer. It negotiates formats and firmware binaries, powers/boots hardware, allocates firmware-visible structures, starts/stops streaming, queues/dequeues buffers, submits parameters, and acknowledges interrupts.

## Important APIs, Types, and Functions
- Public CSS API: init/cleanup, format try/set, metadata format sizing, buffer queue/dequeue, streaming state, parameter set, and queue-empty helpers.
- Hardware API: `imgu_css_set_powerup()`, `imgu_css_set_powerdown()`, and `imgu_css_irq_ack()`.
- Internal paths boot firmware, initialize pipelines, allocate common and binary-specific DMA maps, and operate host/SP queue rings.

## Control Flow
Initialization sets default pipe state, allocates per-pipe ABI maps and pools, allocates the shared SP group, and initializes firmware. Format try/set clamps and aligns formats/rectangles, derives effective/BDS/envelope/GDC geometry, finds a compatible binary, and commits adjusted queues and rectangles.

Streaming startup resizes binary-specific maps, initializes/boots hardware and SPs, builds pipeline stage/group structures, enables IRQs, submits default parameters, drains old queues, and sends start events. Stop sends stop events, halts hardware, cleans pools, marks outstanding buffers failed, and clears streaming.

Buffer queueing fills an ABI buffer with a user DMA address, links the software buffer, queues the ABI buffer IOVA to firmware, and sends a buffer-enqueued event. Dequeue reads firmware events, maps event types to CSS queues, dequeues the ABI buffer address, verifies software/FW FIFO agreement, and returns the completed buffer.

## State and Persistence Behavior
Top-level CSS state stores device/register/firmware pointers, firmware binary maps, streaming flag, enabled-pipe bitmap, and per-pipe state. Per-pipe state stores queue formats and lists, rectangles, selected binary, common maps, binary parameter maps, auxiliary frames, parameter pools, and ABI buffer maps.

## Dependencies and Integration Points
The file integrates V4L2 formats, IPU3 firmware metadata, DMA/MMU mapping, parameter conversion, static tables, hardware registers, and interrupt-driven buffer completion. Queue lists are protected by per-pipe spinlocks.

## Risks
- `imgu_css_queue_empty()` initializes its aggregate result to false, making it always return false.
- `imgu_css_buf_queue()` removes a just-linked buffer on queueing failure without taking `qlock`, which is a concurrency concern.
- Startup has complex partial-failure cleanup requirements across hardware, firmware, maps, and pools.
- Buffer completion depends on firmware queue positions matching software FIFO order.
- Hardware/firmware ABI drift or register polling timeouts can break streaming.

## Test Signals
Test supported and invalid format negotiation, binary selection boundaries, streaming start/stop, parameter queue rollback, buffer FIFO completion, invalid/unknown events, IRQ ack paths, and injected allocation/startup failures. Hardware tests should monitor firmware warnings/asserts and buffer states on stop.
