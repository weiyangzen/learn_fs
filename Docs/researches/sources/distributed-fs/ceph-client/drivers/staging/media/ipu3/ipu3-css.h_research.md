# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css.h

## Purpose
`ipu3-css.h` defines the public CSS interface and core IPU3 image-processing state structures.

## Important APIs, Types, and Functions
- Queue, rectangle, pipe, and buffer-state constants model CSS firmware concepts.
- `struct imgu_css_buffer`, `imgu_css_format`, `imgu_css_queue`, `imgu_css_pipe`, and `imgu_css` define buffer metadata, queue format state, per-pipe memory, and global CSS state.
- Public functions cover init/cleanup, format negotiation, metadata sizing, buffer queue/dequeue, streaming lifecycle, power/IRQ handling, and parameters.
- Inline helpers report buffer state and initialize buffer metadata.

## Control Flow
External driver code sets formats, starts streaming, initializes/queues buffers, dequeues completed buffers after events, updates parameters, and stops streaming through this interface.

## State and Persistence Behavior
`struct imgu_css_pipe` persists queue lists, selected binary, rectangles, ABI maps, auxiliary frames, and parameter pools. `struct imgu_css` persists firmware/hardware state and the enabled pipe bitmap. Buffers transition NEW to QUEUED to DONE/FAILED.

## Dependencies and Integration Points
The header ties V4L2 types, IPU3 ABI structures, CSS pools, firmware handling, DMA mapping, and the V4L2 IPU3 driver together.

## Risks
The state structures mix software-only queues/locks with firmware-visible IOVAs. Callers must honor queue IDs, pipe IDs, streaming state, and list-head initialization assumptions.

## Test Signals
Exercise public API preconditions, metadata size constants, buffer state transitions, and multiple-pipe isolation.
