# subset-b-006564 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett2.c -->
# sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett2.c

## Purpose

`mixer_scarlett2.c` implements the ALSA USB mixer extension for Focusrite Scarlett 2nd/3rd/4th generation, Clarett USB/Clarett+, and Vocaster devices. It binds supported USB product IDs to a proprietary Focusrite control protocol, exposes model-specific mixer controls through ALSA kcontrols, handles asynchronous device notifications, supports persistent configuration saves, and provides an ALSA hwdep path for flash segment reads/writes used by firmware/configuration tooling. It can also defer to the newer FCP driver via `device_setup` flags.

The file is intentionally table-driven. `scarlett2_device_info` describes each supported model's capabilities, port counts, mux layout, meter order, direct-monitor support, DSP features, flash/device-map availability, S/PDIF modes, and line-output naming/remapping. `scarlett2_config_set` describes each protocol family's configuration offsets, sizes, activation commands, notification masks, optional parameter-buffer address, input gain TLV scale, and autogain status strings.

## Important APIs, Types, and Constants

- `int snd_scarlett2_init(struct usb_mixer_interface *mixer)` is the exported entry point used by the USB audio mixer layer. It checks UAC2 protocol, honors `SCARLETT2_USE_FCP_DRIVER` and `SCARLETT2_DISABLE`, looks up the USB product ID, creates controls, initializes hwdep, and optionally exposes a device map proc file.
- `struct scarlett2_data` is the central runtime state. It stores the mixer pointer, USB/data mutexes, command completion, delayed NVRAM-save work, product/config pointers, Focusrite Control USB interface endpoint metadata, derived I/O counts, firmware/flash segment info, notification dirty flags, cached control values, kcontrol pointers, mux state, matrix mix gains, monitor mix gains, and hwdep flash-write state.
- `struct scarlett2_device_info` defines model capabilities and routing shape. Key fields include `config_set`, `min_firmware_version`, `has_devmap`, `has_speaker_switching`, `has_talkback`, input feature counts, `direct_monitor`, `dsp_count`, Bluetooth/SPDIF flags, line-output remap tables, `port_count`, `mux_assignment`, and `meter_map`.
- `struct scarlett2_config_set` maps protocol-family configuration items to `struct scarlett2_config { offset, size, activate, pbuf, mute }`. `pbuf` routes writes through a model-specific parameter buffer; `mute` marks Gen 4 controls where transient mute/switching encodings must be decoded.
- `struct scarlett2_notification { u32 mask; void (*func)(...) }` maps interrupt notification bits to refresh/notify handlers. Separate arrays exist for Gen 2/3 mixer devices, Gen 3 Solo/2i2, Vocaster, and each Gen 4 family.
- `struct scarlett2_usb_packet` is the proprietary request/response wrapper with `cmd`, `size`, `seq`, `error`, `pad`, and flexible `data[]`.
- USB command constants include `SCARLETT2_USB_GET_DATA`, `SCARLETT2_USB_SET_DATA`, `SCARLETT2_USB_DATA_CMD`, `SCARLETT2_USB_GET_MIX`, `SCARLETT2_USB_SET_MIX`, `SCARLETT2_USB_GET_MUX`, `SCARLETT2_USB_SET_MUX`, meter/sync commands, flash segment commands, reboot, and device-map commands.
- Flash constants include 4096-byte flash blocks, max 1024-byte protocol transfers, settings/firmware segment names, segment IDs from `uapi/sound/scarlett2.h`, and an internal flash write state enum: idle, selected, erasing, write.

## Product and Configuration Tables

The static device tables cover:

- Scarlett Gen 2: 6i6, 18i8, 18i20.
- Scarlett Gen 3: Solo, 2i2, 4i4, 8i6, 18i8, 18i20.
- Vocaster One/Two.
- Scarlett Gen 4: Solo, 2i2, 4i4.
- Clarett USB/Clarett+: 2Pre, 4Pre, 8Pre.

Each `scarlett2_device_info` combines feature flags with port topology. The `port_count` matrix counts input and output ports by type (`None`, analogue, S/PDIF, ADAT, mix, PCM). `mux_assignment` defines how device mux messages are ordered for each sample-rate band, and `meter_map` translates the protocol's meter order to user-facing mux/output order. Some devices define special S/PDIF mode text/value tables and line-output remaps, such as 18i8 Gen 3 internal line 3/4 mapping to analogue 7/8.

The `scarlett2_devices` table is the USB product dispatch list. `get_scarlett2_device_entry()` searches this table using `mixer->chip->usb_id`; missing entries log an error but do not hard-fail the generic USB audio driver.

## USB Control Protocol

`scarlett2_usb()` is the core synchronous protocol primitive:

- Allocates request and response packets sized with `struct_size()`.
- Serializes access under `private->usb_mutex`.
- Fills a monotonically increasing sequence in `scarlett2_fill_request_header()`.
- Sends the request using class-specific interface control OUT transfer `SCARLETT2_USB_CMD_REQ`.
- Retries `-EPROTO` request send failures up to five times with exponential backoff.
- Waits up to one second for an ACK notification via `private->cmd_done`.
- Reads the matching response with class-specific interface control IN transfer `SCARLETT2_USB_CMD_RESP`.
- Validates command, sequence, size, error, and pad fields, with a special reboot tolerance for `-ESHUTDOWN`/`-EPROTO`.

Helpers build on this primitive:

- `scarlett2_usb_get()` reads arbitrary data-space offsets using `SCARLETT2_USB_GET_DATA`.
- `scarlett2_usb_get_config()` interprets `scarlett2_config_set` entries, including 8/16/32-bit endian conversion and bit-sized unpacking.
- `scarlett2_usb_set_data()` and `scarlett2_usb_set_data_buf()` write scalar or vector values to device data space.
- `scarlett2_usb_activate_config()` sends `SCARLETT2_USB_DATA_CMD` with the config item's activation command.
- `scarlett2_usb_set_config()` writes one config value. Parameter-buffer writes program `param_buf_addr + 1` with the index and `param_buf_addr` with the value before activation. Direct writes cancel pending NVRAM save, read/modify/write bit fields when needed, activate the change, and schedule delayed NVRAM persistence unless the activation itself is the save command or the family uses a parameter buffer.
- `scarlett2_usb_set_config_buf()` writes multi-value configs and activates them; bit-sized writes are rejected.

## Mixer, Mux, and Meter Flow

The matrix mixer uses a fixed dB-to-protocol lookup table, `scarlett2_mixer_values`, mapping -80 dB to +12 dB in 0.5 dB steps to 16-bit gain coefficients. `scarlett2_mixer_value_to_db()` reverses that mapping for values read from the device.

Mixer flow:

1. `scarlett2_update_mix()` loops over `num_mix_out`.
2. `scarlett2_usb_get_mix()` reads one mix output's input gains via `SCARLETT2_USB_GET_MIX`.
3. ALSA controls created by `scarlett2_add_mixer_ctls()` expose every `Mix <letter> Input <n> Playback Volume`.
4. `scarlett2_mixer_ctl_put()` updates the cached scalar and writes the whole affected mix row with `SCARLETT2_USB_SET_MIX`.

Mux flow:

1. `scarlett2_usb_get_mux()` reads protocol mux assignments and converts packed hardware IDs to source/destination indexes with `scarlett2_mux_id_to_num()`.
2. `scarlett2_usb_set_mux()` regenerates all mux tables across the three sample-rate bands from `info->mux_assignment` and the cached `private->mux[]`.
3. `scarlett2_update_meter_level_map()` recomputes meter remapping after every mux refresh/write, using `meter_map`, line-output unmapping, and duplicate-source detection.
4. `scarlett2_add_mux_enums()` creates one source-selection enum for each mux destination, naming ports from `scarlett2_ports`.

Meter flow:

- `scarlett2_add_meter_ctl()` exposes one volatile PCM-interface `Level Meter` control with `num_mux_dsts` channels for devices with a mixer.
- `scarlett2_meter_ctl_get()` fetches protocol meter levels, translates through `meter_level_map`, emits zero for "Off", and reuses prior source meter readings for duplicate source assignments.

## ALSA Control Families

Controls are added through `scarlett2_add_new_ctl()`, which creates a `USB_MIXER_BESPOKEN` `usb_mixer_elem_info`, names the kcontrol, attaches `snd_usb_mixer_elem_free`, and registers it with `snd_usb_mixer_add_control()`.

Major control groups:

- Firmware metadata: read-only card controls for `Firmware Version` and `Minimum Firmware Version`.
- Sync: read-only enum `Sync Status` for mixer-capable devices.
- Output volumes: read-only hardware master/headphone volume, per-line software volume and mute, plus per-line software/hardware volume-control enum where supported. Volume uses `SCARLETT2_VOLUME_BIAS` to avoid negative ALSA values while exporting TLV dB ranges.
- Dim/mute: `Mute Playback Switch` and `Dim Playback Switch` mirror physical 18i20-style controls and propagate hardware mute changes to line-out mute controls when outputs are hardware-controlled.
- Speaker switching: enables/disables main/alternate speaker switching, forces the first four line outputs into hardware volume mode, toggles SW/HW control writability, and invalidates routing after monitor-other notifications.
- Talkback: exposes talkback mode and a bitmap of talkback destinations over mixer outputs.
- Input level/pad/air/DSP/mute/phantom/gain/safe/autogain/link/select: model-dependent capture controls derived from `scarlett2_device_info` counts and config availability.
- Vocaster DSP: compressor parameter controls and biquad filter enable/coefficient controls. Compressor values are 32-bit fixed-point on device and scaled to user-facing integer ranges. PEQ coefficients handle per-channel padding by copying only active slots out of the total slot block.
- Direct monitor: simple switch for mono-only devices or Off/Mono/Stereo enum for 2i2-like devices, plus optional monitor mix gain controls on Gen 4-style direct monitor mixers.
- MSD and standalone: boolean controls for mass-storage mode and standalone mode when config items exist. MSD is hidden when already off unless `device_setup` includes `SCARLETT2_MSD_ENABLE`.
- Power status: read-only card enum derived from external-power and low-power config bits.
- Bluetooth volume: Vocaster Two-style bounded integer volume.
- S/PDIF mode: model-specific enum converting user-facing text index to protocol value tables.

Most `get`/`put` functions use `private->data_mutex` and reject access with `-EBUSY` when `hwdep_in_use` is set. Controls that are invalid while autogain is running use `scarlett2_check_put_during_autogain()` and dynamic kcontrol write-bit updates. Autogain is also disabled while a related phantom power group is switching.

## Notifications and Lazy Refresh

`scarlett2_init_notify()` creates an interrupt URB on the vendor-specific Focusrite Control interface. `scarlett2_notify()` decodes 8-byte notification payloads, masks non-ACK notifications during initialization, dispatches matching bits through the active `scarlett2_config_set` notification table, warns on unhandled bits, and resubmits the URB unless it is shutting down.

Notification handlers do not generally fetch new values immediately. Instead, they:

- Set an `*_updated` dirty flag in `struct scarlett2_data`.
- Notify affected ALSA controls via `snd_ctl_notify()` with value and sometimes info masks.
- Trigger access-mode notifications for controls whose writability depends on autogain or phantom-switch state.
- Invalidate mux/mix controls after route-affecting changes such as direct monitor, PCM input switching, or speaker switching.

The next control `get` or guarded `info`/`put` path performs a lazy USB refresh via the relevant `scarlett2_update_*()` function.

## Initialization and Integration Points

Initialization in `snd_scarlett2_controls_create()` proceeds in strict order:

1. `scarlett2_init_private()` allocates state, initializes mutexes/delayed work, assigns callbacks to `mixer->private_free` and `mixer->private_suspend`, stores the product/config pointers, derives I/O counts, and finds the vendor-specific Focusrite Control interface.
2. `scarlett2_usb_init()` performs the proprietary init sequence: an initial control read, notification URB submission, ACK-only phase, two init commands, and firmware version extraction.
3. `scarlett2_get_flash_segment_nums()` discovers flash segment numbers and block counts for settings and firmware upgrade segments.
4. Firmware version controls are added.
5. `scarlett2_read_configs()` reads initial config caches, returning early if firmware is too old or MSD mode is enabled.
6. MSD control is added, then all feature controls are created if firmware/MSD gates allow.
7. Autogain/phantom-dependent access bits are initialized.
8. `private->running` becomes `2`, enabling full notification handling.

External dependencies include Linux USB APIs, ALSA control/hwdep/proc APIs, `snd_usb_ctl_msg()`, USB audio mixer registration helpers, `uapi/sound/scarlett2.h` ioctl/segment definitions, and `snd_fcp_init()` from `fcp.h`.

## State and Persistence Behavior

Runtime state is mostly cached in `struct scarlett2_data` and synchronized with `data_mutex`. Hardware state changes from external controls or device buttons are represented by dirty flags and lazily refreshed. USB command sequencing is protected by `usb_mutex` and completed by ACK notifications.

Persistent configuration differs by protocol family:

- Direct config writes on older devices schedule a delayed `SCARLETT2_USB_CONFIG_SAVE` two seconds after activation, using `private->work`.
- Newer parameter-buffer families do not schedule a separate save; writes are activated through the parameter-buffer path.
- `scarlett2_private_suspend()` flushes a pending delayed save by calling `scarlett2_config_save()` if work was canceled.
- `scarlett2_private_free()` cancels delayed work and frees private state.

Flash/hwdep state is explicit. Opening the hwdep resets flash write state to idle after any pending erase completes. Selecting a segment moves to selected; erasing locks ALSA controls through `hwdep_in_use` and moves to erasing; progress completion moves to write; write is allowed only for the firmware segment. Release resets selected/write states to idle but leaves erasing for the next open to resolve.

## Firmware, Flash, and Device Map Interfaces

The hwdep device named `Focusrite Control` is exclusive and exposes:

- `SCARLETT2_IOCTL_PVERSION` for hwdep ABI version.
- `SCARLETT2_IOCTL_REBOOT`.
- `SCARLETT2_IOCTL_SELECT_FLASH_SEGMENT`.
- `SCARLETT2_IOCTL_ERASE_FLASH_SEGMENT`.
- `SCARLETT2_IOCTL_GET_ERASE_PROGRESS`.
- `read()` for selected flash segment reads, limited to 1024-byte protocol operations and bounded by segment size.
- `write()` for firmware segment writes after erase, limited by protocol max payload and segment bounds.

For Gen 4/Vocaster devices with `has_devmap`, `scarlett2_devmap_init()` creates `/proc/asound/cardX/device-map.json.zz.b64`. Reads use `SCARLETT2_USB_GET_DEVMAP` on 1024-byte block boundaries and copy requested slices to userspace.

## Risks and Edge Cases

- The driver is reverse-engineered and heavily model-table dependent. Incorrect offsets, activation commands, mux assignments, or meter maps can misroute audio, hide controls, corrupt device state, or expose misleading meter data.
- `scarlett2_usb()` relies on interrupt ACK delivery. Lost notifications or a stuck URB cause synchronous commands to time out.
- Control callbacks frequently trust derived counts to fit static arrays. The tables must remain consistent with `SCARLETT2_*_MAX` constants.
- Many controls update cached state before USB writes. On failed writes, cache and hardware can temporarily diverge until a notification or manual refresh path corrects it.
- Flash operations intentionally block ALSA controls through `hwdep_in_use`, but they still rely on userspace following select/erase/progress/write sequencing. Firmware writes are high risk by nature.
- Delayed NVRAM saves can be interrupted by disconnect or suspend; suspend tries to flush them, but USB failure paths only log errors.
- Gen 4 muteable controls encode transient switching/mute states, so missing `mute` metadata or wrong `phantom_first`/`level_input_first` offsets can invert or mis-index visible state.
- Speaker switching changes access permissions and volume-source mode for multiple controls; ordering bugs can leave controls read-only or writable incorrectly.
- The `SCARLETT2_USE_FCP_DRIVER` path hands off entirely to `snd_fcp_init()`, so behavior depends on module setup flags.

## Test Signals

Useful validation points include:

- Build coverage for this translation unit with `CONFIG_SND_USB_AUDIO` and the relevant UAPI header available.
- Connecting each supported USB product ID and verifying `snd_scarlett2_init()` creates only the expected controls for firmware version, MSD state, and product capabilities.
- ALSA control smoke tests: enumerate controls, get every control, set bounded writable controls, verify notifications update values without oopses or stale writability.
- Mux/mixer tests: change mux sources and matrix gains, verify `scarlett2_usb_set_mux()`/`scarlett2_usb_set_mix()` round-trip correctly and meters follow remapped/duplicate/off sources.
- Autogain/phantom interaction tests: while autogain is running, gain/level/air/phantom/safe/etc. controls become read-only or reject writes; while phantom is switching, autogain rejects writes.
- Persistence tests on older devices: verify config changes schedule and complete delayed save, and suspend flushes pending save.
- Flash hwdep tests with a non-firmware settings segment read and firmware segment erase/progress/write sequencing, including invalid segment, invalid offset, and concurrent ALSA-control access returning `-EBUSY`.
- Device map tests on Gen 4/Vocaster devices: proc file exists, reports the expected size, supports partial and unaligned reads, and returns valid base64/zlib JSON bytes.
- Disconnect/suspend/reboot tests should cover URB shutdown completion, reboot response tolerance, delayed-work cancellation, and no use-after-free in notification paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett2.h -->
# sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett2.h

## Purpose

`mixer_scarlett2.h` is the private declaration header for the Focusrite Scarlett 2 protocol mixer implementation. It exposes the single initialization hook used by the surrounding USB audio mixer code while keeping the large implementation details in `mixer_scarlett2.c`.

## Important API

- `int snd_scarlett2_init(struct usb_mixer_interface *mixer);`

This function is implemented in `mixer_scarlett2.c`. The USB audio mixer path calls it with the active `struct usb_mixer_interface`. It detects supported Focusrite devices, optionally delegates to the FCP driver, initializes proprietary USB notifications, reads device configuration, creates ALSA controls, registers the hwdep firmware/configuration interface, and exposes a proc device-map file when supported.

## Dependencies and Integration

The header assumes `struct usb_mixer_interface` is declared before inclusion. In this tree it is included from USB audio mixer code that already has the relevant ALSA USB mixer definitions. The include guard `__USB_MIXER_SCARLETT2_H` prevents duplicate declarations.

The declaration integrates the Scarlett 2 mixer implementation with the broader ALSA USB audio driver without exporting its internal structs, product tables, USB packet helpers, notification handlers, or control callbacks.

## Control Flow and State

This header contains no control flow and owns no state. All state is allocated and managed by `snd_scarlett2_init()` and the implementation's private data. The only observable behavior from this header is whether callers can link against the initialization entry point.

## Persistence Behavior

No persistence is implemented here. Persistent behavior, including delayed config saves and flash segment access, is handled in `mixer_scarlett2.c`.

## Risks

- Include-order matters because the header does not forward-declare `struct usb_mixer_interface`; callers must include the USB mixer definitions first.
- Any signature change must be reflected in the caller and implementation together, or the driver will fail to build.
- The broad implementation is hidden behind one API, so callers cannot express partial feature initialization or inspect support status except through the function return and created ALSA side effects.

## Test Signals

- A compile test should verify all users include this header after defining or declaring `struct usb_mixer_interface`.
- Link/build coverage should confirm exactly one implementation of `snd_scarlett2_init()` is available.
- Runtime tests are driven by `mixer_scarlett2.c`: successful probe should call this entry point and create the expected Focusrite controls or cleanly no-op for unsupported/disabled conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett2.h -->
