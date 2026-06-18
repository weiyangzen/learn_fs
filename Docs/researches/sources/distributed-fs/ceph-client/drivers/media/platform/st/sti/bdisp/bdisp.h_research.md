# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp.h

Purpose: provides the shared BDisp driver data model and internal function declarations used by the V4L2, hardware, and debugfs implementation files.

Important APIs and types: defines `BDISP_NAME`, node count limits, `struct bdisp_fmt`, `struct bdisp_frame`, `struct bdisp_request`, `struct bdisp_ctx`, `struct bdisp_m2m_device`, `struct bdisp_dbg`, and `struct bdisp_dev`. Function declarations expose hardware lifecycle/submission helpers and debugfs/performance hooks across compilation units.

Control flow: no executable flow is present, but the types define the ownership graph. A platform-level `bdisp_dev` owns the V4L2 device, mem2mem device, register/clock resources, IRQ waitqueue, timeout work, and debug state. Each open file owns a `bdisp_ctx`, which carries the active source/destination frames, controls, and DMA node descriptors.

State and persistence: all state is runtime-only. `bdisp_frame` records negotiated geometry, colorspace, crop, and DMA plane addresses. `bdisp_request` and `bdisp_dbg` preserve the last submitted operation for diagnostics. `bdisp_dev->state` and `bdisp_ctx->state` are in-memory synchronization flags.

Dependencies and integration points: includes Linux clock/platform/spinlock/time headers, V4L2 controls/devices/mem2mem, and videobuf2 DMA-contig. It deliberately forward-shares internals across the local BDisp driver rather than exposing a public kernel API.

Risks: because this header carries cross-file internals, changing structure fields affects hardware programming, V4L2 control logic, and debugfs simultaneously. `MAX_NB_NODE` encodes current assumptions of two output planes and two width strides; new formats or wider hardware capabilities require revisiting node allocation and build logic.

Test signals: compile all BDisp compilation units after structural changes, then run open/close, format negotiation, debugfs last-node/request inspection, and multi-plane/large-width jobs to confirm the shared structures remain coherent.
