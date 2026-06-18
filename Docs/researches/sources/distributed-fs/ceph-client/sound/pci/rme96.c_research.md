# sources/distributed-fs/ceph-client/sound/pci/rme96.c Research

## Purpose

`rme96.c` is the ALSA PCI driver for the RME Digi96 family: Digi96, Digi96/8, Digi96/8 PRO, Digi96/8 PAD, and Digi96/8 PST. Unlike `rme32.c`, this hardware exposes separate playback and capture buffers, separate DMA pointers, separate start bits, and separate playback/capture IRQ acknowledgements. The driver therefore supports duplex operation through normal independent playback and capture paths while still coordinating synchronized ALSA trigger groups.

The file supports S/PDIF and, except on the base Digi96, ADAT PCM devices. It also supports model-specific analog input/output controls, DAC volume programming through a bit-banged SPI-like interface, clock/input selection, IEC958 status controls, loopback, monitor tracks, attenuation, proc diagnostics, and PM sleep buffer/register restoration.

## Important APIs, Types, and Functions

The main state object is `struct rme96`. It holds PCI/ALSA objects, spinlock, I/O mapping, cached write-control register `wcreg`, cached additional register `areg`, cached read register `rcreg`, default and active IEC958 bits, analog volume cache, revision, suspend buffers and saved pointers, open substream pointers, frame-size shifts, and configured period sizes.

Hardware capability macros identify feature variants: `RME96_HAS_ANALOG_IN`, `RME96_HAS_ANALOG_OUT`, `RME96_DAC_IS_1852`, `RME96_DAC_IS_1855`, `RME96_ISPLAYING`, and `RME96_ISRECORDING`. Register-bit definitions cover playback/capture start bits, sample width bits, ADAT mode, clocking, input selection, monitor selection, non-audio Dolby bit, word clock, analog mode, ADC/DAC power, and DAC serial data pins.

Important functions:

- `snd_rme96_playback_ptr()` and `snd_rme96_capture_ptr()` read independent hardware positions and convert bytes to frames using `playback_frlog` and `capture_frlog`.
- `snd_rme96_write_SPI()` bit-bangs `CDAT`, `CCLK`, and `CLATCH` in `areg` to program AD1852/AD1855 DACs.
- `snd_rme96_apply_dac_volume()` writes cached left/right volumes in the format required by the detected DAC.
- `snd_rme96_capture_getrate()` decodes analog, ADAT, and S/PDIF input rates from `areg`/`rcreg`.
- `snd_rme96_playback_getrate()` and `snd_rme96_playback_setrate()` implement internal or slave playback clock selection and double-speed rate bits.
- `snd_rme96_capture_analog_setrate()` configures analog input rates, including revision restrictions for 64/88.2 kHz.
- `snd_rme96_setclockmode()`, `snd_rme96_setinputtype()`, `snd_rme96_setattenuation()`, `snd_rme96_setmontracks()`, and related getters back ALSA controls.
- `snd_rme96_playback_hw_params()` and `snd_rme96_capture_hw_params()` bind runtime DMA to the playback or capture I/O buffer, validate clock/rate/channel compatibility, set sample width, enforce shared period size for synced duplex, program interrupt block size, and apply IEC958 stream bits.
- `snd_rme96_trigger()` is the low-level register operation helper for start/stop/reset/IRQ-clear combinations.
- `snd_rme96_playback_trigger()` and `snd_rme96_capture_trigger()` translate ALSA trigger commands into per-direction or synchronized both-direction operations.
- `rme96_suspend()` and `rme96_resume()` save and restore DMA pointers, copy both hardware buffers to vmalloc memory, disable/enable DAC, reset ADC/DAC, and restore analog volume.

PCM ops use direct I/O-memory copy and mmap callbacks: playback writes to `RME96_IO_PLAY_BUFFER`, capture reads from `RME96_IO_REC_BUFFER`, and ALSA mmap uses `snd_pcm_lib_mmap_iomem`.

## Control Flow

Probe starts in `snd_rme96_probe()` and `__snd_rme96_probe()`. The driver allocates a managed ALSA card, initializes `struct rme96`, and calls `snd_rme96_create()`. Creation enables PCI, claims regions, maps the `RME96_IO_SIZE` window, requests the IRQ, reads the revision, creates the S/PDIF PCM, optionally creates the ADAT PCM, stops both engines, initializes `wcreg` and `areg` defaults, resets ADC/DAC, enables DAC, resets playback and capture positions, initializes analog volume, creates controls, and registers proc diagnostics. Probe allocates suspend buffers when PM sleep is enabled, names the card based on PCI ID and revision, registers the ALSA card, and stores driver data.

Open paths enforce one playback and one capture substream at a time. S/PDIF playback clears ADAT mode and activates the IEC958 stream control. ADAT playback sets ADAT mode. Capture open rejects invalid source/channel combinations, such as ADAT capture while analog input is selected or S/PDIF capture when the locked input is ADAT. Playback open narrows rates to a locked external rate when in slave clock mode and not using analog input.

`hw_params` sets the runtime DMA view directly to the device buffer, configures rate and format, computes frame shifts, and forces playback/capture period bytes to match when the opposite direction is already configured. `snd_rme96_set_period_properties()` maps 2048- or 8192-byte periods into the interrupt select bit and enables interrupts. S/PDIF playback applies the per-stream AES bits to the control register.

Trigger handling supports ALSA sync groups. Each trigger callback marks all substreams in the group done, detects whether playback and capture belong to the same group, and then starts/stops/resumes either the requested direction or both directions with one low-level register update. IRQ handling checks both playback and capture IRQ bits, calls `snd_pcm_period_elapsed()` on the matching active substream, and acknowledges each IRQ independently.

## State and Persistence

`wcreg` and `areg` are the driver's cached hardware-control state. `wcreg` stores playback/capture start bits, format bits, ADAT mode, playback frequency, clock mode, input selection, monitor bits, IEC958 professional/emphasis/non-audio bits, and interrupt period selection. `areg` stores analog mode, analog sample frequency, word-clock select, DAC enable, ADC/DAC reset bits, and DAC serial programming pins.

The two hardware audio buffers are persistent only while powered. For PM sleep, the driver allocates `RME96_BUFFER_SIZE` vmalloc buffers per direction, saves the current playback/capture hardware pointers and buffer contents, disables the DAC, and on resume restores positions and buffer contents before resetting ADC/DAC and reapplying analog volume.

Substream pointers and period sizes are active-open state and are cleared on close. The analog output volume is cached in `vol[2]` and reapplied after DAC resets or double-speed transitions.

## Dependencies and Integration Points

This file integrates with PCI managed resources, shared IRQs, ALSA core/PCM/control/proc APIs, PM sleep ops, vmalloc suspend buffers, I/O-memory copy/mmap helpers, IEC958 AES status bits, and low-level `writel`/`readl` register access.

ALSA devices are `"Digi96 IEC958"` at PCM device 0 and `"Digi96 ADAT"` at PCM device 1 when the model supports ADAT. Controls include IEC958 default/stream/masks, `"Input Connector"`, `"Loopback Input"`, `"Sample Clock Source"`, and, on analog-output capable models, `"Monitor Tracks"`, `"Attenuation"`, and `"DAC Playback Volume"`.

## Risks and Edge Cases

The analog and revision-specific paths are dense. PAD/PST device IDs overlap and are distinguished by revision; XLR versus analog enumeration changes for PST revisions greater than 4. Wrong revision interpretation can expose invalid inputs or hide real ones.

`snd_rme96_capture_getrate()` appears to test `rme96->areg & RME96_AR_BITPOS_F2` instead of the `RME96_AR_FREQPAD_2` bit when deciding analog double-speed. Since `RME96_AR_BITPOS_F2` is a bit position constant, this is a suspicious area for rate decoding.

The IRQ handler assumes `playback_substream` exists when playback IRQ is set and `capture_substream` exists when capture IRQ is set. Close paths stop active engines before clearing pointers, but interrupt races remain important when modifying locking or teardown.

Rate and channel validation depends on live receiver status. If input lock changes after open/hw_params, ALSA constraints may not follow the hardware. Playback in slave mode uses capture rate unless analog input is selected; analog input forces different clock assumptions.

DAC programming is bit-banged under the same cached `areg` used for other analog/clock controls. Any concurrent `areg` updates must preserve serial bits and hardware timing. Double-speed playback changes reset the DAC and delay/reapply volume outside the main lock, so ordering with user volume changes matters.

Suspend/resume copies the entire I/O buffer while streams may conceptually exist. It restores buffer content and pointers but does not explicitly restart streams; ALSA PM sequencing must quiesce streams correctly. Failure to allocate either suspend buffer aborts probe when PM sleep is enabled.

## Test Signals

Validation should cover each PCI ID and revision-sensitive shortname, S/PDIF playback/capture, ADAT availability only on non-base models, analog input on PAD/PST, analog output controls on PRO/PAD/PST, IEC958 status bits including non-audio, direct mmap/copy operation, and `/proc/asound/card*/rme96` state reporting.

Runtime tests should exercise 2048- and 8192-byte periods, synced playback/capture trigger groups, independent start/stop/pause/resume in each direction, clock modes AutoSync/Internal/Word, S/PDIF rates through 96 kHz, ADAT 44.1/48 kHz, analog capture rates including revision-limited double-speed modes, DAC volume persistence after sample-rate changes, and suspend/resume buffer restoration. Stress tests should monitor for missed period interrupts, stale substream pointers in IRQ, and wrong channel/rate acceptance when input lock changes.
