# sources/distributed-fs/ceph-client/sound/soc/amd/raven/acp3x-i2s.c

## Purpose
This is the Raven ACP3x CPU DAI driver for I2S/TDM playback and capture. It configures DAI format, TDM slot format, sample resolution, I2S/BT instance selection, and stream start/stop registers.

## Important APIs, Types, And Functions
The DAI callbacks are `acp3x_i2s_set_fmt()`, `acp3x_i2s_set_tdm_slot()`, `acp3x_i2s_hwparams()`, and `acp3x_i2s_trigger()`, assembled into `acp3x_i2s_dai_ops`. The platform probe `acp3x_dai_probe()` maps a register resource and registers `acp3x_i2s_dai`.

## Control Flow
The PCI parent creates multiple `acp3x_i2s_playcap` devices for SP and BT TDM register windows. `set_fmt` selects I2S versus DSP_A/TDM mode. `set_tdm_slot` calculates the frame-format register value. `hw_params` obtains `struct acp3x_platform_info` from the card, selects playback or capture I2S instance, maps sample format to hardware sample length, optionally enables TDM and writes TX/RX format, then writes the sample length bits. Trigger start sets watermarks and ring-buffer size, enables the chosen TX/RX iterator/receiver register, and enables the matching IER; trigger stop clears enable bits and disables IER only when both playback and capture are inactive for that instance.

## State And Persistence Behavior
Driver state is `struct i2s_dev_data`, carrying TDM mode and format plus MMIO base. Stream-specific state in `struct i2s_stream_instance` is created by the DMA component and read here through `runtime->private_data`. The DAI driver does not allocate stream memory; it mutates fields such as `i2s_instance`, `xfer_resolution`, and `bytescount`.

## Dependencies And Integration Points
It depends on `acp3x.h` for register offsets, constants, read/write helpers, and `acp3x_platform_info`. It integrates tightly with `acp3x-pcm-dma.c`, which owns DMA buffer programming and substream registration, and with an ASoC card that sets card driver data to choose SP or BT instances.

## Risks And Edge Cases
The DAI assumes `runtime->private_data` was already installed by the DMA component. Capture supports only up to 48 kHz while playback supports up to 96 kHz. TDM register restore is handled in the DMA component resume path, so DAI and DMA state must stay synchronized. Unsupported formats and slot widths return `-EINVAL`.

## Test Signals
Exercise I2S and DSP_A formats, slot widths 8/16/24/32, SP and BT instances, playback/capture trigger transitions, and suspend/resume with TDM enabled. ALSA PCM tests should verify no IER remains enabled after both directions stop.
