# Research: subset-b-006563 USB mixer quirks

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_quirks.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_quirks.h -->
# sources/distributed-fs/ceph-client/sound/usb/mixer_quirks.h

## Purpose
`mixer_quirks.h` declares the public quirk hooks exported by `mixer_quirks.c` to the rest of the ALSA USB-audio mixer implementation. It is the integration contract between generic mixer parsing and the product-specific quirk layer.

## Important APIs
- `snd_usb_mixer_apply_create_quirk(struct usb_mixer_interface *mixer)` creates additional device-specific ALSA controls during mixer construction.
- `snd_emuusb_set_samplerate(struct snd_usb_audio *chip, unsigned char samplerate_id)` updates the EMU USB sample-rate extension unit and notifies mixer clients.
- `snd_usb_mixer_rc_memory_change(struct usb_mixer_interface *mixer, int unitid)` reacts to UAC memory-change events, especially Sound Blaster remote-control packets and jack-related notifications.
- `snd_usb_mixer_fu_apply_quirk(struct usb_mixer_interface *mixer, struct usb_mixer_elem_info *cval, int unitid, struct snd_kcontrol *kctl)` post-processes parsed feature-unit controls.
- `snd_usb_mixer_resume_quirk(struct usb_mixer_interface *mixer)` runs product-specific mixer resume work not represented by individual control resume callbacks.

## Control flow and integration
The header is included by generic USB mixer code and by peer quirk modules such as the Presonus Studio driver. It assumes `struct usb_mixer_interface`, `struct snd_usb_audio`, `struct usb_mixer_elem_info`, and `struct snd_kcontrol` are visible through the including translation unit’s existing ALSA/USB headers.

## State, dependencies, and risks
The header owns no state. Its risk is ABI-style coupling within the kernel tree: changing any signature requires synchronized updates to all callers. Because it lacks forward declarations, include order matters; files using this header must include the appropriate mixer and ALSA definitions first.

## Test signals
Compile coverage of the USB-audio driver is the main signal. Link errors identify missing implementation symbols, while warnings about incomplete structs would indicate include-order breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_s1810c.c -->
# sources/distributed-fs/ceph-client/sound/usb/mixer_s1810c.c

## Purpose
`mixer_s1810c.c` implements ALSA mixer quirks for Presonus Studio 1810c, Studio 1824, and Studio 1824c USB interfaces. The driver is based on reverse-engineered USB traffic from Presonus Universal Control. It bypasses the hardware mixer by programming routing maps directly and exposes front-panel/device switches as ALSA controls.

## Important APIs, types, and functions
- `struct s1810c_ctl_packet` is the basic vendor OUT request payload. It carries selector, routing fields, a fixed tag, a length, and a value field.
- `struct s1810c_state_packet` is the larger state-sync packet exchanged through paired SET_STATE and GET_STATE vendor requests.
- `struct s1810_mixer_state` stores a sequence number plus `usb_mutex` and `data_mutex`.
- `snd_s1810c_send_ctl_packet()` sends one command packet using request `SC1810C_CMD_REQ`.
- `snd_sc1810c_get_status_field()` performs the two-step state sync: send an empty tagged state packet with the current sequence number, read a filled packet with the same sequence number, extract one field, then increment the sequence.
- `snd_s1810c_init_mixer_maps()` programs initial output faders and DAW-to-output routing for 1810c versus 1824/1824c.
- `snd_s1810c_switch_get()`, `snd_s1810c_switch_set()`, and `snd_s1810c_switch_init()` implement generic ALSA kcontrol plumbing for line source, mute, 48V phantom, headphone A/B routing, and 1824 mono controls.
- `snd_sc1810_init_mixer()` is the exported entry point called by `mixer_quirks.c`.

## Control flow
`snd_sc1810_init_mixer()` runs only for the first mixer interface by checking `chip->mixer_list`, initializes the routing map, allocates private state, installs cleanup through `mixer->private_free`, sets `seqnum` to 1, and creates common switch controls. It then adds device-specific controls: the 1810c gets headphone source route, while 1824/1824c get mono main out.

Switch `get` takes `data_mutex`, calls `snd_s1810c_get_switch_state()`, which takes `usb_mutex`, syncs the state packet, and extracts the field index encoded in the low byte of `private_value`. Switch `set` similarly reads current state first, compares with the requested value, stores the one-bit new value into bits 16+ of `private_value`, then sends a device selector command whose control ID is encoded in bits 8..15.

Routing initialization is write-heavy. The 1810c path initializes mixer input-to-output levels, output faders, S/PDIF routing, and basic DAW pair routing to main/line/S/PDIF outputs. The 1824/1824c path sets nine output pairs to unity and maps DAW 1..18 to line, S/PDIF, and ADAT output pairs while muting all other crossings.

## State and persistence behavior
The driver stores state in `mixer->private_data` as `struct s1810_mixer_state`. The sequence number is persistent for the lifetime of the mixer and is required for successful state reads. The current switch values are not fully cached; `get` and `set` read the device state before reporting or modifying values. However, `kcontrol->private_value` stores the field index, control ID, and latest one-bit set value used for command writes.

There are no explicit per-control resume callbacks here. Restoring routing and switch state after device reset depends on mixer reinitialization through USB-audio probing rather than a local resume replay path.

## Dependencies and integration points
The file depends on ALSA control APIs, Linux USB control messaging, USB Audio v2 constants, `usbaudio.h`, `mixer.h`, `helper.h`, `mixer_quirks.h`, and `mixer_s1810c.h`. It is selected by `snd_usb_mixer_apply_create_quirk()` for USB IDs `0x194f:010c`, `0x194f:0107`, and `0x194f:010d`.

The switch controls are standard ALSA mixer controls, but the actual hardware protocol is vendor-specific and device-wide rather than UAC feature-unit based.

## Risks and edge cases
- The protocol comments explicitly state that many fields are guesses from usbmon captures. Firmware changes can break routing or state sync.
- `snd_s1810c_switch_set()` returns `0` rather than the negative error when `snd_s1810c_set_switch_state()` fails, because it maps `(ret < 0) ? 0 : 1`; this can hide write failures from userspace.
- The low-byte field index, mid-byte control ID, and bit-16 value in `private_value` must stay consistent. Enumerated controls only expose two states even where the hardware field may contain wider values.
- The first-mixer guard assumes mixer-list ordering; changes in probe order could skip initialization or create duplicate controls.
- Routing initialization sends many sequential USB control messages and currently ignores individual failures inside loops because `snd_s1810c_init_mixer_maps()` does not check each send result.

## Test signals
- Probe each supported device and verify expected ALSA controls: line source, mute main out, 48V phantom, and either headphone route or mono main out.
- Use `amixer cget/cset` while observing front-panel behavior and USB traces to confirm field/control mappings.
- Confirm default routing by playing DAW channel pairs to main, line, S/PDIF, and ADAT outputs as applicable.
- Test unplug/replug and suspend/resume because there is no explicit resume replay path in this module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_s1810c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_s1810c.h -->
# sources/distributed-fs/ceph-client/sound/usb/mixer_s1810c.h

## Purpose
`mixer_s1810c.h` declares the Presonus Studio 1810c/1824 mixer initialization hook used by the generic USB mixer quirk dispatcher.

## Important API
- `snd_sc1810_init_mixer(struct usb_mixer_interface *mixer)` programs Presonus routing defaults, allocates mixer private state, and creates ALSA controls for device switches.

## Control flow and integration
`mixer_quirks.c` includes this header and calls the function for Presonus USB IDs. The header has no include guard in this copy, so it depends on being included once per translation unit or on the build not including it through multiple paths.

## State, dependencies, and risks
The header owns no state. Its declaration depends on `struct usb_mixer_interface` already being known to the including file. The main maintainability risk is the missing include guard compared with the other quirk headers; duplicate inclusion in one translation unit could produce repeated declarations, which are usually benign in C if identical but still less robust.

## Test signals
Compile/link coverage verifies the declaration matches the implementation. Product-level testing is covered by `mixer_s1810c.c` probe and ALSA control checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_s1810c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett.c -->
# sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett.c

## Purpose
`mixer_scarlett.c` implements first-generation Focusrite Scarlett and Focusrite Forte mixer support. It creates ALSA controls for routing, matrix mixer gains, output volumes/mutes, sample clock controls, sync status, and selected input hardware features. The code exists because UAC2 descriptors do not reliably expose the full Scarlett/Forte control surface, matching the behavior of vendor software that also uses model-specific knowledge.

## Important APIs, types, and functions
- `struct scarlett_mixer_elem_enum_info` describes static or dynamically generated enum domains, including start offsets and source-name offsets.
- `struct scarlett_mixer_control` and `struct scarlett_device_info` describe per-model control lists, matrix dimensions, input/output counts, routing support, and initial matrix mux values.
- Forte-specific helpers `forte_set_ctl_value()`, `forte_get_ctl_value()`, `forte_input_gain_*()`, `forte_ctl_enum_*()`, and `forte_ctl_switch_*()` implement controls through `UAC2_CS_MEM` writes to unit `0x3c`, with cached state because device reads may not be supported.
- Scarlett generic callbacks `scarlett_ctl_switch_*()`, `scarlett_ctl_*()`, `scarlett_ctl_enum_*()`, `scarlett_ctl_meter_get()`, and `scarlett_ctl_resume()` implement boolean mute switches, integer gain controls with TLV, static/dynamic enumerations, sync status, and cached resume replay.
- `add_new_ctl()` is the local control factory. It allocates `usb_mixer_elem_info`, fills UAC-like addressing fields, attaches enum metadata in `private_data`, creates an ALSA kcontrol, and registers it with the mixer.
- `add_output_ctls()` creates master pair mute/volume controls and optional left/right output source routing controls.
- `scarlett_controls_create_generic()` builds common master controls and per-model hardware/input/output controls.
- `snd_scarlett_controls_create()` and `snd_forte_controls_create()` are the exported entry points used by `mixer_quirks.c`.

## Control flow
Both exported create functions first require UAC2 (`mixer->protocol` nonzero) and dispatch on USB ID to choose a `scarlett_device_info` table. They call `scarlett_controls_create_generic()`, then create matrix route controls and matrix mix volume controls. Scarlett devices additionally create input capture route controls, sample clock source, sync status, and initialize the sample rate to 48000 Hz through a class CUR write to control `0x29`. Forte creates a smaller matrix and sync status, with Forte-specific input controls from the generic table.

Normal Scarlett `get` and `put` paths call `snd_usb_get_cur_mix_value()` and `snd_usb_set_cur_mix_value()` using fields stored in `usb_mixer_elem_info`: `head.id` becomes the high byte of `wIndex`, `control` contributes to `wValue`, and `idx_off` selects channel/node. Mute switch logic is inverted for user-facing semantics. Gain values are scaled by 256 and biased by `SND_SCARLETT_LEVEL_BIAS` so GUI mixers avoid negative values.

Dynamic route enumerations generate names such as PCM, Analog, S/PDIF, ADAT, Mix, or Off from the model’s offset table. The same enum callbacks are used for matrix mux, output source routing, and capture source routing.

## State and persistence behavior
Most Scarlett controls read current values from the device and rely on `usb_mixer_elem_info` caching performed by the lower mixer helpers for resume replay. `scarlett_ctl_resume()` replays cached per-channel values. Enum resume replays the cached first value. Forte controls explicitly cache writes in `elem->cached` and `elem->cache_val[0]` because `forte_get_ctl_value()` does not actually read hardware and defaults to zero when uncached.

The device info tables are static read-only configuration. `matrix_mux_init` arrays document initial routing expectations but this file does not visibly use them in the read sections; matrix controls are created for userspace to set routes.

## Dependencies and integration points
The file depends on ALSA control/TLV APIs, Linux USB APIs, USB Audio v2 request constants, and local helpers from `usbaudio.h`, `mixer.h`, `helper.h`, `power.h`, and `mixer_scarlett.h`. It integrates with `mixer_quirks.c` for Focusrite USB IDs `0x1235:8010`, `8012`, `8002`, `8004`, `8014`, and `800c`. Newer Scarlett/Clarett generations are intentionally handled by other modules (`mixer_scarlett2.c` or FCP), not by this file.

## Risks and edge cases
- The implementation is model-table driven. Incorrect `matrix_in`, `matrix_out`, offsets, or control codes create wrong ALSA controls or issue writes to the wrong vendor control.
- Forte reads are cache/default based, so after hardware-side changes or a missed write, ALSA may report stale/default values.
- `snd_scarlett_controls_create()` writes a fixed 48000 Hz sample rate during mixer creation, which can interact with runtime audio configuration expectations.
- Some `sprintf()` calls are used where most other paths use bounded formatting; current names are short, but future control names should stay within ALSA ID limits.
- Dynamic enum naming depends on offset ordering and one-based comparisons in `scarlett_generate_name()`. Off-by-one errors are easy when adding devices.
- `scarlett_ctl_meter_get()` uses `elem->channels` as transfer length even though the buffer is sized for `2 * MAX_CHANNELS`; this is fine for current one-byte sync use but worth checking if reused.

## Test signals
- Probe each supported first-generation Scarlett/Forte model and verify expected control counts and names with `amixer controls`.
- Exercise route enums, matrix volumes, master mute/volume, sample clock source, and sync status through `amixer cget/cset`.
- Suspend/resume after changing routes and gains to confirm cached values replay.
- For Forte, test write/readback expectations carefully because software readback is cache-based rather than hardware-derived.
- USB traces against Scarlett MixControl/Forte Control are useful for validating request numbers, `wValue`, `wIndex`, and payload shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett.h -->
# sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett.h

## Purpose
`mixer_scarlett.h` declares the first-generation Focusrite Scarlett and Forte mixer creation hooks used by the USB mixer quirk dispatcher.

## Important APIs
- `snd_scarlett_controls_create(struct usb_mixer_interface *mixer)` creates controls for supported first-generation Scarlett interfaces.
- `snd_forte_controls_create(struct usb_mixer_interface *mixer)` creates controls for the Focusrite Forte.

## Control flow and integration
`mixer_quirks.c` includes this header and calls the appropriate function from its USB ID switch. The header has an include guard and expects `struct usb_mixer_interface` to be declared by earlier includes in the translation unit.

## State, dependencies, and risks
The header owns no state and exposes only two function declarations. The primary risk is keeping the dispatcher’s product-ID table aligned with the implementation’s internal USB ID switch: a caller may route a USB ID here that the implementation rejects with `-EINVAL`.

## Test signals
Compile/link coverage verifies symbol consistency. Runtime probe tests should confirm `snd_usb_mixer_apply_create_quirk()` selects this legacy Scarlett/Forte path only for the IDs supported by `mixer_scarlett.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett.h -->
