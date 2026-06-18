# sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_codec.c

## Purpose

`ac97_codec.c` implements ALSA's universal Audio Codec '97 / MC'97 codec layer. It creates AC97 buses and codec instances for controller drivers, probes and names codecs, validates and caches register accesses, builds standard mixer and modem controls, applies codec-specific patches and board quirks, determines supported sample rates, handles suspend/resume and optional power saving, and exports helper APIs to PCI AC97 controller drivers.

## Important APIs, Types, and Functions

Exported APIs include `snd_ac97_write()`, `snd_ac97_read()`, `snd_ac97_write_cache()`, `snd_ac97_update()`, `snd_ac97_update_bits()`, `snd_ac97_get_short_name()`, `snd_ac97_bus()`, `snd_ac97_mixer()`, `snd_ac97_update_power()` when power-save is enabled, `snd_ac97_suspend()` / `snd_ac97_resume()` when PM is enabled, and `snd_ac97_tune_hardware()`.

Important internal structures are `struct ac97_codec_id` tables for vendor and exact codec matching, standard `snd_kcontrol_new` templates, AD18xx private PCM controls, S/PDIF controls, and `power_regs[]`. Codec-specific patch functions are included by textual inclusion of `ac97_patch.c`, and `ac97_id.h` supplies selected ID constants.

## Control Flow

Controller drivers first call `snd_ac97_bus()` with bus callbacks for register I/O. That allocates `struct snd_ac97_bus`, initializes bus lock and default 48 kHz clock, initializes procfs bus support, and registers an ALSA bus device.

`snd_ac97_mixer()` creates a codec from a template. It initializes private pointers, bus slot, mutexes, subsystem IDs, and optional delayed power work. It then uses controller reset/wait callbacks if present; otherwise it writes AC97 audio and modem reset registers and waits for accessible registers with `ac97_reset_wait()`. It reads vendor IDs, rejects invalid all-zero/all-ones IDs unless vendor detection is requested, tests audio and modem capabilities, reads audio caps and extended IDs, and waits for analog/modem readiness. It enables VRA/VRM and surround/center/LFE extended status bits, detects double-rate support, determines supported DAC/ADC/MIC/S/PDIF rates, runs controller `init`, applies codec name lookup and patch hooks, builds audio mixer controls and/or modem controls, updates power registers, initializes procfs codec support, and registers the codec as an ALSA device.

Register I/O helpers gate accesses through `snd_ac97_valid_reg()` for known buggy codecs, then call bus read/write callbacks. Cached writes and updates hold `reg_mutex`; paging helpers hold `page_mutex` for AC97 2.3 paged registers. Mixer construction probes register behavior with writes/reads to decide which controls exist and what volume resolution they support, then adds ALSA controls with TLV dB metadata.

Suspend calls codec patch suspend hooks if present, cancels power work, and powers the chip down. Resume resets or powers up the codec, waits for register access, runs bus init and patch resume hooks, or restores cached registers and S/PDIF state.

## State and Persistence

State is stored in `struct snd_ac97_bus` and `struct snd_ac97`: bus callbacks, clock, codec array, register cache `regs[]`, `reg_accessed` bitmap, mutexes, codec IDs/caps/ext IDs, rates, flags/scaps, build ops, S/PDIF status, subsystem IDs, private data, proc entries, device registration, and optional power-work state. Hardware register state is mirrored in the cache for suspend/resume and control reads. There is no disk persistence.

## Dependencies and Integration Points

The file depends on ALSA core/control/PCM/TLV APIs, Linux PCI and device model APIs, delayed work and mutexes, AC97 public headers, `ac97_id.h`, and `ac97_patch.c`. It integrates with many PCI controller drivers that select `SND_AC97_CODEC` and provide `snd_ac97_bus_ops`. Optional procfs functions come from `ac97_proc.o`, declared in `ac97_local.h`.

## Risks and Edge Cases

Hardware probing intentionally writes to mixer registers to detect capabilities and must restore cache carefully. `snd_ac97_read_cache()` has the `set_bit()` line commented out in the first-read path, so callers rely on later writes/updates for accessed tracking. Some reset failures only warn and proceed because many systems tolerate partial response. Codec-specific register filtering is critical; unsupported reads can hang some hardware. S/PDIF updates temporarily disable S/PDIF and must restore state. Power-down logic changes analog and EAPD bits without changing mixer cache for master/headphone mute, which is intentional for resume but easy to break. Quirk application renames/removes controls and can fail when expected controls were not built.

## Test Signals

Build with AC97 codec as module and built-in, with and without `CONFIG_SND_PROC_FS`, `CONFIG_PM`, and `CONFIG_SND_AC97_POWER_SAVE`. Runtime tests include controller-driven bus creation, codec probe for audio and modem codecs, register cache read/write/update, mixer control enumeration and TLV values, S/PDIF default/status updates, variable-rate detection, suspend/resume restoring cached controls, delayed power-save transitions, and board quirk application by subsystem IDs and override strings.
