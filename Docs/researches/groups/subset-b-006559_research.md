# Group Research: subset-b-006559

This grouped report covers the exact subset-b-006559 source manifest. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/soundfont.c -->
# sources/distributed-fs/ceph-client/sound/synth/emux/soundfont.c

## Purpose
Implements ALSA SoundFont patch loading, GUS patch compatibility, preset-zone lookup, and lifecycle management for `struct snd_sf_list`. It accepts OSS-style SoundFont patch records from userspace, constructs in-memory soundfont/sample/zone lists, delegates actual sample storage to driver callbacks, and builds a preset hash for fast voice lookup by bank, preset, note, and velocity.

## Important APIs, Types, and Functions
Public entry points include `snd_soundfont_load()`, `snd_soundfont_load_guspatch()`, `snd_soundfont_search_zone()`, `snd_sf_new()`, `snd_sf_free()`, `snd_soundfont_remove_samples()`, `snd_soundfont_remove_unlocked()`, `snd_soundfont_close_check()`, and exported conversion helpers such as `snd_sf_linear_to_log()`, `snd_sf_calc_parm_hold()`, `snd_sf_calc_parm_attack()`, and `snd_sf_calc_parm_decay()`. Core private helpers are `open_patch()`, `close_patch()`, `load_info()`, `load_data()`, `load_map()`, `load_guspatch()`, `rebuild_presets()`, `add_preset()`, `delete_preset()`, `search_zones()`, `set_sample()`, and list allocators for `snd_soundfont`, `snd_sf_zone`, and `snd_sf_sample`.

## Control Flow
`snd_soundfont_load()` copies a `soundfont_patch_info` header from userspace, validates patch type and length, opens a patch under the preset mutex for `SNDRV_SFNT_OPEN_PATCH`, then requires matching `open_client` for later patch commands. `SNDRV_SFNT_LOAD_INFO` reads one voice-record header plus voice records, optionally rejects/replaces existing instrument zones, creates zones, initializes default parameters when requested, and resolves sample references. `SNDRV_SFNT_LOAD_DATA` validates sample metadata, rebases sample offsets relative to submitted data, allocates a sample, and calls `callback.sample_new()` to store waveform data. `SNDRV_SFNT_MAP_PRESET` creates shared mapping zones that recursively alias one preset/bank/key to another. Closing a patch clears `currsf`/`open_client` and rebuilds the preset table.

GUS patches are handled separately by `snd_soundfont_load_guspatch()`: it parses legacy `patch_info`, creates a shared GUS font, creates one sample and one zone, converts GUS frequency/envelope/pan/mode fields to SoundFont voice parameters, calls the sample callback, then inserts the zone into the preset table.

Voice lookup starts at `snd_soundfont_search_zone()`, which refuses lookup when `presets_locked` is set, searches requested bank/preset, optionally falls back to default bank/preset, and follows mapping zones recursively with a depth cap of five.

## State and Persistence
All persistent runtime state lives in `struct snd_sf_list`: linked soundfont list, current open font, open client id, preset hash table, allocation counters, locked counters, memory usage, callback table, and optional memory header. Soundfont, zone, and sample records persist until explicit removal or `snd_sf_free()`. Sample storage persists outside this file through callback-owned device memory; `mem_used` mirrors `sp->v.truesize`. `snd_soundfont_remove_unlocked()` keeps locked records by counter threshold and deletes newer zones/samples only.

## Dependencies and Integration Points
Depends on Linux user-copy helpers, ALSA core, `sound/soundfont.h`, `seq_oss_legacy.h`, and driver-provided `struct snd_sf_callback` operations. It integrates with synth drivers that need SoundFont patch loading and with `util_mem.c` through `struct snd_util_memhdr` passed into sample callbacks. The preset mutex and spinlock are ALSA SoundFont synchronization contracts used by callers doing atomic voice lookups.

## Risks
The userspace ABI accepts complex variable-length records; validation of lengths, signed fields, and sample-offset rebasing is security-critical. `load_info()` may create zones whose sample pointer is initially unresolved, relying on later rebuild to resolve them. Mapping recursion is bounded but aliasing can still produce surprising instrument selection. Callback failures must roll back newly allocated samples/zones; the GUS path explicitly frees a zone with `kfree(zone)` after it has been inserted into the font list, so error path review should confirm list integrity. State is shared across clients; `open_client` checks and preset locking are important race barriers.

## Test Signals
Useful tests include loading valid and malformed SoundFont records, duplicate shared samples, exclusive/replace write modes, preset mapping recursion and fallback defaults, GUS 8-bit/16-bit loop modes, sample callback failure rollback, remove-unlocked behavior with locked fonts, and concurrent lookup during patch load/removal. Sanitizer/fuzzing value is high around `copy_from_user()` lengths and sample offset validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/soundfont.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/util_mem.c -->
# sources/distributed-fs/ceph-client/sound/synth/util_mem.c

## Purpose
Provides a small generic allocator for soundcard/device memory represented as a linear address space. It tracks allocated blocks in offset order and supports both locked public APIs and unlocked internal helpers for callers that already hold `block_mutex`.

## Important APIs, Types, and Functions
Exports `snd_util_memhdr_new()`, `snd_util_memhdr_free()`, `snd_util_mem_alloc()`, `snd_util_mem_free()`, `snd_util_mem_avail()`, plus internal exported helpers `__snd_util_mem_alloc()`, `__snd_util_mem_free()`, and `__snd_util_memblk_new()`. It operates on `struct snd_util_memhdr` and `struct snd_util_memblk` from `<sound/util_mem.h>`.

## Control Flow
`snd_util_memhdr_new()` allocates the header, initializes size, mutex, and list head. `__snd_util_mem_alloc()` aligns requested sizes to even units, scans the sorted block list for the first gap, and inserts a new block after the previous block. `snd_util_mem_alloc()` wraps this in `block_mutex`. `snd_util_mem_free()` validates inputs, locks, removes the block from the list, decrements counters, and frees it. Header free drains every block without callbacks.

## State and Persistence
The header persists allocator-wide `size`, `used`, `nblocks`, `block_extra_size`, mutex, and ordered block list. Each block persists `offset` and `size`; optional extra bytes after the block structure allow device-specific metadata.

## Dependencies and Integration Points
Used by ALSA synth/sample loaders that need to reserve hardware sample RAM or similar linear resources. SoundFont sample callbacks receive an `snd_util_memhdr` and can use this allocator to back `snd_sf_sample` storage.

## Risks
The allocator is first-fit and non-compacting, so fragmentation can deny large allocations even when total available space is enough. Public allocation assumes `hdr` is non-null before taking `&hdr->block_mutex`; callers must not pass null. Size arithmetic uses ints/unsigned ints and should be reviewed for very large virtual regions. Header free does not coordinate with live users.

## Test Signals
Test odd-size alignment, exact-fit head/middle/tail gaps, fragmentation, free counter underflow prevention, extra metadata sizing, concurrent public allocate/free, and null/invalid argument handling through `snd_BUG_ON()` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/util_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/Makefile -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/Makefile

## Purpose
Defines the TerraTec DMX 6Fire USB ALSA module composition.

## Important APIs, Types, and Functions
Build variables are `snd-usb-6fire-y` and `obj-$(CONFIG_SND_USB_6FIRE)`. The module is assembled from `chip.o`, `comm.o`, `midi.o`, `control.o`, `firmware.o`, and `pcm.o`.

## Control Flow
Kbuild compiles the object list into `snd-usb-6fire.o` when `CONFIG_SND_USB_6FIRE` is enabled as built-in or module.

## State and Persistence
No runtime state. It persists the compile-time binding between Kconfig selection and driver objects.

## Dependencies and Integration Points
Depends on `sound/usb/Kconfig` selecting `SND_USB_6FIRE`. The listed objects mutually depend on shared headers under the same directory.

## Risks
Leaving out any object breaks probe, firmware, MIDI, PCM, or mixer functionality. Object order is conventional and does not encode init order; runtime init order is in `chip.c`.

## Test Signals
Build with `CONFIG_SND_USB_6FIRE=m` and `=y`; verify produced module exports one USB driver and includes firmware declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/chip.c -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/chip.c

## Purpose
Owns the TerraTec DMX 6Fire USB driver lifecycle: module parameters, USB probe/disconnect, ALSA card creation, subcomponent initialization, and teardown ordering.

## Important APIs, Types, and Functions
Key routines are `usb6fire_chip_probe()`, `usb6fire_chip_disconnect()`, `usb6fire_chip_abort()`, and `usb6fire_card_free()`. Static module arrays `index`, `id`, `enable`, and `chips` track ALSA card slots. `device_table` matches vendor `0x0ccd`, product `0x0080`. `usb_driver` registers the driver as `snd-usb-6fire`.

## Control Flow
Probe locks `register_mutex`, reuses an existing `sfire_chip` if another interface of the same device is probed, otherwise finds a free card slot. It calls `usb6fire_fw_init()` before card creation; `FW_NOT_READY` means firmware was uploaded and the device should reconnect before ALSA registration. For ready firmware it selects interface 0 altsetting 0, creates an ALSA card, initializes `comm`, `midi`, `pcm`, and `control` in that order, registers the card, stores intfdata, and publishes the chip in `chips[]`. On failure it frees the card, which triggers component destroy callbacks through `private_free`.

Disconnect decrements `intf_count`, removes the chip from `chips[]` on final interface, marks shutdown, disconnects ALSA, aborts live URBs/subsystems, and calls `snd_card_free_when_closed()` last because the embedded chip can be freed immediately.

## State and Persistence
Per-device state is `struct sfire_chip` embedded in ALSA card private data. Slot state persists in `chips[regidx]`, with `intf_count` joining multiple USB interfaces. Runtime component pointers are populated by submodule init and cleared by destroy.

## Dependencies and Integration Points
Integrates with `firmware.c` for cold-start loading, `comm.c` for command/MIDI interrupt transport, `midi.c`, `pcm.c`, `control.c`, ALSA card APIs, and USB core probe/disconnect.

## Risks
Probe holds `register_mutex` across firmware loading and all subsystem initialization, so long firmware/control paths serialize all 6fire registration. Error paths rely on `snd_card_free()` invoking `usb6fire_card_free()` only for initialized pointers. Disconnect must not touch `chip` after `snd_card_free_when_closed()`.

## Test Signals
Test cold firmware upload path returning without card registration, hot ready firmware path, multiple interface probes incrementing/decrementing `intf_count`, failure injection for each component init, and disconnect while PCM/MIDI streams are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/chip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/chip.h -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/chip.h

## Purpose
Declares the shared 6Fire per-device state container.

## Important APIs, Types, and Functions
`struct sfire_chip` holds `usb_device`, `snd_card`, interface count, registration index, shutdown flag, and pointers to `midi_runtime`, `pcm_runtime`, `control_runtime`, and `comm_runtime`.

## Control Flow
No executable logic. The struct fields are populated in `chip.c` and consumed by every 6fire submodule.

## State and Persistence
The struct persists as ALSA card private data until `snd_card_free_when_closed()`. `shutdown` gates URB resubmission in `comm.c`, while component pointers gate abort/destroy calls.

## Dependencies and Integration Points
Includes `common.h` for forward declarations and core USB/ALSA includes. All 6fire implementation files include this header to access cross-module state.

## Risks
The struct is the ownership hub; dangling component pointers or use after card free are primary risks. Any new component must follow the existing init/destroy pointer discipline.

## Test Signals
Compile coverage is most important. Runtime tests should observe that component pointers are null after destroy and that disconnect sets `shutdown` before URB abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/chip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/comm.c -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/comm.c

## Purpose
Implements 6Fire device command transport and inbound interrupt receiver on endpoint 1. It also dispatches inbound MIDI packets to the MIDI runtime.

## Important APIs, Types, and Functions
Public functions are `usb6fire_comm_init()`, `usb6fire_comm_abort()`, and `usb6fire_comm_destroy()`. Runtime callbacks assigned into `struct comm_runtime` are `init_urb`, `write8`, and `write16`. Internal helpers include `usb6fire_comm_receiver_handler()`, `usb6fire_comm_init_buffer()`, and `usb6fire_comm_send_buffer()`.

## Control Flow
Initialization allocates `comm_runtime`, a 64-byte receiver buffer, configures a receive interrupt URB on endpoint 1, submits it, and stores function pointers for other submodules. The receive completion checks packet id `0x10` for MIDI input and calls `midi_rt->in_received()` with payload bytes. Unless `chip->shutdown` is set, the handler resubmits the receiver URB. Writes allocate a 13-byte temporary buffer, encode request-specific packet layouts, synchronously send with `usb_interrupt_msg()`, validate transferred length, then free the buffer.

## State and Persistence
State includes the receiver URB, receiver buffer, chip pointer, serial field, and function pointers. The receiver URB persists from init until abort/destroy. No device settings are cached here beyond transient command buffers.

## Dependencies and Integration Points
Used by `control.c` to write mixer/rate/channel registers, by `midi.c` to initialize its output URB through `init_urb`, and by `chip.c` for lifecycle. Depends on USB interrupt pipes and 6Fire endpoint protocol.

## Risks
`write16` declaration in `comm.h` names `vh, vl` while implementation expects `vl, vh`; callers in this tree pass low then high and the function pointer type is positional, but naming can mislead future edits. Receive handler resubmission failures only warn. Temporary command allocation on every mixer write can fail under memory pressure. Destroy assumes abort already stopped the URB.

## Test Signals
Exercise all request types (`0x02`, `0x12`, `0x20`-`0x22`), short transfer error handling, inbound MIDI dispatch, receiver resubmit on normal completions, and no resubmit after shutdown/poison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/comm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/comm.h -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/comm.h

## Purpose
Defines the 6Fire communication runtime interface shared by command, MIDI, control, and chip lifecycle code.

## Important APIs, Types, and Functions
Declares `COMM_RECEIVER_BUFSIZE = 64`, `struct comm_runtime`, and lifecycle functions `usb6fire_comm_init()`, `usb6fire_comm_abort()`, and `usb6fire_comm_destroy()`. The runtime struct exposes `init_urb`, `write8`, and `write16` callbacks.

## Control Flow
No executable logic. Other modules dereference function pointers after `usb6fire_comm_init()` succeeds.

## State and Persistence
The struct owns a receive URB and buffer, a chip pointer, serial byte, and command/MIDI helper callbacks. It persists until card private free calls destroy.

## Dependencies and Integration Points
Includes `common.h`. `midi.c` uses `init_urb`; `control.c` uses `write8`/`write16`; `chip.c` owns lifetime.

## Risks
The `write16` parameter names are reversed from the implementation's low/high order, creating maintenance risk. Since function pointers are optional by convention but not null-checked by all callers, init ordering must keep comm first.

## Test Signals
Compile and runtime smoke tests should confirm control rate writes and MIDI URB init use the expected byte order and that no caller uses comm before initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/comm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/common.h -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/common.h

## Purpose
Provides common includes, prefix macro, and forward declarations for the 6Fire driver.

## Important APIs, Types, and Functions
Defines `PREFIX "6fire: "` and forward declares `sfire_chip`, `midi_runtime`, `pcm_runtime`, `control_runtime`, and `comm_runtime`.

## Control Flow
No executable logic.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Includes Linux slab and USB headers plus ALSA core, making these available to 6fire headers.

## Risks
Header bloat can mask missing includes in implementation files. The prefix is not consistently used across all logged errors.

## Test Signals
Build-only signal: headers should compile independently through the implementation files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/control.c -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/control.c

## Purpose
Implements mixer controls and hardware configuration writes for 6Fire: analog playback volume/switches, analog capture volume, line/phono route, optical/coax route, digital thru, sample-rate altsetting, and channel enablement.

## Important APIs, Types, and Functions
Public lifecycle functions are `usb6fire_control_init()`, `usb6fire_control_abort()`, and `usb6fire_control_destroy()`. Runtime callbacks published through `control_runtime` are `update_streaming`, `set_rate`, and `set_channels`. Important helpers include output/input volume updates, route updates, `usb6fire_control_set_rate()`, `usb6fire_control_set_channels()`, `usb6fire_control_streaming_update()`, and ALSA kcontrol get/put/info callbacks.

## Control Flow
Initialization allocates runtime state, assigns callback hooks, writes a fixed `init_data` register sequence through `comm`, pushes default route/volume/mute/input/streaming state to the device, creates virtual master controls for playback volume and switch, and registers additional route/capture controls. Mixer `put` callbacks update cached state, clear per-channel updated bits when needed, then send command writes. PCM code calls `set_rate`, `set_channels`, and `update_streaming` during stream prepare/start/stop.

## State and Persistence
`control_runtime` caches device-visible mixer state: output volumes, update bitmask, mute bitmask, input volumes/update bitmask, route booleans, and `usb_streaming`. This is not persisted across unplug or module reload; it is replayed during init.

## Dependencies and Integration Points
Depends on `comm_runtime` for all register writes, `pcm.c` for streaming/rate calls, ALSA control APIs, and `SND_VMASTER` support selected by Kconfig.

## Risks
Initialization ignores return values from many `comm_rt->write8()` update calls, so a partially configured device can still register. Kcontrol callbacks have limited synchronization around cached state and USB writes. `spdif_out`/`spdif_in` parameters are currently ignored in `set_channels()`. Digital-thru changes may set a fixed sample rate when USB streaming is off.

## Test Signals
Use `amixer` to change every control and verify expected USB command writes, validate virtual master follower behavior, test sample-rate changes from PCM prepare, and inject comm write failures to confirm ALSA control return behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/control.h -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/control.h

## Purpose
Declares 6Fire mixer/control runtime state and sample-rate constants.

## Important APIs, Types, and Functions
Defines `CONTROL_MAX_ELEMENTS`, six `CONTROL_RATE_*` values plus `CONTROL_N_RATES`, `struct control_runtime`, and lifecycle functions `usb6fire_control_init()`, `usb6fire_control_abort()`, `usb6fire_control_destroy()`.

## Control Flow
No executable logic. PCM code uses the function pointers and rate enum to configure hardware.

## State and Persistence
Runtime fields cache route switches, USB streaming flag, volumes, mute state, and update masks. The `element` array is declared but not actively populated in current `control.c`.

## Dependencies and Integration Points
Includes `common.h`; used by `chip.c`, `control.c`, and `pcm.c`.

## Risks
Enums must stay synchronized with rate tables in `control.c`, `pcm.c`, and endpoint packet sizes in `firmware.c`. The unused `element` array may confuse ownership expectations.

## Test Signals
Build coverage plus runtime sample-rate tests at all six rates are the best signal that enum/table synchronization is intact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/firmware.c -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/firmware.c

## Purpose
Loads and validates the 6Fire device firmware chain: EZ-USB loader firmware, FPGA bitstream, and EZ-USB application firmware. It also checks runtime firmware version and passes endpoint packet-size data needed by later PCM altsettings.

## Important APIs, Types, and Functions
Public API is `usb6fire_fw_init()`. Important helpers are Intel HEX parser functions `usb6fire_fw_ihex_hex()`, `usb6fire_fw_ihex_next_record()`, `usb6fire_fw_ihex_init()`, vendor control helpers `usb6fire_fw_ezusb_write()`/`read()`, `usb6fire_fw_fpga_write()`, upload helpers `usb6fire_fw_ezusb_upload()` and `usb6fire_fw_fpga_upload()`, and `usb6fire_fw_check()`.

## Control Flow
`usb6fire_fw_init()` reads an 8-byte firmware state block. State `0x01` uploads the loader firmware and returns `FW_NOT_READY`. State `0x02` verifies current version, uploads FPGA firmware with bytes bit-reversed in 512-byte chunks, then uploads application firmware with endpoint packet-size postdata at address `0x0003`, returning `FW_NOT_READY`. State `0x03` verifies the known firmware version and returns ready. Unknown signatures or states fail.

Intel HEX upload validates the whole firmware by scanning records and CRCs, stops the EZ-USB CPU, writes all data records to addresses, optionally writes postdata, then restarts the CPU.

## State and Persistence
No long-lived driver state. Firmware persists on the USB device until power cycle or reset. The static `ep_w_max_packet_size` table must match PCM packet sizes and control rate altsettings.

## Dependencies and Integration Points
Uses Linux firmware loader, USB control/bulk APIs, `bitrev8()`, and module firmware declarations for `6fire/dmx6firel2.ihx`, `6fire/dmx6fireap.ihx`, and `6fire/dmx6firecf.bin`. Called before ALSA card creation in `chip.c`.

## Risks
Firmware files are external runtime dependencies; missing files prevent device startup. HEX parser accepts only data and EOF records, so extended-address records are unsupported. Packet-size table synchronization is critical for high-rate ISO transfers. Upload returns `FW_NOT_READY`, relying on device reconnect/reprobe semantics.

## Test Signals
Test all firmware states with valid/missing/corrupt firmware files, HEX CRC failure, short bulk transfer from FPGA upload, unknown version rejection, and ready-state probe without upload. Confirm dmesg firmware requests match `MODULE_FIRMWARE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/firmware.h -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/firmware.h

## Purpose
Declares the 6Fire firmware readiness API and state constants.

## Important APIs, Types, and Functions
Defines `FW_READY = 0`, `FW_NOT_READY = 1`, and `usb6fire_fw_init(struct usb_interface *intf)`.

## Control Flow
No executable logic. Probe interprets `FW_NOT_READY` as a successful firmware upload that should not register an ALSA card yet.

## State and Persistence
No state in header.

## Dependencies and Integration Points
Includes `common.h`; used by `chip.c` and implemented by `firmware.c`.

## Risks
The distinction between `0` ready and positive `FW_NOT_READY` is part of probe control flow; callers must not treat all nonnegative returns as ready.

## Test Signals
Probe tests should cover both ready and not-ready return paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/midi.c -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/midi.c

## Purpose
Implements ALSA rawmidi input/output for the 6Fire device using the comm endpoint protocol.

## Important APIs, Types, and Functions
Public lifecycle functions are `usb6fire_midi_init()`, `usb6fire_midi_abort()`, and `usb6fire_midi_destroy()`. ALSA callbacks are `usb6fire_midi_out_trigger()`, `usb6fire_midi_out_drain()`, `usb6fire_midi_in_trigger()`, plus trivial open/close handlers. Completion/input helpers are `usb6fire_midi_out_handler()` and `usb6fire_midi_in_received()`.

## Control Flow
Initialization allocates `midi_runtime`, output buffer, initializes command header bytes, sets spinlocks, asks `comm_runtime` to initialize the output URB, creates a duplex rawmidi device, and attaches output/input ops. Output trigger pulls up to 60 bytes from ALSA rawmidi into the command buffer, stamps length and serial, submits the URB, and records the active substream. Output completion transmits the next packet if available or clears `out`. Input bytes arrive through `comm.c` and are pushed to the active input substream under lock.

## State and Persistence
Persistent runtime state includes rawmidi instance, active input/output substream pointers, spinlocks, output URB, serial byte, and output buffer. It persists until card free.

## Dependencies and Integration Points
Depends on ALSA rawmidi, `comm_runtime` for endpoint/URB setup, and `chip.c` for lifecycle. Incoming MIDI is dispatched by `comm.c`.

## Risks
`ret` in output trigger is `__s8`, while `snd_rawmidi_transmit()` returns int; practical payload is small, but error values and length types deserve caution. Drain waits up to one second by polling `rt->out`. Output trigger and completion share state under spinlock, but USB submission failure after filling the buffer leaves active state dependent on branch behavior.

## Test Signals
Run bidirectional MIDI loop tests, trigger stop while URB active, close/drain during output, disconnect during active MIDI, and high-throughput output requiring chained completion sends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/midi.h -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/midi.h

## Purpose
Declares 6Fire rawmidi runtime state and lifecycle functions.

## Important APIs, Types, and Functions
`struct midi_runtime` stores chip pointer, rawmidi instance, active substreams, locks, output URB, serial, buffer, and input callback pointer. Public functions are `usb6fire_midi_init()`, `usb6fire_midi_abort()`, and `usb6fire_midi_destroy()`.

## Control Flow
No executable logic. `comm.c` calls `in_received`; `chip.c` calls lifecycle functions.

## State and Persistence
The runtime persists as `chip->midi`. `in_active` and `buffer_offset` are present but not used by current implementation.

## Dependencies and Integration Points
Includes `common.h`; used by `midi.c`, `comm.c`, and `chip.c`.

## Risks
Unused fields can mislead future changes. Active substream pointers require disconnect/abort ordering to avoid completion callbacks after free.

## Test Signals
Compile plus runtime MIDI open/trigger/abort coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/midi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/pcm.c -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/pcm.c

## Purpose
Implements 6Fire duplex PCM streaming over isochronous USB endpoints. Capture URB completions drive both capture ingestion and playback packet generation so output mirrors the incoming packet cadence.

## Important APIs, Types, and Functions
Public lifecycle functions are `usb6fire_pcm_init()`, `usb6fire_pcm_abort()`, and `usb6fire_pcm_destroy()`. ALSA PCM ops are open, close, prepare, trigger, and pointer. Important helpers include `usb6fire_pcm_set_rate()`, stream start/stop, capture/playback format copy functions, in/out URB handlers, URB initialization, and buffer allocation/destruction.

## Control Flow
Open assigns hardware constraints, limiting rates to the already selected runtime rate if streaming is active and setting max channels by direction. Prepare resets positions; if streaming is disabled, it maps ALSA rate to internal index, asks control code to stop streaming, set rate/altsetting/channel enables, restart hardware streaming, submits all input URBs, and waits for an output URB completion to confirm the stream is running. The input URB handler validates packet status, copies capture data into ALSA buffers, calculates matching output packet lengths, zero-fills playback packets, copies active playback data, stamps 6Fire packet headers/check bytes, submits output URB, then resubmits input URB. Trigger just toggles `pcm_substream.active`. Close deactivates substreams and stops USB streaming when both are closed.

## State and Persistence
`pcm_runtime` stores playback/capture substream state, panic flag, URB arrays and buffers, channel counts, packet sizes, stream mutex, stream state, rate index, wait queue, and startup condition. Per-substream state tracks active flag and DMA/period offsets. State is reset at stream stop and destroyed at card free.

## Dependencies and Integration Points
Depends on `control_runtime` to configure rate, altsetting, channel masks, and streaming bit; on USB ISO URBs; and on ALSA PCM vmalloc-managed buffers. Packet-size tables must match `firmware.c` endpoint descriptors and `control.c` altsettings.

## Risks
The in-URB handler calls `usb_submit_urb()` without checking return values for in/out resubmission. Any ISO packet status sets `panic`, after which PCM returns XRUN/EPIPE until reset by device lifecycle. Format handling uses pointer offset tricks for S24/S32 packing; alignment errors could corrupt samples. Stream start waits only one second for output running. Rate table synchronization across files is a recurring maintenance risk.

## Test Signals
Test playback-only, capture-only, and duplex streams at all six rates; S24_LE and S32_LE formats; period elapsed accounting across ring wrap; disconnect during active stream; ISO packet error forcing panic; and startup timeout/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/pcm.h -->
# sources/distributed-fs/ceph-client/sound/usb/6fire/pcm.h

## Purpose
Declares 6Fire PCM URB, substream, and runtime structures.

## Important APIs, Types, and Functions
Defines `PCM_N_URBS = 16`, `PCM_N_PACKETS_PER_URB = 8`, and `PCM_MAX_PACKET_SIZE = 604`. `struct pcm_urb` embeds `struct urb` followed immediately by ISO descriptors, buffer pointer, and peer pointer. `struct pcm_substream` tracks lock, ALSA substream, active flag, DMA offset, and period offset. `struct pcm_runtime` holds full duplex state.

## Control Flow
No executable logic. The "do not separate" comment around `urb` and packet descriptors reflects the kernel URB allocation layout expectation for inline ISO descriptors.

## State and Persistence
Runtime state persists as `chip->pcm` and owns URB arrays and buffers until destroy.

## Dependencies and Integration Points
Includes ALSA PCM and mutex APIs plus `common.h`; used by `pcm.c` and `chip.c`.

## Risks
Changing `PCM_MAX_PACKET_SIZE` requires keeping firmware endpoint descriptors and rate packet tables in sync. Reordering `struct pcm_urb` fields could break ISO descriptor assumptions.

## Test Signals
Build tests plus runtime high-rate streaming are needed to validate max packet sizing and inline descriptor layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/6fire/pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/Kconfig -->
# sources/distributed-fs/ceph-client/sound/usb/Kconfig

## Purpose
Defines configuration options for ALSA USB sound drivers, including generic USB Audio, MIDI 2.0 support, CAIAQ, 6Fire, BCD2000, and other USB audio device drivers.

## Important APIs, Types, and Functions
Key symbols in this subset are `SND_USB`, `SND_USB_AUDIO`, `SND_USB_AUDIO_MIDI_V2`, `SND_USB_AUDIO_USE_MEDIA_CONTROLLER`, `SND_USB_CAIAQ`, `SND_USB_CAIAQ_INPUT`, `SND_USB_6FIRE`, and `SND_BCD2000`.

## Control Flow
The top-level `menuconfig SND_USB` depends on `USB`; all nested drivers are available only under `if SND_USB && USB`. Symbols select required ALSA subsystems such as `SND_PCM`, `SND_RAWMIDI`, `SND_HWDEP`, `SND_VMASTER`, firmware loader, and bit reversal helpers.

## State and Persistence
No runtime state. Kconfig selections persist in the kernel `.config` and drive Kbuild object inclusion.

## Dependencies and Integration Points
Feeds `sound/usb/Makefile` and subdirectory Makefiles. `SND_USB_CAIAQ_INPUT` depends on input core availability compatible with the CAIAQ module linkage. `SND_USB_6FIRE` selects firmware loader and `BITREVERSE` needed by `firmware.c`.

## Risks
Missing `select` dependencies lead to link failures or disabled runtime features. `SND_USB_CAIAQ_INPUT` has a subtle dependency because input support can be built-in or tied to the CAIAQ module. Help text documents firmware requirements for 6Fire and incomplete audio support for BCD2000.

## Test Signals
Run `allmodconfig`, `allyesconfig`, and minimal configs for `SND_USB_AUDIO`, `SND_USB_CAIAQ` with/without input, `SND_USB_6FIRE`, and `SND_BCD2000`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/Makefile -->
# sources/distributed-fs/ceph-client/sound/usb/Makefile

## Purpose
Defines Kbuild composition for the ALSA USB audio subtree.

## Important APIs, Types, and Functions
`snd-usb-audio-y` lists the generic USB audio core objects, conditionally adding `midi2.o` and `media.o`. `snd-usbmidi-lib-y` builds shared MIDI support. `obj-$(CONFIG_SND_USB_AUDIO)` includes both `snd-usb-audio.o` and `snd-usbmidi-lib.o`. `obj-$(CONFIG_SND)` descends into device-specific subdirectories including `caiaq/`, `6fire/`, and `bcd2000/`.

## Control Flow
Kbuild links objects based on the active config. The shared MIDI library is built for generic USB audio and several other drivers.

## State and Persistence
No runtime state. It persists compile-time module boundaries and subdirectory traversal.

## Dependencies and Integration Points
Integrates with `Kconfig` symbols and subdirectory Makefiles. `card.c` is part of `snd-usb-audio-y`.

## Risks
Device-specific subdirectories are traversed under `CONFIG_SND`, but their own Makefiles gate object inclusion by more specific symbols. Object list drift can omit new source files.

## Test Signals
Build matrix for generic USB audio with/without MIDI 2.0 and media controller, plus module builds for `6fire`, `caiaq`, and `bcd2000`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/bcd2000/Makefile -->
# sources/distributed-fs/ceph-client/sound/usb/bcd2000/Makefile

## Purpose
Defines the Behringer BCD2000 ALSA module build.

## Important APIs, Types, and Functions
Builds `snd-bcd2000.o` from `bcd2000.o` under `obj-$(CONFIG_SND_BCD2000)`.

## Control Flow
Kbuild includes the module only when `SND_BCD2000` is enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Driven by `sound/usb/Kconfig`; the source depends on ALSA rawmidi and USB core.

## Risks
Low risk; a missing object means the module has no implementation.

## Test Signals
Build as module and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/bcd2000/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/bcd2000/bcd2000.c -->
# sources/distributed-fs/ceph-client/sound/usb/bcd2000/bcd2000.c

## Purpose
Implements a USB rawmidi driver for the Behringer BCD2000 DJ controller. It provides MIDI input/output only; the Kconfig help notes audio support is not implemented here.

## Important APIs, Types, and Functions
Core type is `struct bcd2000`, holding USB, ALSA, rawmidi, substream, URB, buffers, anchor, and slot state. Key functions include `bcd2000_probe()`, `bcd2000_disconnect()`, `bcd2000_init_midi()`, `bcd2000_init_device()`, MIDI trigger/open/close callbacks, `bcd2000_midi_send()`, `bcd2000_input_complete()`, `bcd2000_output_complete()`, and `bcd2000_free_usb_related_resources()`.

## Control Flow
Probe allocates a free ALSA card slot under `devices_mutex`, creates an ALSA card, names it, initializes rawmidi and interrupt URBs, submits a fixed device init sequence, submits the input URB, waits briefly for anchored init completion, registers the card, and stores interface data. Output trigger records the active output substream and starts sending if idle; completion clears active state and sends more queued MIDI. Input completion parses a BCD2000 packet with payload length in byte 0 and passes bytes 1..N to the active input substream, then resubmits the input URB. Disconnect disconnects ALSA, kills/frees URBs, clears slot bit, and defers card free until close.

## State and Persistence
Global `devices_used` tracks occupied ALSA slots. Per-device state persists in card private data: buffers, URBs, active output flag, rawmidi substream pointers, and USB interface pointer.

## Dependencies and Integration Points
Depends on USB interrupt endpoints `0x81` input and `0x01` output, ALSA rawmidi, and kernel bitmap/mutex helpers. It registers USB id `1397:00bd`.

## Risks
Substream pointers and `midi_out_active` are not protected by locks; completion and trigger paths can race under SMP. `bcd2000_init_midi()` can return after one URB allocation fails without freeing the other until higher-level error cleanup, which does call the shared resource cleanup. The init wait uses an anchor but URBs remain anchored after completions unless unanchored by core completion semantics; behavior should be verified. Input packet length is clamped by actual buffer length, which is good, but malformed packets are silently ignored.

## Test Signals
Test probe/disconnect, rawmidi bidirectional traffic, init sequence submission, close while output active, unplug during input/output URBs, invalid endpoint descriptors, and repeated open/close under concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/bcd2000/bcd2000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/Makefile -->
# sources/distributed-fs/ceph-client/sound/usb/caiaq/Makefile

## Purpose
Defines Kbuild composition for the Native Instruments/CAIAQ USB audio driver.

## Important APIs, Types, and Functions
`snd-usb-caiaq-y` includes `device.o`, `audio.o`, `midi.o`, and `control.o`; `snd-usb-caiaq-$(CONFIG_SND_USB_CAIAQ_INPUT)` conditionally adds `input.o`. `obj-$(CONFIG_SND_USB_CAIAQ)` builds `snd-usb-caiaq.o`.

## Control Flow
Kbuild conditionally includes Linux input support in the same module when enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Driven by `SND_USB_CAIAQ` and `SND_USB_CAIAQ_INPUT` Kconfig symbols.

## Risks
Input support is compile-time optional; code paths in `device.c` are guarded by `CONFIG_SND_USB_CAIAQ_INPUT`, so object selection must match those guards.

## Test Signals
Build CAIAQ with input enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/audio.c -->
# sources/distributed-fs/ceph-client/sound/usb/caiaq/audio.c

## Purpose
Implements CAIAQ PCM audio over isochronous USB endpoints for multiple Native Instruments devices. It supports paired stereo streams, device-specific sample alignment modes, and duplex operation where capture completions generate matching playback URBs.

## Important APIs, Types, and Functions
Public functions are `snd_usb_caiaq_audio_init()`, `snd_usb_caiaq_audio_disconnect()`, and `snd_usb_caiaq_audio_free()`. ALSA PCM ops include open, close, hw_free, prepare, trigger, and pointer. Key helpers include `stream_start()`, `stream_stop()`, `activate_substream()`, `deactivate_substream()`, `read_in_urb_mode0/2/3()`, `fill_out_urb_mode_0/3()`, `read_completed()`, `write_completed()`, `alloc_urbs()`, and `free_urbs()`.

## Control Flow
Initialization derives audio stream counts from device spec, creates an ALSA PCM with one substream per stereo stream, sets supported rates by product id, allocates callback info plus 32 input and 32 output ISO URBs, and registers PCM ops. Prepare sets per-stream buffer offsets according to `spec.data_alignment`; if streaming is not active, it locks sample rate for all active streams, computes bytes-per-packet, sends audio params over EP1, starts streaming by submitting all input URBs, and waits for the first output completion. Input URB completion finds a free output URB bit, mirrors input frame lengths into output frames, under spinlock fills playback data and reads capture data, reports elapsed periods, submits output URB if data was present, and resubmits input URB. Write completion marks output running and clears the active bit.

## State and Persistence
State is stored in `snd_usb_caiaqdev`: stream counts, streaming flags, per-stream buffer/period positions, panic flags, audio buffers, samplerate mask, bytes-per-packet, out URB active bitmask, substream arrays, PCM handle, URB arrays, and callback info. It persists until card free; disconnect stops streaming but final memory cleanup happens in `audio_free()`.

## Dependencies and Integration Points
Depends on `device.c` command helpers for setting audio params and on CAIAQ device spec received via EP1. Integrates with ALSA PCM vmalloc buffers and USB ISO endpoints 2 capture / 6 playback.

## Risks
Read completion uses `urb->iso_frame_desc[outframe].actual_length` when assigning output length while iterating `frame`; review suggests it likely meant the current input frame, so nonmatching skipped frames may be risky. URB submit return values in completion paths are mostly ignored. Stream position arrays are indexed by substream number and require `n_streams <= MAX_STREAMS`. Alignment modes are protocol-sensitive and panic on check-byte mismatch. Closing checks substream arrays before `hw_free()` may leave stream running until `hw_free()` deactivates.

## Test Signals
Test all supported sample rates per product, data alignment modes 0/2/3, multiple stereo stream counts, playback/capture period elapsed behavior, ISO frame status errors, output URB exhaustion, disconnect while streaming, and audio-param timeout/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/audio.h -->
# sources/distributed-fs/ceph-client/sound/usb/caiaq/audio.h

## Purpose
Declares CAIAQ audio lifecycle hooks.

## Important APIs, Types, and Functions
Exports declarations for `snd_usb_caiaq_audio_init()`, `snd_usb_caiaq_audio_disconnect()`, and `snd_usb_caiaq_audio_free()`.

## Control Flow
No executable logic. `device.c` calls these during setup, disconnect, and card free.

## State and Persistence
No state in header.

## Dependencies and Integration Points
Requires `struct snd_usb_caiaqdev` from `device.h` to be visible before use.

## Risks
Call order matters: disconnect should stop streams before free releases URBs.

## Test Signals
Build coverage and disconnect/free lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/control.c -->
# sources/distributed-fs/ceph-client/sound/usb/caiaq/control.c

## Purpose
Creates per-product ALSA HWDEP controls for CAIAQ/Native Instruments LEDs, input modes, ground lift, software lock, and controller illumination state.

## Important APIs, Types, and Functions
Public function is `snd_usb_caiaq_control_init()`. Core callbacks are `control_info()`, `control_get()`, and `control_put()` using a shared `kcontrol_template`. `struct caiaq_controller` maps control names to indexes, with many static per-product tables such as `ak1_controller`, `rk2_controller`, `rk3_controller`, `kore_controller`, `a8dj_controller`, `kontrolx1_controller`, `kontrols4_controller`, and `maschine_controller`.

## Control Flow
`snd_usb_caiaq_control_init()` selects a control table by USB id and calls `add_controls()`. Each control uses `private_value` either as a bit position into `control_state` or as a byte index flagged by `CNT_INTVAL`. `control_info()` exposes boolean or bounded integer ranges, with product-specific max values. `control_put()` updates the cached byte/bit, sends the changed `control_state` to the device using EP1 commands, endpoint 8 for Traktor Kontrol S4 integer controls, or banked LED dimming for Maschine, and rolls back cache on USB error.

## State and Persistence
The persistent state is `cdev->control_state[256]` plus `ep8_out_buf`. It represents current software-visible control/LED settings and is initialized partly by `device.c` for Audio 8 DJ.

## Dependencies and Integration Points
Depends on `device.c` command helpers and product ids in `device.h`. The controls are added after `snd_card_register()` in `setup_card()`, so they become part of the ALSA card interface.

## Risks
`kcontrol_template` is a mutable static modified during `add_controls()`; registration is serialized by probe context, but static mutation is fragile. Control state writes can send all 256 bytes for many simple changes. Bounds are based on table correctness; out-of-range private indexes would access `control_state`. Product-specific endpoint 8 path must match descriptors.

## Test Signals
Enumerate controls for each supported product id, write every control boundary value, inject USB command failure to verify rollback, and test Maschine bank split and S4 endpoint 8 writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/control.h -->
# sources/distributed-fs/ceph-client/sound/usb/caiaq/control.h

## Purpose
Declares CAIAQ control initialization.

## Important APIs, Types, and Functions
Provides `snd_usb_caiaq_control_init(struct snd_usb_caiaqdev *cdev)`.

## Control Flow
No executable logic. Called from `device.c` after card registration.

## State and Persistence
No header-owned state.

## Dependencies and Integration Points
Requires `struct snd_usb_caiaqdev` from `device.h`.

## Risks
Only init is exposed; controls are freed by ALSA card teardown rather than a module-specific destroy function.

## Test Signals
Build and ALSA control enumeration after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/device.c -->
# sources/distributed-fs/ceph-client/sound/usb/caiaq/device.c

## Purpose
Owns CAIAQ USB driver probe/disconnect, EP1 command transport, device spec discovery, product-specific startup, ALSA card creation, and subsystem initialization.

## Important APIs, Types, and Functions
USB lifecycle functions are `snd_probe()` and `snd_disconnect()`. Card helpers include `create_card()`, `init_card()`, `setup_card()`, and `card_free()`. EP1 command functions are `snd_usb_caiaq_send_command()`, `snd_usb_caiaq_send_command_bank()`, `snd_usb_caiaq_set_audio_params()`, and `snd_usb_caiaq_set_auto_msg()`. Completion handler `usb_ep1_command_reply_dispatch()` routes device info, audio-param acknowledgments, MIDI input, control-state reads, and input events.

## Control Flow
Probe creates an ALSA card with embedded `snd_usb_caiaqdev`, stores intfdata, sets interface 0 altsetting 1, initializes EP1 input and MIDI output bulk URBs, submits EP1 input, requests device info, waits for spec, gets USB strings, names the card, and calls `setup_card()`. Setup performs product-specific startup writes, initializes audio if any audio I/O exists, initializes MIDI if MIDI ports exist, optionally initializes input, registers the card, then adds controls. Disconnect disconnects ALSA, tears down input/audio, kills EP1 and MIDI output URBs, and defers card free.

## State and Persistence
State is centralized in `snd_usb_caiaqdev`, embedding a generic `snd_usb_audio` plus EP buffers, spec, wait queues, flags, product strings, audio/MIDI/control/input state, and ALSA handles. USB device refcount is held via `usb_get_dev()` until `card_free()`.

## Dependencies and Integration Points
Depends on USB core, ALSA core/PCM/rawmidi/control, and local `audio.c`, `midi.c`, `control.c`, and optional `input.c`. Uses Native Instruments USB ids declared in `device.h`.

## Risks
`enable[]` selection in `create_card()` picks the first enabled slot rather than tracking occupied slots, unlike many ALSA drivers; multiple devices may compete for the same configured slot behavior. `snd_usb_caiaq_send_command()` does not validate `actual_len` for bulk sends. EP1 command replies requeue after processing but return without requeue on URB error. Controls are added after card registration, which can expose a partially initialized card if control init fails.

## Test Signals
Test every product id path, device-info timeout, audio-param ack timeout/failure, EP1 MIDI/input dispatch, Audio 8 DJ control-state initialization, disconnect during waits, and probe with multiple CAIAQ devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/device.h -->
# sources/distributed-fs/ceph-client/sound/usb/caiaq/device.h

## Purpose
Defines CAIAQ/Native Instruments product ids, endpoint command constants, device specification format, central runtime state, and command helper prototypes.

## Important APIs, Types, and Functions
Important definitions include `USB_VID_NATIVEINSTRUMENTS`, product ids for RigKontrol, Kore, Audio DJ, Traktor, and Maschine devices, `EP1_BUFSIZE`, `EP4_BUFSIZE`, `MAX_STREAMS`, EP1 command ids, `struct caiaq_device_spec`, `struct snd_usb_caiaqdev`, `struct snd_usb_caiaq_cb_info`, `caiaqdev()` and `caiaqdev_to_dev()` macros, plus EP1 command helper prototypes.

## Control Flow
No executable logic. The packed `caiaq_device_spec` is filled from an EP1 GET_DEVICE_INFO reply and drives audio/MIDI/input initialization.

## State and Persistence
`snd_usb_caiaqdev` is the persistent per-card state. It includes command URBs/buffers, audio stream arrays, panic flags, control state, optional input device, rawmidi and PCM handles, and product strings.

## Dependencies and Integration Points
Includes `../usbaudio.h`, embedding the generic `snd_usb_audio` as the first field. Used by every CAIAQ source file.

## Risks
The struct is large and cross-module; lifetime is tied to ALSA card private data. Arrays are sized by `MAX_STREAMS` and require runtime validation before indexing. Optional input fields exist only under config guard, so code must keep guards aligned.

## Test Signals
Compile CAIAQ with input enabled/disabled and run probe tests that verify spec-derived stream counts stay within `MAX_STREAMS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/input.c -->
# sources/distributed-fs/ceph-client/sound/usb/caiaq/input.c

## Purpose
Implements optional Linux input-device support for CAIAQ controllers: buttons, analog pots/faders, endless rotary encoders, jog wheels, Maschine pads, and product-specific event packet parsing.

## Important APIs, Types, and Functions
Public functions are `snd_usb_caiaq_input_init()`, `snd_usb_caiaq_input_dispatch()`, `snd_usb_caiaq_input_disconnect()`, and `snd_usb_caiaq_input_free()`. Important helpers are `decode_erp()`, `snd_caiaq_input_read_analog()`, `snd_caiaq_input_read_erp()`, `snd_caiaq_input_read_io()`, `snd_usb_caiaq_tks4_dispatch()`, `snd_usb_caiaq_maschine_dispatch()`, `snd_usb_caiaq_ep4_reply_dispatch()`, and input open/close callbacks.

## Control Flow
Initialization allocates an input device, fills name/phys/id, selects capabilities by USB product id, copies or generates keycodes, sets absolute axis ranges, configures automatic EP1 event messages, and for Traktor Kontrol X1/S4/Maschine allocates and configures an EP4 bulk input URB. Input open submits EP4 URB for products that need it; close kills it. EP1 replies are dispatched by `device.c` to `snd_usb_caiaq_input_dispatch()`, which routes analog, ERP, or IO messages. EP4 completion parses product-specific bulk packets, reports events, and resubmits the URB.

## State and Persistence
State persists in `snd_usb_caiaqdev`: `input_dev`, physical path, keycode array, EP4 URB, and EP4 buffer. Runtime event state is reported to the Linux input core, not stored beyond current buffers.

## Dependencies and Integration Points
Depends on Linux input core, USB input id helpers, CAIAQ command helpers, and product ids/spec in `device.h`. Built only when `CONFIG_SND_USB_CAIAQ_INPUT` is enabled.

## Risks
Many parsers assume minimum packet lengths only in some paths; EP1 analog/ERP/IO dispatch has limited length validation before per-product offset reads. In Maschine init, `input->absbit[0] |= MASCHINE_PAD(i)` appears to OR a code value rather than a bit mask, which deserves scrutiny. EP4 URB free occurs in `input_free()` after unregister; disconnect kills URB first. Input unregister sets core ownership expectations, so `input_dev` pointer handling must avoid double free.

## Test Signals
Test each supported input product, EP1 auto messages, EP4 open/close/requeue, short packet handling, keycode tables, ERP wraparound decode, S4 block ids, Maschine pad pressure reports, and config-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/input.h -->
# sources/distributed-fs/ceph-client/sound/usb/caiaq/input.h

## Purpose
Declares optional CAIAQ Linux input support hooks.

## Important APIs, Types, and Functions
Provides `snd_usb_caiaq_input_dispatch()`, `snd_usb_caiaq_input_init()`, `snd_usb_caiaq_input_disconnect()`, and `snd_usb_caiaq_input_free()`.

## Control Flow
No executable logic. `device.c` calls these only under `CONFIG_SND_USB_CAIAQ_INPUT`.

## State and Persistence
No header-owned state.

## Dependencies and Integration Points
Requires `struct snd_usb_caiaqdev` from `device.h`. Tied to CAIAQ Makefile and Kconfig input option.

## Risks
Callers must keep init/disconnect/free order correct when input is compiled in. Header lacks a trailing comment on `#endif`, but functional impact is none.

## Test Signals
Build with input enabled and disabled; runtime input device registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/input.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/midi.c -->
# sources/distributed-fs/ceph-client/sound/usb/caiaq/midi.c

## Purpose
Implements CAIAQ rawmidi support over the EP1 command channel and the preconfigured MIDI output URB.

## Important APIs, Types, and Functions
Public functions are `snd_usb_caiaq_midi_init()`, `snd_usb_caiaq_midi_handle_input()`, and `snd_usb_caiaq_midi_output_done()`. ALSA callbacks include MIDI input/output open/close/trigger and private helper `snd_usb_caiaq_midi_send()`.

## Control Flow
Initialization creates a rawmidi device with port counts from device spec, names it, assigns duplex flags and stream ops when ports exist, and stores the handle. Output trigger records the active output substream and sends immediately if no output URB is active. Send builds an EP1 MIDI_WRITE packet with port zero and length byte, pulls rawmidi bytes into the buffer, submits the pre-initialized `midi_out_urb`, and marks it active. Completion clears active state and sends the next packet if the substream is still active. Input is delivered by `device.c` EP1 reply dispatch and passed to `snd_rawmidi_receive()`.

## State and Persistence
Uses `snd_usb_caiaqdev` fields: `rmidi`, active rawmidi substream pointers, `midi_out_buf`, `midi_out_urb`, and `midi_out_active`.

## Dependencies and Integration Points
Depends on ALSA rawmidi and `device.c` command/URB setup. MIDI input is multiplexed on EP1 with control and input messages.

## Risks
No spinlock protects active substream pointers or `midi_out_active`; trigger, completion, close, and disconnect can race. The `port` argument for input is ignored, and output always uses port 0. Submit failure logs but leaves `midi_out_active` false.

## Test Signals
Test MIDI in/out for devices with different port counts, chained output completions, close while output active, disconnect during URB completion, and multi-port behavior if hardware exposes more than one port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/midi.h -->
# sources/distributed-fs/ceph-client/sound/usb/caiaq/midi.h

## Purpose
Declares CAIAQ rawmidi initialization and data callbacks.

## Important APIs, Types, and Functions
Provides `snd_usb_caiaq_midi_init()`, `snd_usb_caiaq_midi_handle_input()`, and `snd_usb_caiaq_midi_output_done()`.

## Control Flow
No executable logic. `device.c` calls init and uses output completion callback in the MIDI output URB.

## State and Persistence
No header-owned state.

## Dependencies and Integration Points
Requires `struct snd_usb_caiaqdev` and `struct urb` declarations from included compilation context.

## Risks
Only minimal prototypes are exposed; lifecycle cleanup is implicit through card teardown and URB kill in `device.c`.

## Test Signals
Build and rawmidi enumeration after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/caiaq/midi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/card.c -->
# sources/distributed-fs/ceph-client/sound/usb/card.c

## Purpose
Main generic ALSA USB Audio driver entry point. It owns module parameters, card creation and naming, interface aggregation, stream/mixer/MIDI creation, quirk aliasing, platform offload hooks, disconnect, shutdown locking, autosuspend, and PM suspend/resume.

## Important APIs, Types, and Functions
Exported platform/offload APIs are `snd_usb_register_platform_ops()`, `snd_usb_unregister_platform_ops()`, `snd_usb_rediscover_devices()`, and `snd_usb_find_suppported_substream()`. Shutdown/power APIs are `snd_usb_lock_shutdown()`, `snd_usb_unlock_shutdown()`, `snd_usb_autoresume()`, and `snd_usb_autosuspend()`. Core internals include `usb_audio_probe()`, `usb_audio_disconnect()`, `__usb_audio_disconnect()`, `snd_usb_audio_create()`, `snd_usb_create_streams()`, `snd_usb_create_stream()`, `try_to_register_card()`, `find_last_interface()`, `get_alias_id()`, `get_alias_quirk()`, `usb_audio_suspend()`, and `usb_audio_resume()`.

## Control Flow
Probe applies quirk aliases and boot quirks, then under `register_mutex` either finds an existing chip for the USB device or allocates a new ALSA card slot matching module vid/pid/enable filters. New chips initialize lists, flags, names, proc entries, and card private free. Probe claims/creates quirk-specific interfaces when required, otherwise parses normal UAC v1/v2/v3 control descriptors to discover audio streaming and MIDI interfaces, creates mixers, optionally delays card registration until the last matching interface, stores intfdata, increments interface count, and calls platform connect callbacks.

Stream creation handles MIDI streaming interfaces via `snd_usb_midi_v2_create()` and audio streaming interfaces via `snd_usb_parse_audio_interface()`, claiming unused interfaces for the USB audio driver. UAC v1 uses `baInterfaceNr[]`; UAC v2/v3 uses interface association descriptors and validates UAC3 BADD profile. Disconnect uses `shutdown` and `usage_count` to wait for protected tasks, disconnects ALSA, releases PCM endpoints, MIDI, media, and mixers, decrements interface count, and frees the card only after the final interface disappears. Suspend/resume fan out to PCM, endpoint, MIDI, mixer, MIDI2, media/platform hooks, and ALSA power state.

## State and Persistence
Global arrays and parameters persist module-wide: `usb_chip[]`, module card indexes/ids/enables, vid/pid filters, device setup, quirk alias/delayed-register/implicit-feedback flags, and platform ops. Per-card `struct snd_usb_audio` persists in card private data and owns lists of PCM streams, endpoints, interface refs, clock refs, MIDI devices, MIDI2 devices, and mixers, plus active/shutdown/usage counters and PM state.

## Dependencies and Integration Points
Integrates most of the generic USB audio subtree: `stream.c`, `format.c`, `pcm.c`, `endpoint.c`, `mixer.c`, `midi.c`, `midi2.c`, `quirks.c`, `proc.c`, `media.c`, and `power.c`. Exposes platform ops for audio offload users such as Qualcomm sideband drivers. Uses `quirks-table.h` in the USB id table.

## Risks
Probe/disconnect are multi-interface and heavily stateful; refcount, `num_interfaces`, and delayed registration bugs can expose partial cards or free too early. `platform_ops` callbacks run under `register_mutex` in several paths and must avoid deadlocks. Module quirk parameters can alter device behavior at runtime. Shutdown locking depends on all long operations using `snd_usb_lock_shutdown()`. UAC descriptor parsing is security-sensitive because it processes device-supplied descriptors.

## Test Signals
Test UAC1/UAC2/UAC3 devices, MIDI-only interfaces, quirked devices, delayed register option, quirk alias option, multiple control interfaces, disconnect during PCM/MIDI/mixer operations, autosuspend/resume, system suspend/resume, platform ops registration/rediscovery, media-controller sharing, and malformed descriptor validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/card.c -->
