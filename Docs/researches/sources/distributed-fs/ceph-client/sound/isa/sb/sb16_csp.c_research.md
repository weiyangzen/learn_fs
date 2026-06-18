# sources/distributed-fs/ceph-client/sound/isa/sb/sb16_csp.c

## Purpose
This file implements ALSA hwdep support for the SB16 Creative Signal Processor, also known as ASP/CSP. It detects the CSP, creates a hwdep device, loads and unloads CSP microcode, autoloads kernel firmware for compressed PCM formats, starts/stops/pauses/restarts the processor, exposes QSound mixer controls, and publishes a read-only proc status entry.

## Important APIs, Types, and Functions
`snd_sb_csp_new()` is the exported constructor. It calls `csp_detect()`, creates `SB16-CSP` hwdep, allocates `struct snd_sb_csp`, fills function pointers in `p->ops`, initializes `access_mutex`, and creates the proc entry. The hwdep operations are `snd_sb_csp_open()`, `snd_sb_csp_ioctl()`, and `snd_sb_csp_release()`. Ioctls support `SNDRV_SB_CSP_IOCTL_INFO`, `LOAD_CODE`, `UNLOAD_CODE`, `START`, `STOP`, `PAUSE`, and `RESTART`.

Microcode parsing centers on `snd_sb_csp_riff_load()`, which reads a user-supplied RIFF/CSP container, finds a requested function, loads `init` and `main` blocks through `snd_sb_csp_load_user()`, and fills codec capability fields. `snd_sb_csp_autoload()` requests built-in firmware names for mu-law, A-law, and IMA ADPCM. Hardware helpers include `command_seq()`, `set_codec_parameter()`, `set_register()`, `read_register()`, `set_mode_register()`, and `get_version()`. QSound controls are built and removed by `snd_sb_qsound_build()` and `snd_sb_qsound_destroy()`.

## Control Flow
Detection writes and reads CSP register 0x83 under the SB register lock, checks version range 0x10..0x1f, and resets the DSP. User-space opens the hwdep exclusively through `snd_sb_csp_use()`, which is guarded by `access_mutex` and rejects concurrent users. `LOAD_CODE` refuses to run while the CSP is active, validates RIFF headers and chunk bounds, loads initialization chunks first, then the required main chunk, maps VOC codec IDs to ALSA format capability bits, decouples CSP from IRQ/DMA lines, and marks the code loaded. `UNLOAD_CODE` clears capabilities and QSound controls when not running.

The PCM engine in `sb16_main.c` calls the `ops` callbacks to autoload and start codecs during PCM prepare. `snd_sb_csp_start()` validates loaded state and requested width/channels, mutes PCM mixer volume during the hardware transition, sets STOP/RUN mode, programs sample type and start command, records run state, and enables QSound if applicable. Stop disables QSound, sends STOP, restores volume, and clears running/paused bits.

## State and Persistence
Runtime state is in `struct snd_sb_csp`: `used`, `running` bit flags, `mode`, accepted format/channel/width/rate masks, run width/channel, loaded codec name/function, firmware cache pointers, QSound controls, QSound positions, and locks. Firmware blobs requested by `request_firmware()` are cached in `p->csp_programs` until hwdep free. No state is persisted beyond the kernel object lifetime.

## Dependencies and Integration Points
The file depends on ALSA hwdep, control, proc info, SB16 CSP UAPI definitions, SB mixer/DSP helpers from the Sound Blaster core, and Linux firmware loading. It exports `snd_sb_csp_new()` for `sb16.c` and is used at runtime by `sb16_main.c` through the CSP ops table.

## Risks and Edge Cases
RIFF parsing operates on user pointers and must preserve length checks; malformed lengths or unsupported VOC types return errors. `snd_sb_csp_unuse()` decrements `used` without checking underflow, so caller pairing matters. Some helper calls ignore intermediate command failures, reflecting historical hardware assumptions. QSound control removal calls `snd_ctl_remove()` on possibly NULL members after partial build failure, relying on ALSA tolerance. Firmware absence disables autoloaded compressed formats.

## Test Signals
Look for `cspD*` proc entries, `SB16-CSP` hwdep, successful `LOAD_CODE`/`INFO`/`START`/`STOP` ioctl sequences, autoloaded mu-law/A-law/IMA playback and capture through normal PCM open/prepare, QSound controls appearing only for QSound firmware, and clean unload while no PCM stream is running.
