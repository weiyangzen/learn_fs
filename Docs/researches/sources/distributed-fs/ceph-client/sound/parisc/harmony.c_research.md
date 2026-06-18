# sources/distributed-fs/ceph-client/sound/parisc/harmony.c

## Purpose

`harmony.c` is an ALSA driver for the HP Harmony/Vivace audio chipset found in LASI/GSC PA-RISC workstations. It creates one ALSA card with one playback and one capture PCM stream, mixer controls for Harmony gain routing, GSC device binding, DMA buffers, interrupt-driven period advancement, and hardware register programming.

## Important APIs, Types, and Functions

Module parameters are `index` and `id`. Device matching is via `snd_harmony_devtable` and `parisc_driver`. Register access uses `harmony_read()`, `harmony_write()`, `harmony_wait_for_control()`, and `harmony_reset()`. Runtime control uses `harmony_disable_interrupts()`, `harmony_enable_interrupts()`, `harmony_mute()`, `harmony_unmute()`, and `harmony_set_control()`.

PCM callbacks include playback/capture `open`, `close`, `prepare`, `trigger`, and `pointer`, grouped in `snd_harmony_playback_ops` and `snd_harmony_capture_ops`. Card setup flows through `snd_harmony_create()`, `snd_harmony_pcm_init()`, `snd_harmony_mixer_init()`, and `snd_harmony_probe()`. Cleanup is through ALSA device free hooks and `snd_harmony_remove()`.

## Control Flow

`alsa_harmony_init()` registers a PA-RISC driver. Probe allocates an ALSA card, allocates and maps `struct snd_harmony`, requests the hardware IRQ, registers it as a low-level ALSA device, creates PCM, creates mixer controls, sets card names, registers the card, and stores it in `parisc_set_drvdata()`.

The IRQ handler disables Harmony interrupts under lock, reads `HARMONY_DSTATUS`, and responds to playback-next (`PN`) and record-next (`RN`) conditions. If playback is active, it advances `pbuf.buf` by one period, wraps within buffer size, writes the next playback DMA address to `HARMONY_PNXTADD`, increments stats, and calls `snd_pcm_period_elapsed()`. If inactive, it points playback at the silence buffer. Capture mirrors this behavior with `cbuf` and `HARMONY_RNXTADD`, otherwise routing data to the graveyard buffer. Interrupts are re-enabled at the end.

Prepare callbacks reject the opposite active direction, derive buffer and period byte counts from ALSA runtime, translate format/rate/channels to Harmony control bits, write control, and store runtime DMA address. Trigger start writes active DMA and opposite-direction sink/source buffers, unmutes, and enables interrupts. Trigger stop clears playing/capturing, mutes, points hardware to silence/graveyard, and disables interrupts. Pointer callbacks read current hardware addresses and convert byte deltas to ALSA frames.

Mixer controls manipulate the cached `h->st.gain` bitfield and write `HARMONY_GAINCTL`. They expose master playback, capture, monitor, input route, internal speaker, line-out, and headphone controls.

## State and Persistence

`struct snd_harmony` stores IRQ, physical and remapped base address, device pointers, cached hardware state (`gain`, `rate`, `format`, `stereo`, `playing`, `capturing`), DMA buffer descriptors, graveyard/silence DMA buffers, interrupt stats, ALSA card/PCM/substream pointers, and two spinlocks. Graveyard and silence buffers live for driver lifetime; playback/capture DMA is managed by ALSA per stream. There is no persistent storage beyond ALSA card state while loaded.

## Dependencies and Integration Points

The file depends on ALSA core, PCM, control, info, DMA helpers, Linux IRQ/io APIs, and PA-RISC `parisc_device` infrastructure. Hardware register layout and bit definitions come from `harmony.h`. It integrates with kbuild through `snd-harmony.o` and with Kconfig through `SND_HARMONY`.

## Risks and Edge Cases

The PCM hardware info advertises joint duplex, but prepare and trigger paths return `-EBUSY` if the opposite stream is active, so behavior is not actually simultaneous duplex. `harmony_wait_for_control()` busy-waits without timeout, so broken hardware can hang the CPU. Pointer callbacks return zero when the current address appears outside the buffer, which can hide hardware address anomalies. Cleanup calls `iounmap(h->iobase)` unconditionally; creation only reaches normal free paths after map success, but future edits should preserve that invariant. Graveyard/silence DMA allocation failure after the first allocation relies on device-free cleanup.

## Test Signals

Compile with `CONFIG_SND_HARMONY=m/y`, probe on matched PA-RISC IDs, IRQ request failure unwind, ALSA playback and capture open/prepare/start/stop, rejection of simultaneous playback/capture, supported rate constraint validation for the 14 explicit rates, mixer get/put for all gain controls, suspend-style stop/start cycles, and period elapsed accounting under interrupt load.
