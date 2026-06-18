# sources/distributed-fs/ceph-client/sound/soc/pxa/mmp-sspa.c

Purpose: implements the Marvell MMP SSPA CPU DAI and PCM component for serial audio playback/capture.

Important APIs/types/functions: private `struct sspa_priv` stores TX/RX bases, DMA data, clocks, running count, and cached SP/CTL values. DAI ops include `mmp_sspa_set_dai_fmt`, `mmp_sspa_hw_params`, `mmp_sspa_trigger`, clock setters, startup/shutdown, and probe. Component callbacks include custom `mmp_pcm_mmap`, `mmp_sspa_open`, and `mmp_sspa_close`.

Control flow: platform probe maps RX/TX registers, gets clocks, registers optional DMAEngine PCM for DT systems, registers component/DAI, enables runtime PM and audio clock. Open verifies hardware is idle, writes reset/flush configuration, clears reset, and writes initial CTL. hw_params maps sample formats to SSPA word/sample sizes, sets frame width/period, configures bitclk for DT, and writes TX or RX control. Trigger always enables RX for hardware reasons, enables TX only for playback, and disables RX when the shared running count reaches zero.

State and persistence: cached `sp` and `ctrl` fields persist desired port format across open/hw_params. `running_cnt` coordinates shared RX hardware. Runtime PM and clocks track device active state.

Dependencies and integration: depends on `mmp-sspa.h`, DMAEngine PCM, runtime PM, clock framework, ASoC DAI/component APIs, and optional DT compatible `marvell,mmp-sspa`.

Risks: `running_cnt` is not protected by a lock in trigger paths. DT mode returns `-ENOTSUPP` for legacy clock setter APIs and expects bitclk clock rate programming in hw_params. Custom mmap maps noncached DMA pages and must match buffer allocation semantics.

Test signals: DT and non-DT probe, playback/capture startup with shared RX enable, 8/16/24/32-bit formats, runtime PM balance, DMA mmap behavior, and stop sequences driving running count back to zero.
