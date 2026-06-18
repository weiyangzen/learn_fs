# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-ld11.c

## Purpose
SoC description and platform driver binding for UniPhier LD11/LD20 AIO audio. It describes available ports, virtual-to-real hardware mappings, PLL availability, DAI capabilities, and OF compatibles for the shared UniPhier AIO core.

## Important APIs, Types, and Functions
The main data are `uniphier_aio_ld11[]`, `uniphier_aio_pll_ld11[]`, `uniphier_aio_dai_ld11[]`, `uniphier_aio_ld11_spec`, and `uniphier_aio_ld20_spec`. The platform driver calls common `uniphier_aio_probe()` and `uniphier_aio_remove()`. DAI ops are referenced from the shared AIO implementation: `uniphier_aio_i2s_ld11_ops`, `uniphier_aio_spdif_ld11_ops`, and `uniphier_aio_spdif_ld11_ops2`.

## Control Flow, State, and Persistence
Probe is delegated entirely to the common core with `of_device_id.data` selecting either LD11 or LD20 chip spec. The spec arrays persist as read-only topology: HDMI, SIF, line/EVEA, S/PDIF input, speaker, HDMI PCM, line/headphone output, SRC outputs, S/PDIF PCM, and compressed S/PDIF. LD20 reuses LD11 topology but sets `addr_ext = 1`, a DMA access workaround flag consumed by shared code.

## Dependencies and Integration Points
Depends on the common UniPhier AIO core, ALSA DAI descriptors, OF platform matching, and the AIO register/routing helpers behind the `uniphier_aio_*_ops`. It integrates with EVEA for line/headphone analog paths and with the AIO DMA component for ring-buffer transport.

## Risks and Test Signals
Risks are mostly declarative: wrong map/hardware IDs route audio through the wrong AIO block, DAI stream names must match the spec names used by the common core, and LD20 behavior depends on the single `addr_ext` difference. Test signals include OF match for `socionext,uniphier-ld11-aio` and `socionext,uniphier-ld20-aio`, DAI registration count, playback/capture on each exposed stream, SRC operation on `aio-epcmout2/3`, and compressed S/PDIF open on `aio-hieccompout1`.
