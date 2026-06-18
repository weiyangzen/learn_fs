# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_wp.c

## Purpose
`hdmi_wp.c` is the common HDMI wrapper programming layer. It maps wrapper registers, manages IRQ status/enables, controls PHY/PLL power commands, starts/stops wrapper video, writes wrapper timing/format/interface fields, configures audio DMA/FIFO format, exposes the audio DMA address, and dumps wrapper registers.

## Important APIs, types, and functions
Key functions are `hdmi_wp_init`, `hdmi_wp_dump`, IRQ helpers, `hdmi_wp_set_phy_pwr`, `hdmi_wp_set_pll_pwr`, `hdmi_wp_video_start`, `hdmi_wp_video_stop`, `hdmi_wp_init_vid_fmt_timings`, `hdmi_wp_video_config_*`, `hdmi_wp_audio_config_format`, `hdmi_wp_audio_config_dma`, `hdmi_wp_audio_enable`, `hdmi_wp_audio_core_req_enable`, and `hdmi_wp_get_audio_dma_addr`.

## Control Flow
Init obtains the named `"wp"` memory resource, saves its physical base, and maps it. Power helpers write command fields and poll status fields using `hdmi_wait_for_bit_change`. Video setup initializes wrapper-local timing from `struct hdmi_config`, writes size and sync porch registers, writes packing/polarity/master mode, and start sets the enable bit. Stop clears the enable bit and waits up to roughly one second for frame-done. Audio config writes format fields, SoC-specific channel fields, DMA block/transfer sizes, DMA mode, and FIFO threshold; audio enable toggles wrapper control bits.

## State and Persistence
Software state is `wp->base` and `wp->phys_base`. Register state persists in wrapper video, timing, power, IRQ, audio, and sysconfig registers until reset or reconfiguration. Callers cache idle mode separately before audio streaming changes it.

## Dependencies and Integration Points
The wrapper layer is used by HDMI4/5 core, PLL, display, and audio code. It depends on platform resources, `hdmi.h` register definitions/macros, DSS version detection, and seq_file debug output.

## Risks
PHY/PLL status polling can timeout if hardware is wedged. `hdmi_wp_video_stop` logs but does not return failure when frame-done is missing. Audio channel format fields are conditional on older OMAP4 versions, so SoC detection must be correct. Register writes assume runtime PM has already made the wrapper accessible.

## Test Signals
Test wrapper mapping, PHY/PLL power transitions, video start/stop with frame-done, timing register values for progressive/interlaced modes, audio DMA address correctness, audio FIFO threshold programming, and IRQ status clear/enable behavior.
