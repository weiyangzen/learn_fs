# sources/distributed-fs/ceph-client/sound/hda/common/beep.c

## Purpose
This file implements the optional digital PC beep input interface for HDA codecs and beep-aware mixer switch callbacks. It lets HDA codecs expose an input-layer `EV_SND` device that translates `SND_BELL` and `SND_TONE` events into HDA `AC_VERB_SET_BEEP_CONTROL` writes.

## Important APIs, Types, And Functions
Exported functions are `snd_hda_enable_beep_device()`, `snd_hda_attach_beep_device()`, `snd_hda_detach_beep_device()`, `snd_hda_mixer_amp_switch_get_beep()`, and `snd_hda_mixer_amp_switch_put_beep()`. Internal helpers include `generate_tone()`, `snd_hda_generate_beep()`, `beep_linear_tone()`, `beep_standard_tone()`, `snd_hda_beep_event()`, `turn_on_beep()`, `turn_off_beep()`, `beep_dev_register()`, `beep_dev_disconnect()`, `beep_dev_free()`, and `ctl_has_mute()`. The file operates on `struct hda_beep`, `struct hda_codec`, ALSA `snd_kcontrol`, ALSA `snd_device`, and Linux `input_dev`.

## Control Flow
`snd_hda_attach_beep_device()` checks hints and `codec->beep_mode`, allocates `struct hda_beep`, enables linear scale on the beep NID, initializes work, allocates and configures an input device, and registers it as an ALSA device. Input events arrive at `snd_hda_beep_event()`, which converts bell/tone frequency to a hardware tone parameter with linear or standard math, then schedules `snd_hda_generate_beep()`. The worker calls `generate_tone()` when enabled. `generate_tone()` powers up the codec when starting, runs an optional power hook, writes the beep control unless the codec is in `beep_just_power_on` mode, and powers down when stopping.

`snd_hda_enable_beep_device()` toggles enabled state and calls `turn_on_beep()` or `turn_off_beep()`. Device disconnect unregisters or frees the input device and stops active beeps. The beep mixer get/put callbacks bridge mixer switch state to `beep->enabled` when the underlying amp has no mute capability or the beep is disabled, while still delegating to normal amp switch callbacks when a real mute amp exists.

## State And Persistence
`codec->beep` points to the allocated `struct hda_beep` until device free. Beep runtime state includes `enabled`, `playing`, `tone`, `linear_tone`, `keep_power_at_enable`, `registered`, `nid`, the input device pointer, work item, and physical path string. Tone generation is asynchronous through a workqueue. The input device registration persists as an ALSA-managed device and is removed during disconnect/free. Power references are balanced by `snd_hda_power_up()`, `snd_hda_power_down()`, and optional PM power hold when `keep_power_at_enable` is set.

## Dependencies And Integration Points
This file depends on Linux input, workqueue, ALSA core device management, and HDA codec helpers. It is built only when `CONFIG_SND_HDA_INPUT_BEEP` enables `beep.o` in the Makefile. Codec drivers such as SigmaTel and VIA add beep mixer controls and call or rely on `snd_hda_attach_beep_device()` through the common codec layer. Mixer macros such as `HDA_CODEC_MUTE_BEEP` use the exported get/put callbacks.

## Risks
Power management must stay balanced across asynchronous work, enable/disable, disconnect, and shutdown. Failing to cancel work before freeing the beep object could cause use-after-free. Tone conversion is hardware-specific: IDT/STAC linear tone mode is the inverse of standard HDA tone math, so selecting the wrong mode produces wrong frequencies. The mixer callbacks intentionally synthesize switch state when no hardware mute exists; changes can break user-visible "Beep Playback Switch" semantics. `codec->beep_just_power_on` suppresses writes and bypasses normal hint checks, so it must be understood by callers.

## Test Signals
Runtime signals include an `HDA Digital PCBeep` input device when enabled, absence of the device when disabled by hint or module mode, audible/observable tone writes for `SND_BELL` and `SND_TONE`, correct stopping on disable/disconnect, balanced codec power during beeps, and expected mixer switch behavior with and without hardware amp mute. Kernel sanitizers or debug builds should show no workqueue use-after-free during detach and shutdown.
