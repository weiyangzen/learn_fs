# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_cx2072x.c

## Purpose
This Baytrail/Cherrytrail DPCM machine driver supports Conexant CX2072X codecs on Atom SST or SOF platforms. It describes headset, internal mic, speaker, SSP2 routing, and codec clock setup.

## Important APIs, Types, and Functions
DAPM widgets/routes connect `Headphone`, `Headset Mic`, `Int Mic`, and `Ext Spk` to CX2072X ports and SSP2. `byt_cht_cx2072x_init()` installs ACPI GPIO mapping for headset detection, disables idle bias, sets codec sysclk to `CX2072X_MCLK_EXTERNAL_PLL` at 19.2 MHz, creates a headset jack with button 0, calls `snd_soc_component_set_jack()`, and sets a BCLK ratio of 50. `byt_cht_cx2072x_fixup()` enforces 48 kHz stereo S24_LE and programs the CPU DAI to I2S, bit/provider frame/provider mode, two slots, 24-bit.

## Control Flow and Integration
The card has two FEs indexed by `MERR_DPCM_AUDIO` and `MERR_DPCM_DEEP_BUFFER`, plus an SSP2 BE to `cx2072x-hifi`. Probe locates the ACPI codec device using `mach->id`, rewrites the codec component name to the actual `i2c-<ACPI name>`, fixes platform names, chooses SOF or legacy card identity, optionally assigns `snd_soc_pm_ops`, and registers the card.

## State, Persistence, and Dependencies
Static state includes the headset jack and `codec_name` buffer. Hardware state includes CX2072X sysclk, BCLK ratio, jack binding, and SSP2 CPU DAI format. Dependencies include `sst-mfld-platform`, Atom DPCM indices, ACPI HID discovery, GPIO mapping, and the CX2072X codec driver.

## Risks and Test Signals
Risks include assuming one codec DAI match, failing probe if ACPI lookup misses `mach->id`, and global mutable DAI/link state after codec-name rewrite. Test signals include probe deferral or success based on ACPI codec presence, FE and deep-buffer PCM creation, 48 kHz-only stream startup, headset button events, and correct SSP2 I2S signal shape.
