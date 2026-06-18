# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_core.h

## Purpose
This header is the central data model for the legacy MediaTek MDP driver. It defines pixel format metadata, frames, controls, variant limits, the global device object, and per-file V4L2 mem2mem context.

## Important APIs, Types, and Functions
Important types include `struct mtk_mdp_fmt`, `struct mtk_mdp_frame`, `struct mtk_mdp_variant`, `struct mtk_mdp_dev`, and `struct mtk_mdp_ctx`. It defines format flags, VPU/context state bits, module name, shutdown timeout, and debug macros. It declares component registration helpers and exports `mtk_mdp_dbg_level`.

## Control Flow
Most source files include this header. The core populates `struct mtk_mdp_dev`; the mem2mem frontend allocates and configures `struct mtk_mdp_ctx`; register/VPU helper code consumes the context to fill shared VPU configuration.

## State and Persistence
`struct mtk_mdp_dev` stores driver-global runtime state for the platform binding. `struct mtk_mdp_ctx` stores per-open-file configuration, V4L2 controls, colorimetry, VPU instance state, and queued work. None of this is durable beyond module/device lifetime.

## Dependencies and Integration Points
The header integrates V4L2 controls, V4L2 device/mem2mem, videobuf2 DMA-contig, MediaTek VPU state, and MDP component definitions.

## Risks and Edge Cases
Many fields are shared across ioctl, queue, worker, watchdog, and release paths, so lock ownership matters. The header references `struct mtk_mdp_pix_limit` before its definition appears in `mtk_mdp_m2m.c`, so the pointer-only use is intentional. Debug macros compile out unless `DEBUG` is defined, which can hide diagnostics in production builds.

## Test Signals
Compile with and without `DEBUG`, run V4L2 format/control/streaming tests across multiple simultaneous contexts, and validate watchdog context-state transitions.
