<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen1.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen1.h

## Purpose
Declares the generation-1 VFE abstraction layer used by older CAMSS hardware. It separates common Gen1 streaming logic from per-revision register programming.

## Important APIs, Types, And Functions
- Defines `struct vfe_hw_ops_gen1`, a large callback table for bus connect/disconnect, write-interface control, IRQ control, CAMIF control, module/scaler/crop/demux programming, QoS, xbar setup, UB configuration, ping/pong addresses, frame-drop control, and WM enable/status.
- Provides `vfe_calc_interp_reso()` for scaler interpolation mode selection.
- Declares `vfe_gen1_enable()`, `vfe_gen1_disable()`, `vfe_gen1_halt()`, `vfe_word_per_line()`, `vfe_isr_ops_gen1`, and `vfe_video_ops_gen1`.

## Control Flow
The header has no runtime control flow, but it defines the required callback contract consumed by `camss-vfe-gen1.c`. SoC-specific VFE files populate these callbacks, the shared VFE resource table stores them in `vfe->ops_gen1`, and stream enable/disable paths invoke them in hardware-programming order.

## State And Persistence
No state is owned here. The declarations operate on `struct vfe_device`, `struct vfe_line`, and `struct vfe_output` instances owned by `camss-vfe.h` and initialized by `camss-vfe.c`.

## Dependencies And Integration Points
Includes `camss-vfe.h` and relies on V4L2 pixel format types through callback signatures. Its exported declarations are the integration point between generic VFE code and revision-specific register files such as VFE 4.x implementations.

## Risks And Edge Cases
The callback table is broad and has no capability flags, so every Gen1 hardware implementation must provide semantically compatible functions. Mismatched UB sizing, WM status semantics, or PIX/RDI IRQ wiring can cause dropped frames or stalled shutdowns. The comment above `vfe_gen1_halt()` says `vfe_gen1_enable`, which is a documentation typo.

## Test Signals
Build coverage verifies all Gen1 ops tables satisfy the callback signatures. Runtime signals are the Gen1 stream and interrupt tests covered by `camss-vfe-gen1.c`, especially RDI/PIX enable, halt completion, and address update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen1.h -->
