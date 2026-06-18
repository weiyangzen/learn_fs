# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-reg.h

## Purpose

`mt8188-reg.h` is the MT8188 audio front-end hardware register map. It provides symbolic offsets and bitfield masks for the MT8188 AFE, ASYS, ADDA, DMIC, ETDM, PCM, SPDIF, DPTX, GASRC, connection matrix, secure mask, memory interface, interrupt, clock-gate, gain, monitor, and tuner blocks. It is a declarative hardware contract consumed by MT8188 platform and DAI drivers rather than executable code.

## Important APIs, Types, and Data

The file exports preprocessor macros only. Major offset families include top/control and IRQ registers, digital audio interface blocks, analog codec interface blocks, memory interface blocks, routing fabric registers, DMIC and gain blocks, and ASRC/GASRC blocks.

Examples include `AUDIO_TOP_CON0..6`, `ASYS_IRQ*`, `AFE_IRQ*`, `PCM_INTF_CON1/2`, `ETDM_IN*`, `ETDM_OUT*`, `AFE_DPTX_CON/MON`, SPDIF in/out registers, `AFE_ADDA_*`, `AFE_ADDA6_*`, MTKAIF config/monitor registers, DL/UL memif base/current/end/control registers, and large `AFE_CONN*` plus `AFE_SECURE_MASK_CONN*` ranges. `AFE_MAX_REGISTER` is defined as `AFE_CONN183_6`, marking the highest register offset known to this map.

Important bitfield macros cover clock gates (`AUDIO_TOP_CON*_PDN_*`), ASYS timing bits, PCM polarity/master/format bits, MTKAIF protocol/delay bits, DMIC mode/gain bits, ETDM channel/word/clock/format bits, DPTX channel and sample-width bits, ADDA voice/mute/gain/source controls, and GASRC calibration/timing fields.

## Control Flow

There is no runtime control flow in this header. Control flow is indirect: other MT8188 driver files include these macros and use them in regmap reads/writes, clock gating, DAI setup, memif setup, interrupt setup, and ALSA control handling. The register definitions are grouped by hardware block and by register field comments, which indicates expected call-site ownership.

## State and Persistence

The header itself holds no state. It describes volatile hardware state in MMIO registers. State persistence is therefore the hardware register contents across clock/reset domains and the regmap cache policy used by the including driver. Register writes affect live audio routing, DMA memory windows, interrupt enablement, clock gating, gain ramps, ASRC calibration, and secure routing masks.

## Dependencies and Integration Points

This file assumes Linux `BIT()` and `GENMASK()` macros are available from the including context. It integrates with MT8188 AFE common/platform drivers, DAI implementations for ADDA/DMIC/ETDM/PCM/DPTX/SPDIF/GASRC, and regmap configuration. The exact offsets are a hardware ABI between the kernel and MT8188 silicon. Device-tree resources must map the AFE register base that these offsets are relative to.

The header also ties into cross-file private data: machine and platform drivers use MTKAIF-related masks and offsets when calibrating or setting codec interface protocols; clock drivers use audio top PDN bits; PCM/memif code uses base/current/end definitions to program DMA windows.

## Risks

The main risk is silent hardware misprogramming. Offsets and masks are not type-checked, many names are mechanically similar, and several large connection and secure-mask ranges differ only by suffix. A single copied `_5` versus non-suffixed connection register can route the wrong audio path or bypass a security mask. Some definitions have spelling quirks such as `VOCIE` and `MULIT`; downstream code must use the exact macro names. Because `AFE_MAX_REGISTER` gates the declared map size, omissions above that address can block valid regmap access if hardware grows.

Another risk is semantic inversion in PDN/gate bits. Some `AUDIO_TOP_CON*` bits are power-down bits where setting disables a block, while other enable fields elsewhere use positive logic. Call sites must centralize on helpers where possible. Secure-mask registers need particular care because testing only normal audio may not expose mistakes in protected or HDMI/DP routes.

## Test Signals

Build testing catches missing macros and syntax but not offset correctness. Useful runtime signals include regmap read/write traces, successful probe without regmap range failures, playback/capture through every memif listed by the platform driver, ETDM/PCM/DPTX/SPDIF loopback where available, DMIC capture at all supported rates, gain ramp behavior, interrupt delivery and clearing for ASYS/AFE IRQs, ASRC/GASRC calibration status, suspend/resume register restoration, and negative testing of secure or disabled routes. Hardware bring-up should compare this header against the MT8188 datasheet or vendor register dump and audit all `AFE_CONN*` and `AFE_SECURE_MASK_CONN*` consumers.
