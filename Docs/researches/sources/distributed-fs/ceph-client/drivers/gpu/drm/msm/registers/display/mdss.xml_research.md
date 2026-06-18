# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdss.xml

## Purpose
This XML file describes the top-level Qualcomm MDSS register block used around the MDP/display subsystem. It is a small RNN database focused on MDSS hardware version, interrupt summary, and UBWC static/control registers.

## Important APIs, Types, And Data
The `MDSS` 32-bit domain defines `HW_VERSION` with `STEP`, `MINOR`, and `MAJOR` fields. `HW_INTR_STATUS` exposes summary bits for MDP, DSI0, DSI1, HDMI, and eDP interrupts. UBWC registers include `UBWC_DEC_HW_VERSION`, `UBWC_STATIC`, `UBWC_CTRL_2`, and `UBWC_PREDICTION_MODE`; `UBWC_STATIC` encodes swizzle, bank spread, highest bank bit, min access length, AMSBC, and macrotile mode.

## Control Flow, State, And Integration
Generation converts these descriptions into accessors used by MSM display code to identify MDSS revisions, route top-level interrupts, and configure UBWC-related display memory behavior. The file models volatile SoC-global display state. It integrates with generated display headers rather than directly with C source.

## Risks And Test Signals
The `HIGHEST_BANK_BIT` comment notes that older UBWC revisions used a narrower field, so version-specific programming must interpret the generated macro correctly. Incorrect interrupt bits would break display IRQ demultiplexing. Test signals include generated headers compiling, MDSS version reads matching hardware, DSI/HDMI/eDP interrupt handling working, and UBWC framebuffers scanning out without corruption across supported SoCs.
