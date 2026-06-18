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
