# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_v4l2.h

Purpose: Declares the shared Amphion V4L2 helper API exported by `vpu_v4l2.c` for encoder, decoder, command, and message-handling code.

Important APIs: It exposes instance locking, vb2/V4L2 buffer state and average-QP accessors, open/close entry points, common format sizing/validation, output and capture processing triggers, source-buffer lookup/skip helpers, error notification, source-change notification, last-buffer-dequeued handling, buffer counts, source queue emptiness checks, physical DMA address lookup, and `vpu_get_format()`.

Control flow and state: This header has no control flow except `vpu_get_format()`, which selects `inst->out_format` for output queue types and `inst->cap_format` otherwise. Its declarations establish that V4L2-facing code manipulates per-instance lock-protected state, vb2 buffer metadata, and V4L2 event state managed by the implementation.

Dependencies and integration: Depends on Linux V4L2 type definitions and implicit Amphion structs from including contexts. Used by encoder/decoder ops, firmware frame submission, and common queue management.

Risks: Because the header forward-declares behavior without local type declarations for every struct, include order matters. Misusing `vpu_get_format()` with non-video or malformed queue types would fall through to capture format.

Test signals: Compile coverage across all Amphion units, output/capture queue format access in encoder and decoder paths, and buffer lookup helpers under queued, processing, and drained states.
