# subset-b-006362 FireWire MOTU/OXFW/TASCAM and HDA build research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-pcm.c -->
# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-pcm.c

## Purpose

This file exposes MOTU FireWire devices as one ALSA PCM device with one playback and one capture substream. It translates model-specific packet-format caches into PCM hardware constraints, coordinates duplex stream reservation/start/stop, and binds ALSA callbacks to the MOTU AMDTP streams.

## Important APIs, types, and functions

`snd_motu_create_pcm_devices()` creates the ALSA PCM, marks it nonatomic, installs capture/playback ops, and uses VMALLOC buffers. `motu_rate_constraint()` and `motu_channels_constraint()` keep rate/channel choices consistent with `snd_motu_packet_format.pcm_chunks`. `init_hw_info()` selects `tx_stream` for capture and `rx_stream` for playback, configures S32 samples, adds MOTU-specific AMDTP constraints, and uses cached packet formats.

## Control flow

`pcm_open()` first takes the device stream lock, refreshes packet formats, initializes runtime hardware limits, reads the clock source, and restricts rate/period/buffer to current values when externally clocked or already reserved. `pcm_hw_params()` reserves the duplex domain and increments `substreams_counter`; `pcm_hw_free()` decrements it and stops/free resources when the last substream leaves. Prepare starts duplex streaming, trigger only attaches or detaches the ALSA substream, and pointer/ack delegate to the shared AMDTP domain.

## State and persistence behavior

The file mutates `substreams_counter`, runtime hardware constraints, and AMDTP PCM trigger state. Long-lived state is in `struct snd_motu`, especially cached formats and domain period/buffer sizing.

## Dependencies and integration points

It depends on `motu.h`, protocol dispatchers, `motu-stream.c`, and `amdtp-motu` helpers. ALSA PCM state is synchronized with the hwdep lock notifications produced by `snd_motu_stream_lock_try/release()`.

## Risks and test signals

The main risks are incorrect channel/rate constraints when optical interface state changes, counter imbalance on error paths, and deadlocks between ALSA open/close and stream mutex paths. Test signals include opening capture/playback in both orders, externally clocked operation, simultaneous duplex use, period/buffer locking, xrun recovery, and changing sample rates between opens.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-proc.c -->
# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-proc.c

## Purpose

This file adds `/proc/asound/.../firewire` information nodes for MOTU devices. It provides human-readable clock and packet-format diagnostics for users, developers, and regression triage.

## Important APIs, types, and functions

`snd_motu_proc_init()` creates a `firewire` directory under the ALSA card proc root. `proc_read_clock()` reports the current sample rate and decoded clock source using protocol-version helpers. `proc_read_format()` refreshes packet formats and prints message chunks, fixed chunks, and total PCM chunks per supported rate for transmit and receive directions. `clock_names[]` maps `enum snd_motu_clock_source` values to display strings.

## Control flow

Proc reads are best-effort: if any FireWire transaction or protocol parser fails, the callback returns without printing partial fallback data. Format output iterates all six MOTU clock rates and maps each rate to one of the three packet modes by `mode = i >> 1`.

## State and persistence behavior

The proc callbacks do not persist proc-local state, but `proc_read_format()` refreshes `motu->tx_packet_formats` and `motu->rx_packet_formats`, so reading the file can update cached packet-format state.

## Dependencies and integration points

It integrates with ALSA info entries, `motu.h`, and the version-specific protocol cache and clock functions. It depends on `motu->spec` fixed chunk arrays and cached dynamic packet formats.

## Risks and test signals

Risks include stale or failed hardware reads producing empty proc files and user-visible confusion if `clock_names` diverges from protocol enums. Useful tests are proc reads while idle, while streaming, after optical interface changes, and after bus reset.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-protocol-v1.c -->
# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-protocol-v1.c

## Purpose

This file implements MOTU protocol version 1 support for original 828 and 896 models. It decodes their distinct clock/status registers, controls frame fetching/output, detects packet formats, and defines the two v1 model specs.

## Important APIs, types, and functions

Exports include `snd_motu_protocol_v1_get_clock_rate()`, `set_clock_rate()`, `get_clock_source()`, `switch_fetching_mode()`, and `cache_packet_formats()`. 828 helpers operate on `CLK_828_STATUS_OFFSET` and support only 44.1/48 kHz. 896 helpers operate on `CLK_896_STATUS_OFFSET` and support up to 96 kHz. `snd_motu_spec_828` and `snd_motu_spec_896` provide fixed chunk defaults.

## Control flow

Public entry points dispatch by comparing `motu->spec` to the exact model spec. Read paths issue MOTU transactions, convert big-endian registers, and decode bitfields into generic clock enums. Write paths read-modify-write only the relevant bits. Fetching mode for 828 includes a 100 ms delay before enabling PCM frame fetch and output because the device can mute until packets arrive.

## State and persistence behavior

Persistent hardware state is in MOTU registers under `0xfffff0000000`. Driver state updated here is limited to packet-format caches. Packet format detection starts from fixed chunks and adds optical ADAT channels when register state or model assumptions require it.

## Dependencies and integration points

It depends on `snd_motu_transaction_read/write()`, the common rate table, and `motu-stream.c` start/finish sequencing. ALSA constraints in `motu-pcm.c` depend on the cached chunks produced here.

## Risks and test signals

Risks include undocumented register-bit interpretation, device-specific delays, and spec pointer dispatch missing future v1-compatible devices. Test signals are clock-rate changes per model, optical S/PDIF versus ADAT format changes, 828 output unmute behavior, and error handling on invalid register encodings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-protocol-v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-protocol-v2.c -->
# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-protocol-v2.c

## Purpose

This file implements MOTU protocol version 2 for 828mk2, 896HD, Traveler, UltraLite, and 8pre. It handles the shared v2 clock register, optical interface configuration, model-specific frame fetching bits, packet-format detection, and model spec definitions.

## Important APIs, types, and functions

The exported v2 protocol functions implement clock get/set/source, fetching-mode switching, and packet-format caching. `get_clock_rate()` decodes the clock-rate index into `snd_motu_clock_rates`. `get_clock_source()` maps hardware source bits into generic clock enums and consults the I/O configuration register for S/PDIF-on-optical detection. `switch_fetching_mode_cyclone()` and `switch_fetching_mode_spartan()` encode FPGA-family quirks.

## Control flow

Set-rate searches the common rate table, read-modify-writes `V2_CLOCK_STATUS_OFFSET`, and rejects unknown rates. Fetching mode is a no-op for 828mk2 and 896HD but updates `V2_CLOCK_FETCH_ENABLE` and sometimes `V2_CLOCK_MODEL_SPECIFIC` for Traveler/UltraLite/8pre. Packet-format caching reads `V2_IN_OUT_CONF_OFFSET`, copies fixed chunks, and adds ADAT-derived chunks depending on enabled input/output optical modes.

## State and persistence behavior

The file writes persistent hardware clock/fetch bits and refreshes in-memory packet-format caches. It does not own allocation or ALSA state.

## Dependencies and integration points

It is called through inline dispatchers in `motu.h` from PCM open, stream reserve/start, and proc reads. Register access is through `motu-transaction.c`; output constraints depend on the cached chunk arrays.

## Risks and test signals

Risks include hardware-family quirks being underdocumented, S/PDIF source ambiguity, and incorrect chunk additions for the dual-optical 8pre. Tests should cover each model spec, all supported rates, optical ADAT/S/PDIF transitions, external clock sources, and fetching-mode behavior at double-rate SPH.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-protocol-v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-protocol-v3.c -->
# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-protocol-v3.c

## Purpose

This file implements MOTU protocol version 3 for mk3/Hybrid/Audio Express/Track16/4pre models. It manages clock rate/source, waits for asynchronous clock-change notification, controls frame fetching, handles optical-interface-dependent packet formats, and declares v3 model specs.

## Important APIs, types, and functions

Exports mirror the protocol interface in `motu.h`: clock get/set/source, fetching switch, and packet-format cache. `snd_motu_protocol_v3_set_clock_rate()` writes the clock index and clears fetch mode before waiting up to four seconds for `V3_MSG_FLAG_CLK_CHANGED` on `hwdep_wait`. `detect_packet_formats_with_opt_ifaces()` adds ADAT or S/PDIF chunk counts for enabled optical interfaces.

## Control flow

Clock source decoding reads `V3_CLOCK_STATUS_OFFSET`; optical A/B sources require a second read of `V3_OPT_IFACE_MODE_OFFSET` to distinguish ADAT from S/PDIF. Fetching mode simply toggles `V3_FETCH_PCM_FRAMES`. Packet-format caching copies model fixed chunks, reads optical mode, and applies dynamic additions only for models with optical-dependent layouts.

## State and persistence behavior

The file writes clock/fetch registers and uses `motu->msg` as a transient notification latch. Packet-format cache mutations persist in `motu->tx_packet_formats` and `rx_packet_formats` until refreshed.

## Dependencies and integration points

It depends on MOTU transaction helpers, async message delivery in `motu-transaction.c`, wait queues in `struct snd_motu`, and stream startup in `motu-stream.c`. Command-DSP/register-DSP parser initialization in stream startup depends on model flags defined here.

## Risks and test signals

Risks include timeout or missed wakeup during clock changes, ambiguous unknown clock sources, and incorrect optical chunk math for hybrid models. Tests should exercise rate changes, bus-reset recovery after a pending wait, packet-format cache after optical mode changes, and all listed model specs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-protocol-v3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-register-dsp-message-parser.c -->
# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-register-dsp-message-parser.c

## Purpose

This file parses register-DSP status messages embedded in MOTU isochronous packets. It maintains cached meter/parameter state and queues change events for hwdep clients for models whose DSP controls are exposed through asynchronous register access.

## Important APIs, types, and functions

`snd_motu_register_dsp_message_parser_new()` allocates parser state and records 4pre/Audio Express meter-position quirks. `snd_motu_register_dsp_message_parser_init()` resets sequencing state at stream start. `snd_motu_register_dsp_message_parser_parse()` scans packet descriptors and updates mixer, output, line input, input, and meter caches. Copy/count/event functions expose snapshots and queued events to other MOTU UAPI code.

## Control flow

The parser locks its private spinlock, iterates packets then data blocks, derives `msg_type` and `val` from fixed byte offsets, and uses previous-message state to infer channel indexes for message series. When a cached parameter changes, `queue_event()` pushes a compact 32-bit event and wakes `hwdep_wait`. Meter messages update meter bytes but intentionally do not alter previous-message sequencing.

## State and persistence behavior

`struct msg_parser` persists meter data, parameter snapshots, inferred channel cursors, previous message type, and a 16-entry circular event queue. The queue is explicitly described as rough and has no overrun check, so old events can be overwritten.

## Dependencies and integration points

It depends on MOTU AMDTP packet layout, `struct pkt_desc`, model flags, and UAPI structures under `sound/firewire.h`. It is initialized from `motu-stream.c` before domain start and consumed by hwdep paths elsewhere in the MOTU driver.

## Risks and test signals

Risks include queue overrun, byte-offset quirks, inferred channel desynchronization after packet loss, and event loss when no hwdep client is open. Useful tests are high-rate meter streams, rapid mixer-control changes, 4pre/Audio Express layout validation, and concurrent snapshot/event reads while streaming.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-register-dsp-message-parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-stream.c -->
# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-stream.c

## Purpose

This file owns MOTU duplex isochronous streaming. It initializes AMDTP streams/resources, reserves channels and bandwidth, programs MOTU streaming registers, starts/stops the shared AMDTP domain, handles bus-generation updates, and exposes stream locks for ALSA/hwdep coordination.

## Important APIs, types, and functions

Public functions include `snd_motu_stream_init_duplex()`, `cache_packet_formats()`, `reserve_duplex()`, `start_duplex()`, `stop_duplex()`, `destroy_duplex()`, `lock_try()`, and `lock_release()`. Helpers program `ISOC_COMM_CONTROL_OFFSET` and `PACKET_FORMAT_OFFSET`, allocate resources in `keep_resources()`, and call `amdtp_motu_set_parameters()`.

## Control flow

Reserve stops active streaming when the first substream opens or rate changes, frees resources, sets hardware clock rate, refreshes packet formats, allocates tx/rx resources, sets domain period sizing, and allocates the MOTU cache ring. Start updates resources after bus reset, writes packet format flags, initializes DSP parsers when needed, registers tx/rx channels with the device, adds both streams to the AMDTP domain, initializes cache cursors, starts the domain, waits readiness, then enables device frame fetching. Stop tears all of that down only when the substream count reaches zero.

## State and persistence behavior

Persistent state includes FireWire resource reservations, hardware communication register state, AMDTP domain state, `cache.event_offsets`, and stream lock counters. `dev_lock_count < 0` is the user-space exclusive lock state; positive counts mean kernel PCM/MIDI users.

## Dependencies and integration points

It integrates `motu-transaction.c`, protocol dispatchers, `amdtp-motu`, `fw_iso_resources`, and ALSA PCM/MIDI callers. `motu_bus_update()` re-registers transactions; stream startup separately updates resource generations.

## Risks and test signals

Risks include partial resource allocation cleanup, cache allocation sizing, start-order sensitivity, and fetch-mode failures leaving hardware active. Test signals include bus reset during streaming, rate-change reopen, no-substream stop, external clock use, DSP parser init failures, and generation mismatch recovery.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-transaction.c -->
# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-transaction.c

## Purpose

This file centralizes MOTU asynchronous FireWire register access and inbound notification address registration. It abstracts the MOTU register aperture and publishes a local address that the device writes when status changes occur.

## Important APIs, types, and functions

`snd_motu_transaction_read()` and `snd_motu_transaction_write()` validate quadlet alignment and choose quadlet versus block transaction TCODEs against `SND_MOTU_ADDR_BASE`. `snd_motu_transaction_register()` installs a four-byte `fw_address_handler`. `snd_motu_transaction_reregister()` writes the handler address into MOTU `ASYNC_ADDR_HI/LO`. `handle_message()` stores inbound quadlet messages in `motu->msg`.

## Control flow

Registration configures the handler, adds it in the high response address region, then writes the address to the device; failures remove the handler. Inbound writes are accepted only for a quadlet at the registered offset. The callback stores the big-endian payload under `motu->lock`, responds complete, and wakes `hwdep_wait`. Unregister removes the handler and writes zeroes to the device address registers.

## State and persistence behavior

Persistent hardware state is the device's async callback address. Driver state includes `async_handler`, the last `msg`, and wait-queue wakeups. Bus resets clear device-side registers, so `snd_motu_transaction_reregister()` is called from the driver update callback.

## Dependencies and integration points

It depends on FireWire core address handlers and `snd_fw_transaction()`. Protocol v3 clock waits and hwdep event reads rely on `motu->msg` updates.

## Risks and test signals

Risks include stale handler addresses after bus reset, accepting unexpected tcode/lengths, and unregister writes racing with disconnect. Tests should cover probe/register failure paths, bus reset re-registration, v3 clock notification wakeups, and removal while clients are blocked in hwdep read.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-transaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu.c -->
# sources/distributed-fs/ceph-client/sound/firewire/motu/motu.c

## Purpose

This is the MOTU FireWire ALSA driver entry point. It matches supported MOTU models, allocates and names ALSA cards, wires together transaction, streaming, proc, PCM, MIDI, hwdep, and DSP parser components, and registers the FireWire driver.

## Important APIs, types, and functions

`motu_probe()` is the central constructor. `motu_card_free()` is the card private cleanup hook. `motu_bus_update()` re-registers async message addresses after bus reset. `motu_id_table[]` maps MOTU version IDs to `snd_motu_spec` objects. `snd_motu_clock_rates[]` is the shared six-entry rate table used across protocol and PCM logic.

## Control flow

Probe creates the card, initializes `struct snd_motu`, names the card from config ROM data, registers async transactions, initializes duplex streams, creates proc/PCM/MIDI/hwdep devices, optionally creates register-DSP or command-DSP parser state, and finally registers the card. Any failure releases the card, which invokes cleanup. Remove only calls `snd_card_free()` so ALSA character devices can drain before final teardown.

## State and persistence behavior

The file establishes long-lived `struct snd_motu` state: unit reference, spec pointer, locks, wait queue, card pointer, and model flags. It does not persist data outside kernel runtime.

## Dependencies and integration points

It binds Linux FireWire core to ALSA. It depends on all MOTU submodules declared in `motu.h`, and the device ID table selects protocol behavior indirectly via model specs.

## Risks and test signals

Risks include probe-order cleanup regressions, missing MIDI creation for flag combinations, and model ID/spec mismatches. Test signals are probe/remove for every ID, failed intermediate allocations, bus reset, card naming from config ROM, and module load/unload.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu.h -->
# sources/distributed-fs/ceph-client/sound/firewire/motu/motu.h

## Purpose

This header defines the shared MOTU driver model: central device state, packet format descriptions, cache state, model specs, clock/protocol enums, submodule prototypes, and inline dispatchers from generic protocol calls to version-specific implementations.

## Important APIs, types, and functions

Key types are `struct snd_motu`, `struct snd_motu_packet_format`, `struct amdtp_motu_cache`, and `struct snd_motu_spec`. Flags describe MIDI byte positions and DSP parser style. `enum snd_motu_clock_source` normalizes clock source variants across models. Inline helpers `snd_motu_protocol_get_clock_rate/set_clock_rate/get_clock_source/switch_fetching_mode/cache_packet_formats()` dispatch on `spec->protocol_version`.

## Control flow

The inline dispatchers route v2 first, v3 second, and otherwise v1. This makes `spec->protocol_version` the controlling switch for PCM, stream, and proc users. The header also declares external spec objects for all supported models so the FireWire ID table can bind devices to behavior.

## State and persistence behavior

`struct snd_motu` stores all runtime state: ALSA card/unit references, locks, stream resources, substream count, async handler, hwdep lock state, AMDTP domain, cache ring, and DSP parser pointer. No static persistent state is created here.

## Dependencies and integration points

It includes Linux FireWire, ALSA core/control/PCM/rawmidi/hwdep/info, and common FireWire AMDTP/iso-resource helpers. All MOTU `.c` files include this header as their internal contract.

## Risks and test signals

Risks include ABI drift with UAPI DSP structures, incorrect dispatch defaults, and field lifetime assumptions across modules. Compile coverage is important because this header wires many submodules; runtime signals include lock state transitions, stream counter correctness, and protocol dispatch per model.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/Makefile -->
# sources/distributed-fs/ceph-client/sound/firewire/oxfw/Makefile

## Purpose

This Makefile builds the OXFW970/971 ALSA FireWire driver object from its component sources and ties it to `CONFIG_SND_OXFW`.

## Important APIs, types, and functions

`snd-oxfw-y` lists the linked objects: command, stream, PCM, proc, MIDI, hwdep, speaker controls, SCS.1x support, and driver core. `obj-$(CONFIG_SND_OXFW) += snd-oxfw.o` exposes the final module/built-in object to Kbuild.

## Control flow

Kbuild evaluates the config symbol and either builds `snd-oxfw.o` from all listed objects or skips it. Link order places the core object last but all entries are part of one composite module.

## State and persistence behavior

The file has no runtime state. Its persistent effect is build graph membership.

## Dependencies and integration points

It integrates with the parent sound/firewire Kbuild and the `SND_OXFW` Kconfig option defined elsewhere.

## Risks and test signals

Risks are missing new source files from the object list or stale object names after refactors. Test signals are `make M=sound/firewire/oxfw`, full kernel builds with `SND_OXFW=m/y`, and module symbol resolution.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-command.c -->
# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-command.c

## Purpose

This file implements AV/C/FCP command helpers used by OXFW devices for stream format configuration and signal-format probing.

## Important APIs, types, and functions

`avc_stream_set_format()` sends Extended Stream Format Information CONTROL/SINGLE commands. `avc_stream_get_format()` sends STATUS/SINGLE or STATUS/LIST commands and strips the AV/C header before returning stream format bytes. `avc_general_inquiry_sig_fmt()` uses SPECIFIC INQUIRY for input/output plug signal format at a candidate sample rate.

## Control flow

Set-format allocates a command buffer, writes AV/C operands, appends format bytes, uses `fcp_avc_transaction()`, validates response length/status, maps NOT IMPLEMENTED to `-ENXIO` and REJECTED to `-EINVAL`, and frees the buffer. Get-format chooses SINGLE for `eid == 0xff` and LIST otherwise, validates response identity, handles IN TRANSITION as `-EAGAIN`, verifies LIST entry IDs, then `memmove()`s payload bytes to the caller buffer.

## State and persistence behavior

No driver-local state persists here. Successful CONTROL commands modify device stream-format state; inquiries are read-only.

## Dependencies and integration points

It depends on `fcp_avc_transaction()`, AV/C plug direction enums, `amdtp_rate_table`, and constants from `oxfw.h`. `oxfw-stream.c` uses these helpers for discovery, reserve, and assumed-format probing.

## Risks and test signals

Risks include short responses, devices returning transitional statuses, header validation mismatches, and unsupported LIST handling. Tests should include real devices with LIST and SINGLE only behavior, unsupported Miglia-style devices, all rate inquiries, and malformed/short FCP responses.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-command.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-hwdep.c -->
# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-hwdep.c

## Purpose

This file exposes the OXFW hwdep device for user-space FireWire metadata, stream lock control, and lock-status notifications.

## Important APIs, types, and functions

`snd_oxfw_create_hwdep()` creates an exclusive hwdep with `SNDRV_HWDEP_IFACE_FW_OXFW`. `hwdep_read()` blocks until `dev_lock_changed`, then returns `SNDRV_FIREWIRE_EVENT_LOCK_STATUS`. `hwdep_poll()` reports readable state. Ioctls implement `GET_INFO`, `LOCK`, and `UNLOCK`, with compat forwarding through `compat_ptr()`.

## Control flow

Read waits on `hwdep_wait` with interruptible sleep under the spinlock protocol, then clears `dev_lock_changed` and copies the event to user space. Lock sets `dev_lock_count` to `-1` only when no kernel stream users exist; unlock restores zero only from `-1`. Release clears a user lock if the file closes while locked.

## State and persistence behavior

The file mutates `dev_lock_count` and `dev_lock_changed` in `struct snd_oxfw`. Negative lock count is the persistent user lock until unlock or release.

## Dependencies and integration points

It is paired with `snd_oxfw_stream_lock_try/release()` in `oxfw-stream.c`, which toggles lock notifications for PCM/MIDI users. User-space tools consume `sound/firewire.h` UAPI structures.

## Risks and test signals

Risks include lost wakeups, stale user locks on release, and lock semantics racing with PCM open. Test signals include poll/read around PCM open/close, ioctl lock excluding ALSA streams, compat ioctl, signal interruption, and disconnect while blocked in read.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-hwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-midi.c -->
# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-midi.c

## Purpose

This file creates standard ALSA RawMIDI ports for OXFW devices whose AM824 stream formats advertise MIDI channels. MIDI bytes are transported inside the same duplex AMDTP streams as audio.

## Important APIs, types, and functions

`snd_oxfw_create_midi()` allocates a RawMIDI device according to `midi_input_ports` and `midi_output_ports`. Open callbacks reserve and start duplex streaming with current stream parameters. Trigger callbacks call `amdtp_am824_midi_trigger()` on the transmit or receive stream with the substream number.

## Control flow

Capture/playback open first take the stream lock, reserve duplex resources at current rate/format, increment `substreams_count`, and start the domain. Close decrements the count, stops the domain if this was the last user, and releases the stream lock. Trigger just attaches or detaches the RawMIDI substream under the driver spinlock.

## State and persistence behavior

This file mutates `substreams_count`, stream lock state, and AM824 MIDI substream pointers. RawMIDI port names persist for the ALSA card lifetime.

## Dependencies and integration points

It depends on format discovery in `oxfw-stream.c`, AM824 MIDI helper routines, and ALSA RawMIDI core. It shares stream reservation with PCM users, so counters and lock semantics must match `oxfw-pcm.c`.

## Risks and test signals

Risks include counter imbalance when start fails, MIDI-only opens forcing audio resources, and mismatched port counts from malformed stream formats. Test signals include MIDI-only capture/playback, duplex MIDI plus PCM, trigger start/stop without close, and disconnect/bus reset during active MIDI.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-pcm.c -->
# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-pcm.c

## Purpose

This file exposes OXFW devices as ALSA PCM streams and converts discovered AV/C stream formats into ALSA hardware constraints.

## Important APIs, types, and functions

`snd_oxfw_create_pcm()` creates playback and optional capture streams. `hw_rule_rate()` and `hw_rule_channels()` constrain valid rate/channel pairs from stream-format arrays. `init_hw_params()` selects AM824 sample format bits and adds AM824 constraints. Capture maps to `tx_stream`; playback maps to `rx_stream`.

## Control flow

Open takes the stream lock, initializes runtime constraints, and if streams are already reserved, limits the new substream to the current formation and domain period/buffer size. `pcm_capture_hw_params()` and `pcm_playback_hw_params()` reserve the duplex stream with selected rate/channels and increment `substreams_count`. Prepare starts duplex streaming and prepares the corresponding AMDTP stream. Trigger attaches/detaches substreams; pointer/ack delegate to the domain.

## State and persistence behavior

The file updates ALSA runtime constraints, `substreams_count`, and AM824 PCM trigger state. Stream formats themselves were discovered earlier and stored in `struct snd_oxfw`.

## Dependencies and integration points

It depends on `oxfw-stream.c` formation parsing/reservation, AM824 helpers, and the hwdep lock model. It is sensitive to `has_output`, because some devices only support playback to the device.

## Risks and test signals

Risks include invalid interval lists, no format entries leaving min/max at sentinel values, and capture availability confusion when `has_output` is false. Tests should cover all advertised formations, simultaneous PCM directions, rate/channel changes, MIDI coexistence, and devices with playback-only or assumed formats.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-proc.c -->
# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-proc.c

## Purpose

This file adds a proc diagnostic node showing OXFW input/output stream formations and marking the currently active formation.

## Important APIs, types, and functions

`snd_oxfw_proc_init()` creates the `firewire/formation` ALSA info entry. `proc_read_formation()` reads the current input formation, iterates `rx_stream_formats`, and optionally repeats the process for output using `tx_stream_formats`. `add_node()` is a small info-entry helper.

## Control flow

The proc callback first reports "Input Stream to device" using `AVC_GENERAL_PLUG_DIR_IN`. If `has_output` is false it returns early. Otherwise it reports "Output Stream from device". Each row is parsed with `snd_oxfw_stream_parse_format()` and compared with the current formation using `memcmp()` to prefix an active row with `*`.

## State and persistence behavior

The file does not own durable state. Reads can trigger AV/C transactions through `snd_oxfw_stream_get_current_formation()`.

## Dependencies and integration points

It depends on OXFW stream discovery data and AV/C current-formation reads. The proc tree is removed automatically by ALSA card disconnect handling.

## Risks and test signals

Risks include empty output on transaction failure, misleading data if cached formats are stale, and `memcmp()` comparing padding if the formation structure changes. Test signals are proc output across all discovered formats, no-output devices, assumed-format devices, and active-format changes after PCM hw_params.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-scs1x.c -->
# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-scs1x.c

## Purpose

This file implements Stanton SCS.1x custom MIDI transport over unique HSS1394 asynchronous FireWire transactions, instead of standard AM824 MIDI channels.

## Important APIs, types, and functions

`struct fw_scs1x` stores address-handler state, input/output RawMIDI substreams, output transaction state, escaping state, and workqueue data. `snd_oxfw_scs1x_add()` registers the async handler, announces its address to the device, and creates a RawMIDI device. `handle_hss()` receives device writes. `scs_output_work()` packetizes RawMIDI bytes into device-specific HSS packets and sends block-write requests.

## Control flow

Incoming packets are converted either directly from user-data packets or escaped into vendor SysEx sequences. Outgoing data is pulled from RawMIDI, normalizes running status into full commands, handles escaped SysEx payloads, sends one FireWire block transaction at a time, and reschedules work from the transaction callback. Playback drain waits until `output_idle`.

## State and persistence behavior

The driver persists the local handler address in the device via a change-address packet. Output state includes current MIDI status, pending transaction bytes, error flag, and idle wait state. Bus reset calls `snd_oxfw_scs1x_update()` to re-register the address.

## Dependencies and integration points

It is enabled by OXFW quirks in `oxfw.c` and stores private state in `oxfw->spec`. It uses FireWire address handlers, raw transactions, workqueues, wait queues, and ALSA RawMIDI.

## Risks and test signals

Risks include MIDI parser edge cases, transaction error recovery, address stale after bus reset, and waiting forever in drain if idle is not signaled. Tests should cover SysEx escape round trips, running status, invalid real-time statuses, bus reset, permanent transaction errors, and capture/playback trigger toggles.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-scs1x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-spkr.c -->
# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-spkr.c

## Purpose

This file provides legacy ALSA mixer controls for Griffin FireWave and LaCie FireWire Speakers, preserving compatibility with older firewire-speaker behavior.

## Important APIs, types, and functions

`struct fw_spkr` caches mute, per-channel volume, min/max, channel count, and AV/C feature block IDs. `snd_oxfw_add_spkr()` allocates speaker state, reads min/max/current values from the device, and adds "PCM Playback Switch" and "PCM Playback Volume" controls. `avc_audio_feature_mute()` and `avc_audio_feature_volume()` implement AV/C feature function block transactions.

## Control flow

Control get callbacks return cached state. Put callbacks validate requested values, issue AV/C CONTROL transactions for changed mute or volume fields, and update the cache only on success. Volume writes optimize equal multi-channel values by writing master channel zero when possible, otherwise per-channel writes use a channel map that matches ALSA-visible order.

## State and persistence behavior

The cache in `oxfw->spec` persists for the ALSA card lifetime. Successful writes persist device mixer state. There is no notification path for out-of-band device changes.

## Dependencies and integration points

`oxfw.c` calls this during quirk detection for Griffin/LaCie IDs. It depends on `fcp_avc_transaction()` and ALSA control core.

## Risks and test signals

Risks include stale cached controls, channel-map mistakes, devices rejecting feature-block commands, and sign extension in 16-bit volume handling. Tests should read/write mute and volume on both models, validate channel ordering, reject out-of-range values, and handle short/failed FCP responses.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-spkr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-stream.c -->
# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-stream.c

## Purpose

This file discovers OXFW stream capabilities, parses AV/C AM824 stream formats, initializes CMP/AM824 streams, reserves resources, starts/stops the duplex AMDTP domain, and maintains stream locks.

## Important APIs, types, and functions

Exports include `snd_oxfw_stream_discover()`, `parse_format()`, `get_current_formation()`, `reserve_duplex()`, `start_duplex()`, `stop_duplex()`, `update_duplex()`, and lock helpers. `oxfw_rate_table[]` and `avc_stream_rate_table[]` translate between ALSA rates and AV/C FDF rate IDs. `fill_stream_formats()` reads LIST entries or falls back to `assume_stream_formats()`.

## Control flow

Discovery reads AV/C plug info, fills oPCR/iPCR format arrays, parses each format, and derives MIDI port counts. Reserve checks whether external software already owns CMP connections, compares requested formation with current formation, stops/breaks old connections when the formation changes, sets stream format, reserves CMP resources, and fixes domain period sizing. Start establishes CMP connections, adds streams to the domain, chooses skip-cycle/replay behavior by quirk, starts the domain, and waits ready. Bus reset stops the domain, breaks connections, and aborts PCM streams.

## State and persistence behavior

The file owns cached stream-format arrays, `has_input/has_output`, `assumed`, CMP connection state, AM824 stream state, `substreams_count`, and lock notifications. Device stream format and CMP plug state are persistent hardware-side until changed/reset.

## Dependencies and integration points

It depends on `oxfw-command.c`, `cmp`, AM824 helpers, FireWire generation tracking, and quirks from `oxfw.c`. PCM, MIDI, proc, and hwdep modules all rely on this stream contract.

## Risks and test signals

Risks include incorrect fallback assumptions, malformed format parsing, external CMP ownership conflicts, and quirk-specific SYT/DBC behavior. Test signals include LIST unsupported devices, all rate/channel entries, bus reset, JACK/FFADO coexistence, playback-only devices, jumbo payload devices, and voluntary recovery devices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw.c -->
# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw.c

## Purpose

This is the OXFW970/971 FireWire driver entry point. It matches device IDs, names ALSA cards, detects hardware/firmware quirks, discovers streams, initializes ALSA devices, and handles bus reset/remove.

## Important APIs, types, and functions

`oxfw_probe()` constructs `struct snd_oxfw` and orchestrates submodule setup. `detect_quirks()` applies model-specific behavior for Griffin, LaCie, Stanton, Apogee, TASCAM FireOne, Loud/Mackie, and Oxford/Miglia devices. `name_card()` reads CSR strings and OXFW firmware ID. `oxfw_id_table[]` encodes supported devices and aliases.

## Control flow

Probe filters generic Loud matches by model string, allocates the card, initializes locks/wait queues, names the card, applies special Miglia quirks, discovers stream formats, applies further quirks, initializes streams and PCM/proc/MIDI/hwdep if audio I/O exists, and registers the card. Bus reset resets FCP, updates streams under the mutex, and re-registers SCS.1x async address when needed. Remove frees the ALSA card.

## State and persistence behavior

This file initializes long-lived `struct snd_oxfw` state: unit, card, quirks, stream-format caches, MIDI port counts, and optional `spec` private data for speakers or SCS.1x. It does not persist outside kernel runtime.

## Dependencies and integration points

It integrates FireWire driver core, ALSA card lifecycle, OXFW stream/PCM/MIDI/hwdep/proc modules, speaker controls, and SCS.1x transactions. Kbuild composes these pieces via the OXFW Makefile.

## Risks and test signals

Risks include quirk mis-detection, probe cleanup ordering, stream discovery failures preventing useful control-only devices, and generic Loud matching false positives. Tests should probe every ID path, firmware-id quirk behavior, bus reset, remove during active streams, and module aliases.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw.h -->
# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw.h

## Purpose

This header is the internal contract for the OXFW driver. It defines device state, quirk flags, stream formation types, AV/C helper prototypes, stream/PCM/MIDI/hwdep/proc entry points, and model-specific extension hooks.

## Important APIs, types, and functions

`enum snd_oxfw_quirk` documents transport and device deviations such as jumbo payload, wrong DBS, blocking transmission, SCS transactions, NO_INFO handling, voluntary recovery, unsupported stream-format info, and unusual DBC semantics. `struct snd_oxfw` stores card/unit refs, locks, quirks, stream-format arrays, CMP connections, AMDTP streams, MIDI port counts, hwdep lock state, private `spec`, and domain.

## Control flow

The header does not execute logic except inline wrappers for single/list stream format queries. It establishes that OXFW code uses AV/C plug direction, format arrays capped at `SND_OXFW_STREAM_FORMAT_ENTRIES`, and a shared duplex stream API consumed by PCM and MIDI users.

## State and persistence behavior

All runtime OXFW state is centralized in `struct snd_oxfw`. Format arrays are devm-managed and persist for card lifetime; CMP and AM824 objects are initialized/destroyed by stream code.

## Dependencies and integration points

It includes ALSA control/core/PCM/info/rawmidi/firewire/hwdep and common FireWire libraries for FCP, packets buffer, iso resources, AM824, and CMP. Every OXFW source includes this header.

## Risks and test signals

Risks include quirk flag overlap, stale prototypes, and lifetime coupling around `spec`. Build tests catch most prototype drift; runtime tests should exercise each quirk family and ensure PCM/MIDI/hwdep modules agree on lock and stream counters.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/packets-buffer.c -->
# sources/distributed-fs/ceph-client/sound/firewire/packets-buffer.c

## Purpose

This shared helper allocates and destroys DMA-backed page buffers split into many fixed-size isochronous packet slots.

## Important APIs, types, and functions

`iso_packets_buffer_init()` allocates the packet descriptor array, aligns packet size to the L1 cache line, calculates packets per page and required pages, initializes a FireWire ISO buffer, and fills per-packet virtual buffer pointers and offsets. `iso_packets_buffer_destroy()` destroys the ISO buffer and frees descriptors. Both functions are exported for other FireWire sound modules.

## Control flow

Initialization fails with `-ENOMEM` on allocation failures and `-EINVAL` if aligned packet size exceeds a page. After successful `fw_iso_buffer_init()`, each packet index maps to a page plus an aligned offset. Error paths free only resources already acquired.

## State and persistence behavior

The persistent state is `struct iso_packets_buffer`: one `fw_iso_buffer` plus an array of packet descriptors. The caller owns lifecycle and must call destroy after successful init.

## Dependencies and integration points

It depends on Linux FireWire ISO buffer APIs, DMA direction, page mapping, and `kmalloc_objs()`. Consumers can submit packet offsets to FireWire ISO contexts.

## Risks and test signals

Risks include oversized packet sizes, offset arithmetic mistakes, resource leaks on partial failure, and cache-alignment assumptions wasting pages. Tests should cover several packet sizes/counts, DMA directions, failure injection for allocations, and destroy after init.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/packets-buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/packets-buffer.h -->
# sources/distributed-fs/ceph-client/sound/firewire/packets-buffer.h

## Purpose

This header declares the shared ISO packet buffer abstraction for FireWire sound drivers.

## Important APIs, types, and functions

`struct iso_packets_buffer` combines a FireWire `fw_iso_buffer` with an array of per-packet descriptors containing a CPU pointer and byte offset. It declares `iso_packets_buffer_init()` and `iso_packets_buffer_destroy()`.

## Control flow

There is no executable control flow in this header. It defines the lifecycle contract: initialize with a unit, count, maximum packet size, and DMA direction; destroy with the same unit context.

## State and persistence behavior

State persists in the caller-owned struct. Packet descriptors point into pages owned by the embedded `fw_iso_buffer`.

## Dependencies and integration points

It includes DMA mapping and FireWire headers and is implemented by `packets-buffer.c`. It is a lower-level utility beneath protocol-specific stream code.

## Risks and test signals

Risks are ABI/structure changes affecting consumers and misuse after failed initialization. Compile tests across FireWire modules and runtime ISO buffer allocation tests are the best signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/packets-buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/Makefile -->
# sources/distributed-fs/ceph-client/sound/firewire/tascam/Makefile

## Purpose

This Makefile builds the TASCAM FireWire ALSA driver composite object and gates it behind `CONFIG_SND_FIREWIRE_TASCAM`.

## Important APIs, types, and functions

`snd-firewire-tascam-y` lists proc, AMDTP protocol, stream, PCM, hwdep, transaction, MIDI, and core driver objects. `obj-$(CONFIG_SND_FIREWIRE_TASCAM) += snd-firewire-tascam.o` connects the composite object to Kbuild.

## Control flow

Kbuild includes all component objects when the config symbol is enabled as built-in or module. The listed object order forms one linked module.

## State and persistence behavior

No runtime state exists here; the file persists build topology.

## Dependencies and integration points

It integrates with the parent FireWire sound Makefile and TASCAM Kconfig symbol.

## Risks and test signals

Risks are stale object names and missing new sources. Test signals are module and built-in builds with `SND_FIREWIRE_TASCAM` enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/amdtp-tascam.c -->
# sources/distributed-fs/ceph-client/sound/firewire/tascam/amdtp-tascam.c

## Purpose

This file implements TASCAM's custom AMDTP payload handling. It converts between ALSA S32 PCM buffers and TASCAM data blocks, applies PCM constraints, and extracts status/control messages from incoming isochronous packets.

## Important APIs, types, and functions

`amdtp_tscm_init()` initializes an AMDTP stream with TASCAM format IDs and callbacks. `amdtp_tscm_set_parameters()` sets data channels, adding two extra channels for input streams. PCM helpers read/write S32 samples; `read_status_messages()` updates `tscm->state` and enqueues hwdep change events. `amdtp_tscm_add_pcm_hw_constraints()` declares 24 significant bits in 32-bit samples.

## Control flow

Incoming payload processing optionally copies PCM frames, then scans every data block's counter/state trailer. For selected state indexes, masked changes are queued to `tscm->queue` and `hwdep_wait` is woken. Outgoing payload processing writes PCM frames or silence. Initialization chooses `process_ir_ctx_payloads` for device-to-host streams and `process_it_ctx_payloads` for host-to-device streams, with nonblocking, skip-DBC-zero, and SYT-unaware flags.

## State and persistence behavior

Protocol state stores fixed PCM channel count. Driver state updated here includes `tscm->state`, circular control-change queue positions, and PCM buffer pointers managed by AMDTP core.

## Dependencies and integration points

It depends on `amdtp-stream`, TASCAM stream setup, ALSA PCM runtime buffers, and hwdep readers that drain queued control changes.

## Risks and test signals

Risks include queue overwrite, endianness mistakes, state mask omissions, buffer wrap errors, and wrong channel counts after model spec changes. Tests should cover PCM capture/playback, silence output, status-event generation, queue wrap, high-rate streams, and hwdep state ioctl consistency.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/amdtp-tascam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-hwdep.c -->
# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-hwdep.c

## Purpose

This file implements the TASCAM hwdep device for node information, stream locking, control-change notifications, and state snapshot ioctl.

## Important APIs, types, and functions

`snd_tscm_create_hwdep_device()` creates an exclusive `SNDRV_HWDEP_IFACE_FW_TASCAM` device. `hwdep_read()` returns either a lock-status event or a packed batch of `snd_firewire_tascam_change` entries. Ioctls implement `GET_INFO`, `LOCK`, `UNLOCK`, and `TASCAM_STATE`.

## Control flow

Read blocks while neither `dev_lock_changed` nor queue data is available. Lock-status reads clear the changed flag. Queue reads copy a type field followed by as many circular-buffer entries as fit, releasing the spinlock during user copies and reacquiring it to advance `pull_pos`. Poll reports readable when either event source is pending.

## State and persistence behavior

The file mutates `dev_lock_count`, `dev_lock_changed`, and `pull_pos`. It exposes `tscm->state`, which is maintained by the AMDTP status parser.

## Dependencies and integration points

It is driven by `snd_tscm_stream_lock_changed()` and by `amdtp-tascam.c` queueing control changes. User-space consumes the shared FireWire sound UAPI.

## Risks and test signals

Risks include circular queue races, partial user copies, short buffers returning `-EINVAL`, and lock state not notifying on user lock/unlock. Tests should cover batched event reads, wraparound, poll behavior, state ioctl, compat ioctl, signal interruption, and disconnect while reading.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-hwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-midi.c -->
# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-midi.c

## Purpose

This file creates ALSA RawMIDI ports for TASCAM FireWire models and connects them to the driver's asynchronous MIDI transaction layer.

## Important APIs, types, and functions

`snd_tscm_create_midi_devices()` creates a duplex RawMIDI device sized by model spec port counts and names hardware ports. Capture trigger stores active input substreams in `tx_midi_substreams`. Playback open initializes the corresponding `snd_fw_async_midi_port`; playback trigger starts its workqueue; drain finishes/cancels it.

## Control flow

Capture open/close are no-ops because inbound MIDI arrives through the async address handler. Playback open resets per-port transaction state. Trigger-up starts or records substreams under the driver spinlock; trigger-down clears capture substreams, while playback cleanup happens through drain/finish.

## State and persistence behavior

This file mutates active capture substream pointers and per-output async MIDI port state. RawMIDI device and substream names persist for the card lifetime.

## Dependencies and integration points

It depends on transaction helpers in `tascam-transaction.c`, model port counts from `tascam.c`, and ALSA RawMIDI core.

## Risks and test signals

Risks include output work continuing after close without drain, capture pointer races with async callbacks, and unsupported virtual ports. Tests should cover all model port counts, capture trigger toggles during incoming MIDI, playback running status/SysEx, drain behavior, and bus reset while output work is active.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-pcm.c -->
# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-pcm.c

## Purpose

This file exposes TASCAM FireWire audio as an ALSA duplex PCM device with fixed channel counts derived from model capabilities.

## Important APIs, types, and functions

`snd_tscm_create_pcm_devices()` creates one playback and one capture substream. `pcm_init_hw_params()` selects S32 format, derives channel count from analog plus optional ADAT/S/PDIF channels, enables 44.1/48/88.2/96 kHz, and adds TASCAM AMDTP constraints. Prepare, trigger, pointer, and ack callbacks bind ALSA operations to `tx_stream` and `rx_stream`.

## Control flow

Open takes the stream lock, initializes hardware params, reads clock source, and when externally clocked or already streaming, constrains rate/period/buffer to current domain values. `pcm_hw_params()` reserves duplex resources and increments `substreams_counter`. `pcm_hw_free()` decrements and stops when the last substream is freed. Prepare starts the duplex stream at the runtime rate and prepares the selected AMDTP stream.

## State and persistence behavior

The file mutates runtime constraints, `substreams_counter`, stream lock state, and AMDTP PCM trigger state. Hardware rate and stream resources are managed by `tascam-stream.c`.

## Dependencies and integration points

It depends on model specs in `tascam.c`, stream helpers, AMDTP TASCAM constraints, and ALSA PCM core. Hwdep lock notifications share the same `dev_lock_count`.

## Risks and test signals

Risks include constraint attempts with zero period/buffer before reservation, counter imbalance, and wrong fixed channel counts for model specs. Tests should cover all models, external clock mode, duplex opens, rate changes, ADAT/S/PDIF variants, and xrun recovery.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-proc.c -->
# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-proc.c

## Purpose

This file adds a TASCAM proc diagnostic node for firmware and hardware version registers.

## Important APIs, types, and functions

`snd_tscm_proc_init()` creates `firewire/firmware` under the ALSA card proc root. `proc_read_firmware()` reads four quadlet registers: register firmware, FPGA, ARM, and hardware. `add_node()` wraps ALSA info-entry creation.

## Control flow

The proc callback performs four FireWire quadlet reads in sequence; on any failure it returns early. Successful reads are converted from big-endian and printed as decimal/hex version fields.

## State and persistence behavior

The file owns no persistent state and only reads hardware registers. Proc entries live for the ALSA card lifetime and are removed by card disconnect.

## Dependencies and integration points

It depends on `snd_fw_transaction()`, TASCAM register offsets in `tascam.h`, and ALSA info infrastructure.

## Risks and test signals

Risks include empty proc output on transient FireWire errors and interpretation drift for version bitfields. Tests should read the proc node during idle, after bus reset, and on each supported TASCAM model.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-stream.c -->
# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-stream.c

## Purpose

This file owns TASCAM duplex audio streaming: clock register handling, data-channel enablement, stream session programming, FireWire resource allocation, AMDTP domain startup/shutdown, bus-reset handling, and stream locks.

## Important APIs, types, and functions

Exports include `snd_tscm_stream_get_rate()`, `get_clock()`, `init_duplex()`, `reserve_duplex()`, `start_duplex()`, `stop_duplex()`, `update_duplex()`, and lock helpers. Helpers program `TSCM_OFFSET_*` registers for clock, channels, stream start, isochronous channels, multiplex mode, and options.

## Control flow

`get_clock()` retries while the hardware clock status is intermediate. Reserve stops existing streams, finishes the session, frees resources, sets clock rate, allocates tx/rx resources, sets domain period sizing, and records whether a long transmit skip is needed after rate change. Start updates resources after bus reset, sets stream formats/channels, begins the hardware session, adds rx and tx streams to the domain, chooses up to 16000 skip cycles after rate changes, starts the domain with sequence replay, and waits up to four seconds ready. Stop tears down only when no substreams remain.

## State and persistence behavior

The file persists hardware register state, FireWire resource reservations, domain state, and `need_long_tx_init_skip`. Lock state mirrors other FireWire drivers: negative for user lock, positive for active kernel users.

## Dependencies and integration points

It depends on `amdtp-tascam.c`, `fw_iso_resources`, model specs, transaction register constants, PCM/MIDI callers, and hwdep lock notifications.

## Risks and test signals

Risks include undocumented register writes, clock intermediate timeouts, cleanup after partial begin failures, and incorrect skip-cycle timing. Tests should cover all supported rates, bus reset, external clock, rate change while reopening, no-substream stop, and forced transaction failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-transaction.c -->
# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-transaction.c

## Purpose

This file implements TASCAM asynchronous MIDI transaction support and device registration of the host callback address.

## Important APIs, types, and functions

`calculate_message_bytes()` classifies MIDI status lengths. `fill_message()` formats outbound MIDI into a four-byte TASCAM quadlet with port label and up to three MIDI bytes, handling running status and SysEx. `midi_port_work()` schedules and sends outgoing quadlet transactions at MIDI baud timing. `handle_midi_tx()` receives inbound MIDI block writes. Register/reregister/unregister functions manage the device callback address, MIDI TX enable bit, and FireWire LED.

## Control flow

Outbound work peeks RawMIDI bytes, forms a complete message only when enough bytes are available, schedules the next send time based on consumed bytes, sends a FireWire write request, and acknowledges bytes only after a successful callback. Recoverable errors retry immediately; permanent errors stop the port. Inbound handler splits block transactions into messages, selects the hardware port from the label, estimates MIDI length, and delivers bytes to active capture substreams.

## State and persistence behavior

Per-output-port state includes work item, next send time, transaction object, running status, SysEx state, active substream, and error/idling flags. Device state persists callback address and MIDI/LED enable registers until unregister or bus reset.

## Dependencies and integration points

It depends on RawMIDI, FireWire request callbacks, `tascam-midi.c` trigger state, and bus-reset update calling `snd_tscm_transaction_reregister()`.

## Risks and test signals

Risks include MIDI parser edge cases, timing drift, no support for virtual ports, queue starvation when incomplete SysEx bytes are pending, and races with close/reset. Tests should cover running status, SysEx start/end, real-time messages, recoverable/permanent transaction errors, inbound block batches, bus reset, and unregister cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-transaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam.c -->
# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam.c

## Purpose

This is the TASCAM FireWire driver entry point. It identifies supported models, initializes ALSA card state, connects transaction/stream/proc/PCM/MIDI/hwdep components, and registers the FireWire driver.

## Important APIs, types, and functions

`model_specs[]` defines FW-1884, FW-1082, and FW-1804 capabilities. `identify_model()` extracts an eight-byte model string from config ROM words and binds the matching spec. `snd_tscm_probe()` builds the card. `snd_tscm_update()` handles bus reset by re-registering async transactions and aborting streams. The ID table matches TASCAM vendor/specifier/version values.

## Control flow

Probe creates the ALSA card, initializes locks and wait queue, identifies the model, registers async MIDI transactions, initializes duplex streams, creates proc/PCM/MIDI/hwdep devices, and registers the card. Failures free the card and trigger cleanup. Remove blocks through `snd_card_free()` until ALSA users are gone.

## State and persistence behavior

This file initializes persistent runtime state in `struct snd_tscm`: card/unit refs, locks, model spec, transaction state, streams, and wait queue. It has no on-disk persistence.

## Dependencies and integration points

It binds Linux FireWire core to ALSA and all TASCAM submodules. Config ROM model parsing is central because the ID table alone does not distinguish all capabilities.

## Risks and test signals

Risks include fragile config-ROM string offsets, unsupported FE-8 behavior, probe cleanup order, and model spec mismatches. Tests should cover all three supported models, short config ROM rejection, bus reset, failed submodule creation, and module load/unload.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam.h -->
# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam.h

## Purpose

This header defines the shared TASCAM FireWire driver state, register map, model specification, MIDI transaction state, stream API, and submodule prototypes.

## Important APIs, types, and functions

`struct snd_tscm_spec` records model capabilities. `struct snd_fw_async_midi_port` stores outbound async MIDI transaction state. `struct snd_tscm` centralizes ALSA card/unit refs, locks, stream resources, async MIDI handler, MIDI substreams, status cache, hwdep queue, AMDTP domain, and skip-cycle state. The header defines all `TSCM_OFFSET_*` register constants and `enum snd_tscm_clock`.

## Control flow

Inline helpers `snd_fw_async_midi_port_run()` and `finish()` start and stop outbound MIDI work by setting the active substream and scheduling or canceling work. Other behavior is declared for implementation in TASCAM source files.

## State and persistence behavior

The header describes all runtime state. Hardware state lives in registers under `TSCM_ADDR_BASE`, while kernel state persists only for the card lifetime.

## Dependencies and integration points

It includes ALSA core/info/PCM/rawmidi/hwdep, Linux FireWire, and common AMDTP/iso-resource helpers. It is included by every TASCAM implementation file.

## Risks and test signals

Risks include register-map uncertainty, queue-size limitations, port-count maxima, and lifetime coupling between work items and card removal. Compile tests catch prototype drift; runtime tests should stress MIDI work cancellation, hwdep queue wrap, and stream state transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/Kconfig -->
# sources/distributed-fs/ceph-client/sound/hda/Kconfig

## Purpose

This Kconfig file defines the top-level "HD-Audio" menu and includes the HDA common, controller, codec, and core configuration subtrees.

## Important APIs, types, and functions

It uses Kconfig `menu`, `source`, and `endmenu` directives. The included files are `sound/hda/common/Kconfig`, `sound/hda/controllers/Kconfig`, `sound/hda/codecs/Kconfig`, and `sound/hda/core/Kconfig`.

## Control flow

During kernel configuration, entering the HD-Audio menu exposes symbols from the sourced subtrees. Ordering places common/controller/codecs/core symbols under the same menu but leaves individual dependencies to those files.

## State and persistence behavior

There is no runtime state. The persistent effect is the generated kernel `.config` choices and build graph.

## Dependencies and integration points

This is the integration root for the HDA subsystem configuration. It must align with the HDA Makefile directory layout.

## Risks and test signals

Risks are missing sourced subtrees after directory refactors or symbols hidden by menu placement. Test signals are `make menuconfig`, `olddefconfig`, and builds for configurations enabling HDA controllers/codecs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/Makefile -->
# sources/distributed-fs/ceph-client/sound/hda/Makefile

## Purpose

This Makefile defines top-level HDA build ordering across core, common, codecs, and controllers.

## Important APIs, types, and functions

`obj-y += core/` always descends into the core directory. `obj-$(CONFIG_SND_HDA) += common/ codecs/ controllers/` conditionally builds the remaining HDA pieces. A comment documents that controllers must be listed last so built-in codec drivers hook before PCI probe.

## Control flow

Kbuild descends into directories in the listed order. When `CONFIG_SND_HDA` is disabled only `core/` is traversed; when enabled, common and codec drivers are built before controllers.

## State and persistence behavior

No runtime state exists. The file controls build-time object ordering, which affects built-in initialization behavior.

## Dependencies and integration points

It must match Kconfig symbols and directory layout. The controller ordering integrates with codec driver registration expectations.

## Risks and test signals

Risks include reordering controllers before codecs, causing built-in probe ordering regressions, or missing directories from the build. Test signals are built-in HDA boots, module builds, and link/order checks after Makefile edits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/Kconfig -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/Kconfig

## Purpose

This Kconfig file defines selectable HD-audio codec driver symbols and sources vendor-specific codec subtrees under the `SND_HDA` dependency.

## Important APIs, types, and functions

Symbols include `SND_HDA_GENERIC_LEDS`, vendor codec tristates for Analog, Sigmatel/IDT, VIA, Conexant, Senarytech, Creative CA0110/CA0132, C-Media, CM9825, SI3054, and `SND_HDA_GENERIC`. `SND_HDA_CODEC_CA0132_DSP` enables firmware-backed DSP support. It sources Realtek, Cirrus, HDMI, and side-codec Kconfig files.

## Control flow

All options are inside `if SND_HDA`. Many vendor codecs `select SND_HDA_GENERIC`, and some select generic LED support. Comments warn users about built-in HDA with modular codec auto-loading. CA0132 DSP depends on the CA0132 codec and selects DSP loader plus firmware loader.

## State and persistence behavior

There is no runtime state. Configuration choices persist in `.config` and determine codec object inclusion and feature dependencies.

## Dependencies and integration points

This file integrates codec-specific drivers with the generic parser, LED class, firmware loader, and vendor subdirectories. Its symbols are consumed by `sound/hda/codecs/Makefile`.

## Risks and test signals

Risks include missing `select` dependencies, bad module/built-in combinations, and firmware dependency surprises. Test signals are config matrix builds for y/m combinations, auto-loading behavior with `SND_HDA=y`, and CA0132 DSP firmware path validation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/Makefile -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/Makefile

## Purpose

This Makefile maps HDA codec Kconfig symbols to codec driver objects and descends into vendor subdirectories.

## Important APIs, types, and functions

`subdir-ccflags-y` adds the common include path. `snd-hda-codec-*-y` variables map composite module names to source objects such as `generic.o`, `cmedia.o`, `analog.o`, `ca0132.o`, `conexant.o`, and `sigmatel.o`. `obj-y` descends into `cirrus/`, `hdmi/`, `realtek/`, and `side-codecs/`; `obj-$(CONFIG_...)` gates each top-level codec object.

## Control flow

Kbuild applies the include flag to this subtree, descends into vendor folders, and builds each codec module when its config symbol is enabled. Composite object variables support module names that differ from source filenames.

## State and persistence behavior

No runtime state exists. The file persists build graph and object naming.

## Dependencies and integration points

It depends on symbols from `codecs/Kconfig` and headers under `../common`. It integrates top-level codecs with vendor-specific subtrees and the parent HDA Makefile ordering.

## Risks and test signals

Risks include object-name mismatches, missing include paths, and Kconfig/Makefile symbol drift. Test signals are per-codec module builds, allmodconfig, allyesconfig, and vendor subtree builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/Makefile -->
