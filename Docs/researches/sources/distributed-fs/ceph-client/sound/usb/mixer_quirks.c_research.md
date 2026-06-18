# sources/distributed-fs/ceph-client/sound/usb/mixer_quirks.c

## Purpose
`mixer_quirks.c` is the ALSA USB-audio mixer quirk hub. It supplements or replaces generic USB Audio Class mixer parsing for devices whose hardware exposes useful controls through vendor requests, broken descriptors, class memory requests, HID/input side channels, or nonstandard feature-unit semantics. Its main exported entry point, `snd_usb_mixer_apply_create_quirk()`, dispatches on `mixer->chip->usb_id` and creates additional ALSA controls for many product families. It also exports resume, remote-control memory-change, sample-rate, and feature-unit post-processing hooks used by the generic USB mixer layer.

## Important APIs, types, and functions
- `struct std_mono_table`, `snd_create_std_mono_ctl_offset()`, `snd_create_std_mono_ctl()`, and `snd_create_std_mono_table()` provide a reusable path for creating standard mono UAC feature controls with optional TLV callbacks. This is used for devices such as M-Audio Fast Track Ultra, C400/C600, and Electrix Ebox-44.
- `add_single_ctl_with_resume()` allocates a `usb_mixer_elem_list`, creates an ALSA `snd_kcontrol`, attaches an optional resume callback, and registers the control with `snd_usb_mixer_add_list()`. Most vendor controls in this file use this helper because they are not normal parsed feature-unit controls.
- Sound Blaster remote support is implemented by `rc_configs`, `snd_usb_soundblaster_remote_init()`, `snd_usb_soundblaster_remote_complete()`, `snd_usb_sbrc_hwdep_read()`, `snd_usb_sbrc_hwdep_poll()`, and `snd_usb_mixer_rc_memory_change()`. It exposes remote key events through a hwdep device and uses class `UAC_GET_MEM` control URBs.
- Per-family create paths include `snd_audigy2nx_controls_create()`, `snd_emu0204_controls_create()`, `snd_dualsense_controls_create()` when `CONFIG_INPUT` is reachable, `snd_xonar_u1_controls_create()`, `snd_mbox1_controls_create()`, `snd_nativeinstruments_create_mixer()`, `snd_ftu_create_mixer()`, `snd_c400_create_mixer()`, `snd_microii_controls_create()`, `snd_soundblaster_e1_switch_create()`, `dell_dock_mixer_create()`, `hp_dock_mixer_create()`, `snd_rme_controls_create()`, `snd_bbfpro_controls_create()`, `snd_rme_digiface_controls_create()`, and `snd_djm_controls_create()`.
- External quirk modules are integrated through `snd_us16x08_controls_create()`, `snd_scarlett_controls_create()`, `snd_forte_controls_create()`, `snd_scarlett2_init()`, `snd_fcp_init()`, and `snd_sc1810_init_mixer()`.
- `snd_usb_mixer_fu_apply_quirk()` modifies generic feature-unit controls after parsing. It applies DragonFly dB TLV ranges, MV-SILICON linear-volume flags, min-mute behavior from `quirk_flags`, and Plantronics control-name normalization.
- `snd_usb_mixer_resume_quirk()` currently reinitializes Dell WD15 dock volumes on resume. Many individual controls also carry their own resume callback through `add_single_ctl_with_resume()`.

## Control flow
Initialization starts in the generic mixer path, which calls `snd_usb_mixer_apply_create_quirk(mixer)`. The function always first attempts Sound Blaster remote setup, then enters a large `switch` on USB VID:PID. Each matched case creates controls, initializes hardware state, or delegates to a focused module. Errors from a family-specific creator generally abort the quirk path for that mixer.

The control callbacks follow ALSA kcontrol conventions: `info` declares boolean, integer, IEC958, or enumerated semantics; `get` reads cached state or hardware; `put` validates the requested value, returns `0` for no change, writes vendor/class controls when changed, and returns `1` on a successful update. Many callbacks store current state in `kcontrol->private_value`; some parse device/group/value bitfields out of it.

Remote-control flow is asynchronous. `snd_usb_mixer_rc_memory_change()` submits a prebuilt control URB when the remote unit reports a memory change. `snd_usb_soundblaster_remote_complete()` decodes the returned packet, notifies mute controls for known mute codes, stores `mixer->rc_code`, and wakes readers waiting on `mixer->rc_waitq`.

Feature-unit quirk flow is post-creation. `snd_usb_mixer_fu_apply_quirk()` sees each parsed UAC feature-unit control and may adjust TLV, flags, min-mute state, or displayed control name based on USB ID, card name, and quirk flags.

## State and persistence behavior
Persistent in-kernel state is mostly per-control cached state in `kcontrol->private_value`, per-mixer remote fields (`rc_cfg`, `rc_urb`, setup packet, waitqueue, `rc_code`), and ALSA mixer element data allocated for each custom control. Resume handling replays cached values for controls with resume callbacks, so vendor switches and volumes survive runtime/system suspend as far as the driver can restore them.

Several controls are read-only volatile status views and deliberately do not persist state: RME clock/sync meters, dock jack detection, DualSense jack state, and some IEC958/status controls read hardware on each `get`. Some controls initialize the hardware to defaults at creation time, notably DJM controls, Dell dock volume init, Scarlett/Forte delegated paths, RME Babyface Pro initial private values, and M-Audio routing controls.

## Dependencies and integration points
This file depends on ALSA core/control/hwdep/info/TLV APIs, Linux USB control messaging, USB Audio Class request constants, optional input subsystem hooks, HDA verb definitions for Realtek dock codecs, and local USB-audio helpers from `usbaudio.h`, `mixer.h`, `helper.h`, `power.h`, and family-specific mixer headers. It is tightly coupled to `struct usb_mixer_interface`, `struct snd_usb_audio`, `struct usb_mixer_elem_info`, `snd_usb_ctl_msg()`, `snd_usb_get_cur_mix_value()`, `snd_usb_set_cur_mix_value()`, `snd_usb_mixer_add_control()`, and `snd_usb_mixer_add_list()`.

The dispatcher is also the integration table for product IDs. Adding a new product family usually means adding a helper or external module and one or more `USB_ID()` cases. The feature-unit hook integrates with generic parsing rather than product-specific creation.

## Device-family behavior highlights
- Creative/Sound Blaster: LED controls, input source switches, hwdep remote events, proc jack reads, and HID `SET_REPORT` writes for Sound Blaster E1.
- Sony DualSense: card-level read-only jack controls mirror switch events from the matching HID input device; path matching prevents cross-talk when multiple identical controllers are attached.
- Digidesign Mbox 1: clock source and input source enumerations issue class endpoint/interface requests; the clock path has a FIXME hardcoded 48000 Hz internal rate.
- Native Instruments: boolean direct-through/phono controls are vendor device requests, initialized by reading the current vendor value.
- M-Audio FTU/C400/C600 and Ebox-44: large sets of synthetic standard mono controls are created because descriptors are incomplete or wrong; several controls rely on volume quirks elsewhere in the mixer code.
- Audio Advantage Micro II: IEC958 default/mask/switch controls map AES bits onto vendor registers and derive sample-rate status from endpoint sample-rate queries.
- Dell/HP docks: jack detection is implemented through vendor requests to Realtek/HP-specific registers rather than UAC jack descriptors.
- RME ADI/Babyface/Digiface: read-only clock/sync status and writable routing/control registers are exposed through vendor status/control requests; Babyface Pro builds a large routing matrix using encoded 18-bit linear volume values.
- Pioneer DJ/AlphaTheta DJM: capture/playback source and level options are model tables; `snd_djm_controls_update()` writes defaults on creation and replays them on resume.

## Risks and edge cases
- Most request payloads, indices, and bit encodings are reverse-engineered constants. Incorrect values can silently misroute audio, mute channels, or fail only on specific firmware revisions.
- `kcontrol->private_value` is used as a compact state store and bitfield across many unrelated families; changes must preserve each family’s layout and word-size assumptions.
- Some `put` paths update cached state before the USB write succeeds, while others update after success. This can cause resume replay to use a value that hardware rejected.
- Many paths assume fixed interfaces, endpoints, unit IDs, and channel counts. For example Micro II assumes interface 1 altsetting 1, and Mbox clock source uses a hardcoded 48000 Hz.
- Optional `CONFIG_INPUT` means DualSense jack controls disappear from builds without reachable input support.
- Vendor control messages run under PM/shutdown locks in most paths, but not every helper has identical locking style. New code should follow the local `CLASS(snd_usb_lock, pm)` or `snd_usb_lock_shutdown()` pattern used by similar controls.
- Product-ID dispatch is large and easy to regress when adding overlapping Focusrite generations, RME variants, or Pioneer/AlphaTheta models.

## Test signals
- Build coverage should include both `CONFIG_INPUT=y/m` and disabled input to catch DualSense conditional compilation.
- Runtime validation is best done with `amixer controls`, `amixer cget/cset`, suspend/resume, and unplug/replug on the target hardware.
- USB trace comparison against known-good vendor software is useful for reverse-engineered paths such as DJM, Babyface Pro, Presonus, Scarlett, and Forte.
- For status-only controls, repeated `amixer cget` while changing external clock/jack state should reflect hardware changes without requiring driver reload.
- Regression checks should verify no duplicate ALSA control names, correct TLV exposure for DragonFly/MV-SILICON/min-mute cases, and successful no-op returns when setting controls to their current value.
