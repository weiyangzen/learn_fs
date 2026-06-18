## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dp_reg.h

### Purpose

`mtk_dp_reg.h` defines the MMIO register offsets and bit fields consumed by the MediaTek DP/eDP bridge driver. It covers PHY analog controls, top-level power/IRQ/memory controls, encoder timing and audio registers, transmitter pattern/HPD/FEC/scrambler registers, and AUX engine registers.

### Important APIs, types, and functions

The header has no functions or types beyond preprocessor definitions. Important groups include PHY calibration fields (`DP_PHY_GLB_*`, `DP_PHY_LANE_TX_*`), top registers (`MTK_DP_TOP_PWR_STATE`, `MTK_DP_TOP_SWING_EMP`, `MTK_DP_TOP_IRQ_MASK`), encoder registers (`MTK_DP_ENC0_*`, `MTK_DP_ENC1_*`), transmitter registers (`MTK_DP_TRANS_*`), and AUX registers (`MTK_DP_AUX_*`). It also defines HPD event bits and SoC-specific audio M-code divider encodings.

### Control flow

There is no runtime control flow. `mtk_dp.c` uses these constants in regmap read/write/update operations to initialize the block, perform AUX transfers, program video timing, set color depth/format, train links, program audio SDP packets, and handle HPD IRQs.

### State and persistence behavior

The header owns no state. It describes persistent hardware state in DP/eDP registers, including power state, lane swing/pre-emphasis, HPD debounce thresholds and status, MSA timing, video/audio mute, FIFO thresholds, FEC/scrambler, SDP payload/header data, AUX FIFO/request/status, and PHY calibration.

### Dependencies

It depends on common Linux bit macros being available through including code. Its semantic dependency is `mtk_dp.c`; field names are matched directly to MediaTek register programming sequences.

### Integration points

The definitions are the low-level contract between `mtk_dp.c`, the DP PHY child device, and the hardware register map. Any bridge, AUX, audio, or training behavior change in `mtk_dp.c` uses this header for masks and offsets.

### Risks

Wrong masks or shifts can corrupt unrelated fields because most writes are read-modify-write through regmap. Audio divider encodings differ between MT8188 and MT8195. AUX and HPD status/clear bits are sequence-sensitive; incorrect definitions can cause stuck IRQs, AUX timeouts, or false cable state. The regmap maximum in `mtk_dp.c` must continue covering all offsets defined here.

### Test signals

Build coverage is the first signal. Runtime validation includes register readback during DP initialization, HPD IRQ clear behavior, successful AUX EDID/DPCD transfers, link training lane/swing changes, video timing output, audio packet generation, and suspend/resume power-state transitions.
