# Research: subset-b-006361

Grouped research for FireWire ALSA driver files under `sources/distributed-fs/ceph-client/sound/firewire`. Each section is delimited for deterministic split into the source-tree-aligned per-file report path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-pcm.c -->
## sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-pcm.c

Purpose: creates the ALSA PCM device for Digidesign Digi 002/003 and binds capture/playback callbacks to the driver duplex stream engine. Important APIs are `snd_dg00x_create_pcm_devices()`, the PCM ops tables, `pcm_open()`, `pcm_hw_params()`, prepare/trigger/pointer/ack callbacks, and the two hardware rules that keep sampling rates aligned with channel-count variants from `snd_dg00x_stream_rates` and `snd_dg00x_stream_pcm_channels`.

Control flow: open takes the stream lock, initializes runtime constraints, reads clock state, rejects missing external clock, and narrows rate/period/buffer constraints when an external clock or existing stream reservation is active. `hw_params` reserves duplex resources and increments `substreams_counter`; `hw_free` decrements it and may stop/free streams. Prepare starts the duplex domain and arms the matching AMDTP stream; trigger only attaches or detaches the PCM substream. State is shared through `dg00x->mutex`, `dev_lock_count`, `substreams_counter`, and `amdtp_domain` period geometry. Dependencies are ALSA PCM core, `amdtp-dot`, and `digi00x-stream.c` device-register helpers. Risks include counter imbalance on unusual ALSA state paths, stale external-clock detection, and period constraints leaking across concurrently opened substreams. Test signals: open under internal and external clocks, rate/channel matrix validation, start/stop under bus reset, and duplex pointer/ack behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-proc.c -->
## sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-proc.c

Purpose: exposes human-readable Digi00x clock and optical-interface status through ALSA procfs under the card's `firewire/clock` node. Important functions are `snd_dg00x_proc_init()`, `proc_read_clock()`, and the private `get_optical_iface_mode()` register reader. It maps driver enums for clock source and optical mode to labels, then prints local rate, current source, external source detection, and external rate when relevant.

Control flow is simple: proc init creates a `firewire` directory, then a text node whose callback performs synchronous FireWire quadlet reads through `snd_fw_transaction()` and stream helpers. No state is persisted by this file; it snapshots hardware registers when users read procfs. Dependencies include ALSA info entries, Digi00x register offsets from `digi00x.h`, and `snd_dg00x_stream_get_*()` functions. Integration is diagnostic rather than part of the streaming fast path. Risks are silent partial output on transaction failure and array indexing if firmware returns an enum value outside the expected range, though the stream helpers validate clock/rate. Test signals: proc node creation during probe, output under internal and external clock sources, missing external source behavior, and transaction-failure paths that should return no stale data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-stream.c -->
## sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-stream.c

Purpose: owns Digi00x duplex stream setup, sampling-rate/clock register access, isochronous resource allocation, session start/finish, bus-reset update, and user/PCM stream locking. Public APIs include `snd_dg00x_stream_get_local_rate()`, `set_local_rate()`, `get_clock()`, `check_external_clock()`, `get_external_rate()`, `init_duplex()`, `reserve_duplex()`, `start_duplex()`, `stop_duplex()`, `update_duplex()`, `destroy_duplex()`, and stream lock helpers.

Control flow: initialization creates RX/TX AMDTP DOT streams and FireWire ISO resources, then initializes an AMDTP domain. Reservation reads the current hardware rate, stops any existing domain when the requested rate changes, finishes the device session, frees resources, writes the local rate, programs stream parameters, allocates TX/RX ISO channels, and stores period geometry. Start handles prior streaming errors, refreshes resources after bus generation changes, writes both isochronous channel numbers to the device, steps the streaming state down through `begin_session()`, adds both streams to the domain, starts the domain, and waits ready. Stop tears down only when `substreams_counter` reaches zero. Persistent state is in `snd_dg00x`: resource generation/channel, AMDTP stream state, domain timing, and lock notification flags. Dependencies are `snd_fw_transaction`, `fw_iso_resources`, and `amdtp-dot`. Risks include opaque device state-machine writes, timeout sensitivity, failed second resource allocation cleanup, and bus-reset windows. Test signals: rate changes while idle and active, generation updates, streaming error recovery, timeout handling, and hwdep lock notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-transaction.c -->
## sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-transaction.c

Purpose: registers a host FireWire address range for asynchronous Digi00x device messages and tells the device where to send them. Important APIs are `snd_dg00x_transaction_register()`, `snd_dg00x_transaction_reregister()`, and `snd_dg00x_transaction_unregister()`, with `handle_message()` and `handle_unknown_message()` as the address-handler callbacks.

Control flow: registration initializes a 4-byte `fw_address_handler` in a broad memory-space region, then writes the handler's node/address pair to the device message-address registers. Bus update calls `reregister()` so the device sees the new node ID after reset. Incoming writes are acknowledged with `RCODE_COMPLETE`; writes at the allocated offset store the big-endian quadlet into `dg00x->msg` under spinlock and wake hwdep readers. State is the handler, latest message value, wait queue, and callback-data sentinel used to avoid double unregister. Dependencies are FireWire core address handlers and `snd_fw_transaction()`. Risks include treating all messages as unknown, relying on userspace to interpret `msg`, and losing messages if multiple arrive before hwdep read. Test signals: handler allocation failure, reregister after bus reset, remove while callback data is null, and hwdep wakeups after injected async writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-transaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x.c -->
## sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x.c

Purpose: top-level FireWire driver for Digidesign Digi 002/003 console and rack devices. It declares module metadata, IEEE 1394 IDs, probe/update/remove callbacks, card naming, and module registration. Key functions are `snd_dg00x_probe()`, `snd_dg00x_update()`, `snd_dg00x_remove()`, and `dg00x_card_free()`.

Probe creates an ALSA card with `struct snd_dg00x` as private data, stores the unit reference, initializes mutex/spinlock/wait queue, determines console-vs-rack from the match entry, names the card from CSR model text, initializes duplex streams, proc, PCM, MIDI, hwdep, async transactions, and finally registers the card. Cleanup reverses stream/transaction setup and drops the FireWire unit. Update re-registers async message address and refreshes duplex streams under the device mutex. State is mostly delegated to submodules but owned through `snd_dg00x`. Dependencies include ALSA core, FireWire bus matching, Digi00x stream/proc/PCM/MIDI/hwdep/transaction modules, and model IDs. Risks are probe unwind ordering, card-free blocking on open ALSA nodes, and update racing with removal if driver data is invalid. Test signals: both model IDs, failure injection at each probe stage, bus reset while streaming, and remove with open PCM/hwdep file descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x.h -->
## sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x.h

Purpose: central Digi00x driver contract. It defines `struct snd_dg00x`, device register offsets under `DG00X_ADDR_BASE`, rate/clock/optical enums, MIDI port counts, and prototypes for DOT AMDTP, transactions, stream management, proc, PCM, MIDI, and hwdep modules.

State model: `struct snd_dg00x` owns the ALSA card, FireWire unit, coarse mutex, spinlock, TX/RX AMDTP streams, TX/RX ISO resources, active substream count, hwdep lock/change fields, async address handler/latest message, console-model flag, and duplex AMDTP domain. Persistent hardware state is not cached except for stream/resource/domain state and lock notifications; clock/rate reads are done directly from device registers. Integration points are all other Digi00x source files plus shared `lib.h`, `iso-resources.h`, and `amdtp-stream.h`. Risks concentrate around shared fields whose invariants span files: `substreams_counter` must match PCM/MIDI reservations, `dev_lock_count` uses negative values for userspace exclusion, and the async handler must be registered before device messages are enabled. Test signals: compile-time include coverage, enum/register offset consistency, cross-file prototype drift, and lock/counter behavior across hwdep and PCM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fcp.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fcp.c

Purpose: shared Function Control Protocol and AV/C helper implementation for FireWire audio drivers. It exports `avc_general_set_sig_fmt()`, `avc_general_get_sig_fmt()`, `avc_general_get_plug_info()`, `fcp_avc_transaction()`, and `fcp_bus_reset()`. It also registers a global FCP response address handler for `CSR_FCP_RESPONSE`.

Control flow: AV/C helpers build command buffers, issue `fcp_avc_transaction()`, validate response length/status/matching bytes, translate AV/C status to Linux errors, and convert sampling-frequency codes through `amdtp_rate_table`. `fcp_avc_transaction()` links a stack transaction into the global list, sends the command to `CSR_FCP_COMMAND`, waits up to 125 ms per response interval, handles INTERIM responses for deferrable commands, retries after bus reset/timeouts, then unlinks. The response handler matches card/generation/node and masked response bytes, copies matched responses, and wakes waiters. State is the global transaction list and per-call wait queue. Dependencies are FireWire core, shared `snd_fw_transaction()`, AMDTP rate tables, spinlocks, and wait queues. Risks include response matching collisions, indefinite practical wait if a device repeatedly sends INTERIM, stack transaction lifetime while listed, and bus-reset retry timing. Test signals: concurrent AV/C transactions, masked-byte mismatch, timeout/retry logging, INTERIM-to-final completion, and `fcp_bus_reset()` waking pending waiters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fcp.h -->
## sources/distributed-fs/ceph-client/sound/firewire/fcp.h

Purpose: public declarations for the FireWire FCP/AV-C helper module. It defines the four-byte plug-info response size, forward-declares `struct fw_unit`, declares `enum avc_general_plug_dir`, and exposes AV/C signal-format, plug-info, generic transaction, and bus-reset functions.

The header establishes the integration contract for drivers that need AV/C general commands without depending on the implementation internals in `fcp.c`. There is no runtime state here, but the API semantics imply DMA-capable command/response buffers for `fcp_avc_transaction()` and a required `.update` hook call to `fcp_bus_reset()` when a device may have outstanding transactions. Dependencies are Linux types via included users, FireWire unit objects, and UAPI-style numeric command constants embedded in callers. Risks are primarily API misuse: insufficient response buffer size, wrong `response_match_bytes`, failing to call `fcp_bus_reset()` on update, or passing unsupported subunit identifiers to plug-info helper. Test signals: build coverage from AV/C-capable drivers, sparse/prototype checks, and functional tests that exercise each helper with supported and rejected devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/Makefile -->
## sources/distributed-fs/ceph-client/sound/firewire/fireface/Makefile

Purpose: Kbuild fragment for the RME Fireface ALSA FireWire module. It composes `snd-fireface.o` from common driver, transaction, MIDI, proc, AMDTP packet, stream, PCM, hwdep, and both former/latter protocol implementation objects, then includes it when `CONFIG_SND_FIREFACE` is enabled.

There is no runtime control flow or persistence, but the object ordering documents the integration surface: `ff.o` supplies driver registration, `ff.h` defines shared state, `ff-protocol-former.o` and `ff-protocol-latter.o` provide the protocol vtable instances used by the core. Dependencies are Kbuild and the kernel config symbol. Risks include missing a newly added implementation object, stale object names after file rename, or building protocol code without the shared declarations it needs. Test signals are kernel build coverage with `CONFIG_SND_FIREFACE=m/y`, modpost symbol checks, and ensuring all protocol symbols referenced by `ff.c` resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/amdtp-ff.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireface/amdtp-ff.c

Purpose: implements the Fireface-specific AMDTP payload codec for PCM samples. It exposes `amdtp_ff_init()`, `amdtp_ff_set_parameters()`, and `amdtp_ff_add_pcm_hw_constraints()`. The protocol private data stores current PCM channel count.

Control flow: parameter setup rejects running streams, records channel count, and configures a no-header AMDTP stream with one event per data block. Playback payload processing writes little-endian 32-bit sample words or silence; capture processing reads little-endian sample words, masks to 24 significant bits, and advances ALSA ring pointers through the AMDTP core. Initialization selects transmit or receive payload callbacks and sets `CIP_BLOCKING | CIP_UNAWARE_SYT | CIP_NO_HEADER`, matching Fireface packets without standard CIP headers. State is per-stream protocol data plus `amdtp_stream` buffer pointers. Dependencies are ALSA PCM runtime, AMDTP stream core, and Fireface stream/PCM code. Risks include endian assumptions, 24-bit-in-32-bit masking, channel count mismatches with device protocol tables, and buffer wrap logic. Test signals: multi-rate channel counts, capture/playback sample alignment, silence when no playback PCM is attached, and xrun/stream restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/amdtp-ff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-hwdep.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-hwdep.c

Purpose: creates the Fireface hwdep device for userspace discovery, lock/unlock of streaming resources, lock-status event reads, and optional protocol message reads. Important APIs are `snd_ff_create_hwdep_devices()`, `hwdep_read()`, `hwdep_poll()`, `hwdep_ioctl()`, and lock helpers.

Control flow: read waits until `dev_lock_changed` or protocol `has_msg()` becomes true. Lock status events are copied directly; protocol messages are delegated to `copy_msg_to_user()` with the spinlock intentionally released inside protocol code where user memory is touched. IOCTL returns FireWire node info and manages exclusive userspace stream locks by setting `dev_lock_count` to `-1`. State is `dev_lock_count`, `dev_lock_changed`, protocol parser queues, and `hwdep_wait`. Dependencies are ALSA hwdep, FireWire UAPI structures, `snd_ff_protocol` optional callbacks, and spinlock/wait-queue coordination. Risks include lock ordering around protocol copy callbacks, starvation if events arrive faster than reads, and userspace lock release on file close. Test signals: poll/read wakeups for lock and FF400 messages, compat ioctl, lock contention with PCM open, and remove while hwdep is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-hwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-midi.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-midi.c

Purpose: creates Fireface raw MIDI devices and wires ALSA rawmidi streams to asynchronous transaction handling. Public entry point is `snd_ff_create_midi_devices()`, with stream open/close/trigger callbacks for capture and playback.

Control flow: capture open/close are no-ops, while capture trigger stores or clears `tx_midi_substreams[]` under spinlock so transaction callbacks can deliver incoming MIDI bytes. Playback open resets per-port sysex/error state and publishes the substream; playback close cancels pending work and clears it. Playback trigger schedules the per-port worker unless a permanent MIDI transfer error is latched. State includes TX/RX substream arrays, `on_sysex`, `rx_midi_error`, per-port workers, byte counts, and transaction buffers owned by `struct snd_ff`. Dependencies are ALSA rawmidi and `ff-transaction.c` workers/protocol packing. Risks include async work racing with close, permanent-error recovery requiring reopen, and correct mapping of “input”/“output” relative to device direction. Test signals: bidirectional MIDI byte flow, close with pending worker, sysex packetization on latter protocols, and error retry/permanent error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-pcm.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-pcm.c

Purpose: creates Fireface ALSA PCM devices and enforces model/rate-dependent channel constraints. It exposes `snd_ff_create_pcm_devices()` and implements open/close/hw_params/hw_free/prepare/trigger/pointer/ack callbacks.

Control flow: open takes a stream lock, initializes S32 runtime hardware, computes allowed rates/channels from the selected model spec, asks the protocol for current clock, and narrows rate/period/buffer constraints when externally clocked or already reserved. `hw_params` reserves duplex streams and increments `substreams_counter`; `hw_free` decrements and may stop. Prepare starts duplex streaming with the runtime rate and arms the relevant AMDTP stream. Trigger attaches/detaches the PCM substream, while pointer and ack defer to the AMDTP domain. State is shared through `struct snd_ff`, especially protocol spec tables, `substreams_counter`, domain period geometry, and stream lock fields. Dependencies include ALSA PCM, `amdtp-ff`, `ff-stream`, and protocol `get_clock()`. Risks include unsupported hardware rates outside `amdtp_rate_table`, wrong mode/channel table entries for a model, and counter imbalance. Test signals: all model specs across low/mid/high rate modes, external-clock constraints, duplex synchronized start, and bus-reset abort/reopen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-proc.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-proc.c

Purpose: provides Fireface procfs diagnostics under `firewire/status` and a shared clock-source label helper. Important functions are `snd_ff_proc_get_clk_label()`, `snd_ff_proc_init()`, and `proc_dump_status()`.

Control flow: initialization creates a `firewire` proc directory and installs a text callback. Reads delegate status formatting to the model protocol’s `dump_status()` callback, which keeps register-map knowledge out of the common proc file. State is not cached here; output is a snapshot of hardware status produced by protocol files. Dependencies are ALSA info, `struct snd_ff`, and the `snd_ff_protocol` vtable. Risks are minimal but include missing labels for new clock enum values and null/failed protocol dumps producing sparse proc output. Test signals: proc node existence for all supported models, label lookup bounds, former/latter protocol dumps, and read behavior when transactions fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-protocol-former.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-protocol-former.c

Purpose: implements `snd_ff_protocol` instances for former Fireface devices, specifically FF800 and FF400. It owns former register maps, clock parsing, status dumping, MIDI packing/parsing, and model-specific resource/session operations.

Control flow: shared former helpers parse clock bits from `FORMER_REG_CLOCK_CONFIG`, toggle fetch mode by block-writing per-channel flags, and dump clock/sync status. FF800 allocation writes sampling frequency, allocates only RX resources through the kernel resource manager, obtains TX channel from the device, and starts/stops communication through FF800 registers. FF400 allocation restricts channel masks to 0-7, allocates both TX/RX resources, programs packet formats, and starts/stops communication through FF400 registers. MIDI handling differs: FF800 receives one byte per quadlet; FF400 multiplexes signal-level messages into a ring parser for hwdep and MIDI bytes by flag. State includes protocol-specific message parser queue, ISO resource channels, and Fireface MIDI buffers. Dependencies are `snd_fw_transaction`, `fw_iso_resources`, ALSA rawmidi, and common Fireface stream code. Risks include many undocumented bitfields, polling timeouts while waiting for TX channel, FF400 ring overwrite when push catches pull, and userspace-dependent lower-address configuration. Test signals: FF800/FF400 rate changes, channel allocation boundaries, fetch-mode toggling, status proc output, MIDI byte paths, and FF400 hwdep signal-level events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-protocol-former.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-protocol-latter.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-protocol-latter.c

Purpose: implements the `snd_ff_protocol_latter` vtable for Fireface UFX, UCX, and 802 generation devices. It owns latter register offsets, clock/rate parsing, fetch mode, resource allocation, session start/finish, status dumping, and compact MIDI message formatting.

Control flow: `latter_get_clock()` reads sync status and `parse_clock_bits()` decodes different rate/source fields for UCX versus UFX/802. Resource allocation writes a sampling-frequency code, polls until the clock reports the requested rate, maps to stream mode, and allocates TX/RX resources on channels 0-7. Session start chooses a model/rate flag, updates resources after bus reset, writes packed TX/RX channel numbers, and enables isochronous communication; finish clears the start register. MIDI receive decodes packed status/port/bytes from async messages; MIDI transmit builds one quadlet with port, length, status bytes, and sysex tracking. State is in `snd_ff` plus per-port `on_sysex`. Dependencies are common Fireface transaction/stream code, FireWire transactions, and rawmidi. Risks include hardware-specific bitfields, polling without sleep in the clock-confirm loop, model differences hidden behind `unit_version`, and sysex fragmentation edge cases. Test signals: UCX and UFX/802 clock parsing, all rate bands, fetch toggling, MIDI channel voice and sysex messages, and resource update after bus reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-protocol-latter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-stream.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-stream.c

Purpose: common Fireface duplex streaming lifecycle. It initializes AMDTP streams/resources/domain, maps sampling frequencies to low/mid/high stream modes, reserves resources, starts/stops the domain, handles update aborts, and manages ALSA/hwdep stream locks.

Control flow: reserve queries protocol clock, stops and finishes existing session when first reservation or rate change occurs, frees resources, validates rate, configures TX/RX AMDTP channels from model spec, delegates resource allocation to the protocol, and stores period geometry. Start checks streaming errors, calls protocol `begin_session()`, adds RX/TX streams to the AMDTP domain, starts the domain, waits ready, then enables device fetch mode. Stop tears everything down only when no substreams remain. Update forcibly stops the domain and aborts PCM streams because Fireface devices discontinue packets after bus reset. State is `substreams_counter`, `amdtp_domain`, TX/RX streams/resources, and lock notification fields. Dependencies are `amdtp-ff`, `fw_iso_resources`, and `snd_ff_protocol`. Risks include protocol callbacks needing precise cleanup on partial failures, start timeout recovery, and abort behavior on update even if streams could have been recovered. Test signals: mode mapping, resource reservation per model/rate, bus reset while streaming, fetch-mode off on finish, and lock-status events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-transaction.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-transaction.c

Purpose: manages Fireface asynchronous MIDI/control transactions. It registers a host address window, writes its high address to the device, handles inbound async messages, and schedules outbound MIDI writes.

Control flow: registration searches IEC 13213 memory-space windows until it obtains one whose low 32 bits are zero, writes the high address to `spec->midi_high_addr`, and initializes per-port workers. Inbound messages are acknowledged, offset-adjusted, and passed under spinlock to the selected protocol’s `handle_msg()`. Outbound MIDI workers call protocol `fill_midi_msg()`, throttle based on MIDI wire time, choose quadlet/block request, and send FireWire requests with generation/node ID serialized by `smp_rmb()`. Completion callbacks retry transient errors, latch permanent errors, acknowledge rawmidi bytes, and reschedule if more data is queued. State includes async handler, transaction objects, `next_ktime`, `rx_bytes`, error flags, and substream pointers. Dependencies are FireWire core async requests, `snd_fw_transaction`, protocol callbacks, and rawmidi. Risks include worker/close races, permanent-error latching, lost inbound messages if userspace does not configure lower address as expected, and generation changes between request and completion. Test signals: address allocation fallback, bus reset reregister, MIDI retry/permanent-error paths, and async inbound parsing for each protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff-transaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireface/ff.c

Purpose: top-level FireWire driver for RME Fireface 800/400/UFX/UCX/802. It binds IEEE 1394 IDs to model specs, creates and names the ALSA card, wires common Fireface submodules, and registers the `fw_driver`.

Probe creates `struct snd_ff`, initializes locks and wait queue, stores unit version/spec from match data, registers async transactions first, names the card, initializes streams, proc, MIDI, PCM, hwdep, allocates an optional protocol message parser, and registers the card. Card cleanup destroys duplex streams, unregisters transactions, frees parser memory, destroys mutex, and drops the unit. Update re-registers async address and calls stream update; remove frees the ALSA card and waits for character devices. State is the model spec table, unit version, and `snd_ff` private data. Dependencies are all `ff-*` modules, FireWire matching, and ALSA core. Risks include transaction registration before stream init requiring robust card-free unwind, protocol parser allocation after hwdep creation, and model spec correctness for channel counts and MIDI addresses. Test signals: probe all IDs/specs, failure injection after each submodule creation, bus reset with active streams/MIDI, and module unload with open files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff.h -->
## sources/distributed-fs/ceph-client/sound/firewire/fireface/ff.h

Purpose: shared Fireface header defining model enums, stream modes, `snd_ff_spec`, `snd_ff`, clock-source enum, `snd_ff_protocol` vtable, protocol instances, and cross-file prototypes.

State model: `struct snd_ff` centralizes card/unit, mutex/spinlock, model version/spec, MIDI TX/RX substream pointers, async handler, sysex/error/work/transaction state, TX/RX AMDTP streams, ISO resources, substream counter, hwdep lock fields, AMDTP domain, and optional protocol message parser. `snd_ff_spec` supplies per-mode capture/playback channels, MIDI port counts, protocol pointer, and MIDI address details. `snd_ff_protocol` abstracts generational differences: message queueing, MIDI packing, clock read, fetch mode, resource/session operations, and status dump. Dependencies are ALSA core, FireWire, shared lib/AMDTP/ISO helpers, and UAPI event structures through hwdep users. Risks are cross-file invariants: protocol callbacks must be non-null for required operations, array sizes cap MIDI ports at two, and lock/counter fields are shared by PCM, MIDI, and hwdep. Test signals: compile-time prototype coverage, all spec/protocol combinations, bounds on MIDI port arrays, and vtable behavior under unsupported optional callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireface/ff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/Makefile -->
## sources/distributed-fs/ceph-client/sound/firewire/fireworks/Makefile

Purpose: Kbuild fragment for Echo Fireworks-family ALSA FireWire support. It links transaction, command, stream, proc, MIDI, PCM, hwdep, and top-level driver objects into `snd-fireworks.o`, included under `CONFIG_SND_FIREWORKS`.

The file has no runtime behavior, but its object list documents module layering: low-level EFW transaction and command code support probe and hwdep, stream/PCM/MIDI use those capabilities for ALSA devices, and `fireworks.o` owns registration. Dependencies are Kbuild and the config symbol. Risks are build omissions when new helper files are added, incorrect object ordering only if future link-time init dependencies appear, and stale object names after renames. Test signals: kernel build with `CONFIG_SND_FIREWORKS`, modpost symbol resolution, and ensuring all functions declared in `fireworks.h` are supplied by listed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks.c

Purpose: top-level Echo Fireworks driver for supported Echo, Mackie, and Gibson devices. It handles module parameters, card index allocation, probe/update/remove, hardware capability discovery, model quirks, and FireWire ID matching.

Probe reserves an enabled ALSA card slot under `devices_mutex`, creates the card, initializes `struct snd_efw`, allocates a response ring buffer, registers the instance for async EFW responses, fetches hardware info, initializes duplex streams, proc, optional MIDI, PCM, hwdep, and registers the card. Hardware info populates card names, response-address capability, supported rates, MIDI ports, PCM channel counts for 1x/2x/4x modes, metering groups, firmware version, and quirk flags (`is_af9`, `is_fireworks3`). Update notifies pending EFW transactions of bus reset and refreshes streams under mutex. State includes global card bitmap, response buffer pointers, capabilities, and stream state. Dependencies are EFW commands/transactions, AMDTP/CMP stream code, ALSA core, and FireWire matching. Risks include card slot cleanup on probe failure, trusting firmware capability counts, response buffer sizing, and quirk-specific stream flags. Test signals: all ID table entries, hardware-info validation failures, response buffer module parameters, bus reset with pending transaction, and remove with open hwdep/PCM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks.h -->
## sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks.h

Purpose: shared contract for Fireworks-family driver files. It defines caps constants, response buffer parameters, physical group and metering structures, `struct snd_efw`, EFW hardware info layout, clock/transport enums, and prototypes for transactions, commands, streaming, proc, MIDI, PCM, and hwdep.

State model: `struct snd_efw` owns card/unit/card index, mutex/spinlock, kernel command sequence number, response-address and firmware quirk flags, MIDI/rate/channel capabilities, TX/RX AMDTP streams, CMP connections, active substream count, physical metering metadata, hwdep lock state, response ring buffer pointers, and AMDTP domain. Persistent hardware state is discovered through `snd_efw_hwinfo` and then cached for constraints and diagnostics. Dependencies include ALSA PCM/rawmidi/hwdep/info, FireWire, `packets-buffer`, `iso-resources`, `amdtp-am824`, `cmp`, and shared transaction helpers. Risks are structure layout compatibility with firmware big-endian command payloads, response ring pointer invariants, capped MIDI/channel group arrays, and shared lock/counter semantics across PCM/MIDI/hwdep. Test signals: compile coverage, endian conversion of `snd_efw_hwinfo`, array bounds from firmware caps, and UAPI response queue behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_command.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_command.c

Purpose: implements kernel-side Fireworks EFW command construction, response validation, hardware info/meters retrieval, transport mode setting, clock source/rate access, and sampling-rate changes. Public APIs include `snd_efw_command_get_hwinfo()`, `get_phys_meters()`, `get_clock_source()`, `get_sampling_rate()`, `set_sampling_rate()`, `set_tx_mode()`, and optional `set_resp_addr()`.

Control flow: `efw_transaction()` allocates a command/response buffer, assigns an even kernel sequence number under spinlock, fills a six-quadlet big-endian EFW header, copies parameters, runs the async transaction, validates version/category/command/status, and copies response payload. Hardware info and clock helpers convert big-endian fields to CPU order and sanitize strings. Clock setting reads current state, updates only requested fields, writes them back, then sleeps 150 ms for firmware convergence. State is the per-device `seqnum` and command-derived cached fields in callers. Dependencies are `fireworks_transaction.c`, `snd_fw_transaction`, firmware EFW categories/commands, and ALSA/device logging. Risks include sequence-number collision with userspace range, response length underflow if firmware reports too-small length, status mapping gaps, and sleep-based clock settling. Test signals: command timeout/status errors, endian conversion, changing only rate while preserving source, firmware versions with delayed clock update, and unsupported response-address changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_command.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_hwdep.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_hwdep.c

Purpose: exposes Fireworks hwdep device for node info, stream lock/unlock, kernel-to-userspace EFW response queue reads, and userspace-to-device EFW command writes. Entry point is `snd_efw_create_hwdep_device()`.

Control flow: `hwdep_read()` waits for lock-status change or queued response. Lock events are returned as `SNDRV_FIREWIRE_EVENT_LOCK_STATUS`; responses are returned with an event type header followed by as many complete EFW transactions as fit from the circular buffer, updating the shared pull pointer. `hwdep_write()` copies a userspace command, validates size and that the sequence number stays in the userspace range, then sends it to the EFW command address. IOCTL returns FireWire node info and manages stream locks via `dev_lock_count == -1`. Poll reports readable events and always writable. State is the response ring, `dev_lock_changed`, `dev_lock_count`, and wait queue. Dependencies are ALSA hwdep, Fireworks transaction format, copy_to/from_user, and FireWire UAPI. Risks include concurrent readers consuming different response windows, ring-buffer wrap/capacity assumptions, user command validation limited to size/seqnum, and lock release on close. Test signals: response wraparound, small read buffer returning `-ENOSPC`, poll/read wakeups, user command writes, compat ioctl, and lock contention with PCM/MIDI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_hwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_midi.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_midi.c

Purpose: creates Fireworks raw MIDI devices and binds MIDI substreams to AMDTP AM824 MIDI slots. Public entry point is `snd_efw_create_midi_devices()`.

Control flow: open takes the stream lock, reserves duplex streams at current rate when rate zero is passed, increments `substreams_counter`, and starts duplex streaming so MIDI can travel even without PCM. Close decrements the counter, stops/free streams when last user leaves, and releases the stream lock. Capture/playback triggers attach or detach the rawmidi substream to `efw->tx_stream` or `efw->rx_stream` using `amdtp_am824_midi_trigger()` under spinlock. Device creation uses firmware-discovered MIDI port counts and sets duplex flags only when both directions exist. State is shared stream reservation state plus per-stream AM824 MIDI substream pointers. Dependencies are ALSA rawmidi, `fireworks_stream.c`, and `amdtp-am824`. Risks include counter imbalance if start fails after reservation, direction naming confusion, and devices with zero ports. Test signals: MIDI-only streaming, mixed PCM/MIDI open/close ordering, trigger attach/detach, port-count variants, and stream lock contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_pcm.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_pcm.c

Purpose: creates Fireworks PCM devices and rate/channel constraints based on firmware-reported 1x/2x/4x AMDTP channel counts. Public entry points are `snd_efw_create_pcm_devices()` and `snd_efw_get_multiplier_mode()`.

Control flow: `freq_table` maps supported rates to multiplier modes; hardware rules constrain channel count and rate together using per-direction channel arrays. Open locks streams, initializes AM824 PCM formats/constraints, reads current clock source, and when externally clocked or already reserved restricts rate and period/buffer sizes to existing values. `hw_params` reserves duplex streams and increments `substreams_counter`; `hw_free` decrements and may stop. Prepare starts duplex and arms the appropriate AMDTP stream; trigger attaches/detaches PCM. Pointer/ack use the AMDTP domain. State is firmware capability arrays, supported rate bitmask, substream count, and domain timing. Dependencies are ALSA PCM, `amdtp-am824`, EFW clock commands, and stream reservation. Risks include assuming `freq_table` covers every advertised firmware rate, using zero channel counts, counter imbalance, and external-clock stale reads. Test signals: all multiplier modes, hardware-rule refinement, external clock restrictions, PCM plus MIDI sharing, and bus-reset recovery after prepare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_proc.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_proc.c

Purpose: provides Fireworks procfs diagnostics: clock, firmware/hardware info, physical meters, and response queue occupancy. Entry point is `snd_efw_proc_init()`.

Control flow: proc init creates a `firewire` directory and four text nodes. `proc_read_hwinfo()` allocates a hardware-info structure, fetches caps through EFW command, and prints IDs, versions, sample rates, port groups, channel counts, MIDI ports, and mixer sizes. `proc_read_clock()` prints current source/rate. `proc_read_phys_meters()` sizes a meter buffer from cached physical input/output counts, fetches meter values, and labels groups by type. `proc_read_queues_state()` reports response-ring occupancy. State is mostly read from hardware, with cached physical group metadata and response buffer pointers from `snd_efw`. Dependencies are EFW commands, ALSA info, and firmware layouts. Risks include diagnostic typo/field mismatch in the physical input group loop, firmware returning inconsistent meter counts, and partial silent output on command failure. Test signals: proc nodes under live hardware, metering sizes at group-count limits, response queue occupancy after hwdep traffic, and failure paths for EFW commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_stream.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_stream.c

Purpose: owns Fireworks duplex streaming over CMP-established AM824 streams. It initializes streams/connections/domain, configures firmware transport mode, reserves resources, starts/stops streams, handles bus reset, destroys resources, and manages stream locks.

Control flow: init creates CMP output/input connections and AM824 streams, applying Fireworks firmware quirks to TX CIP flags, initializes the domain, then sets IEC61883 transport mode. Reservation checks whether another driver owns the CMP connection, reads current sampling rate, stops and releases resources on rate changes, writes the new rate, maps rate to multiplier mode, configures stream parameters including MIDI ports, reserves CMP connections, and sets period geometry. Start establishes RX and TX CMP connections, adds streams to the domain, starts with a quirk-specific initial skip, and waits up to 1000 ms. Stop/bus-update break connections and abort PCM as needed. State includes CMP connections, AMDTP streams, domain, quirk flags, and `substreams_counter`. Dependencies are `cmp`, `amdtp-am824`, EFW clock/transport commands, and ALSA stream users. Risks include other software owning PCRs, firmware-specific DBC quirks, long startup skip cycles, partial reserve cleanup, and bus-reset connection loss. Test signals: JACK/FFADO contention, firmware quirk models, rate changes, MIDI-only reserve, timeout path, and CMP release after last substream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_transaction.c -->
## sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_transaction.c

Purpose: implements Fireworks EFW transport over FireWire async command/response addresses. It supports kernel synchronous transactions, userspace response buffering, bus-reset notification, instance routing, and global response address registration.

Control flow: kernel `snd_efw_transaction_run()` links a stack queue keyed by expected response sequence, sends a block write to the command address, waits for completion/bus reset/timeout with retries, and unlinks. The global response handler validates length/address, reads sequence number, routes kernel-range responses to matching queues and optionally to userspace debug buffer, and routes userspace-range responses to the matching device instance by card/generation/node. User responses are copied into a per-device circular buffer if enough capacity remains, then hwdep readers are woken. Bus reset marks matching pending queues for retry. State is global `instances[]`, global transaction queue list, per-device response ring, and queue waiters. Dependencies are FireWire address handlers, `snd_fw_transaction`, spinlocks, and EFW sequence ranges. Risks include stack queue lifetime, ring capacity conflict responses, exact generation/node matching after resets, timeout sensitivity, and global handler lifetime on module unload. Test signals: concurrent kernel/user transactions, bus reset during wait, response buffer overflow, debug mirroring, unregister with empty queue, and invalid response address/size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/fireworks/fireworks_transaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/isight.c -->
## sources/distributed-fs/ceph-client/sound/firewire/isight.c

Purpose: standalone ALSA capture driver for Apple iSight FireWire audio. It creates a capture-only PCM device, microphone gain/mute controls, allocates one receive isochronous context, parses proprietary audio payloads, and registers as a FireWire driver.

Control flow: probe creates `struct isight`, finds the unit CSR base, initializes ISO resources, names the card, creates PCM and mixer controls, and registers. PCM open allocates an ISO packet buffer; prepare resets buffer pointers and starts streaming. Start writes 48 kHz, allocates an ISO channel, writes device channel/speed config, enables audio, creates/queues a receive ISO context, and starts it. The packet callback validates payload signature, detects dropped samples by total-sample counter, copies big-endian S16 stereo data into vmalloc PCM buffer, advances period counters, requeues buffers, and aborts on queue failure. Controls read/write device gain and mute registers with TLV dB min/max. Remove aborts PCM, disconnects card, stops streaming under mutex, frees card, and drops unit. State includes context, packet buffer, resource channel/generation, buffer pointer, sample total, gain range, and booleans via READ/WRITE_ONCE. Dependencies are FireWire ISO context APIs, `iso-resources`, `packets-buffer`, ALSA PCM/control, and `snd_fw_transaction`. Risks include callback/teardown races, dropped-sample zero filling versus xrun, fixed 48 kHz assumptions, endian/sample layout, and bus-reset resource update failure. Test signals: capture start/stop, period elapsed timing, dropped packet handling, gain/mute control ranges, bus reset while active, and remove with open PCM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/isight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/iso-resources.c -->
## sources/distributed-fs/ceph-client/sound/firewire/iso-resources.c

Purpose: shared helper for FireWire isochronous channel and bandwidth allocation. It exports init/destroy/allocate/update/free functions for `struct fw_iso_resources`.

Control flow: init sets all channels allowed, stores the unit, initializes a mutex, and marks unallocated. Allocation computes bandwidth from max payload plus ISO headers at bus speed, snapshots card generation and bandwidth overhead under card lock, waits one second after bus reset, and calls `fw_iso_resource_manage()` to allocate channel/bandwidth. It retries if another reset occurs, stores channel/generation/overhead on success, and logs exhaustion/errors. Update recalculates overhead for a new generation and reallocates the same channel; non-reset failures clear `allocated`. Free deallocates the stored channel/bandwidth for the saved generation. State is per-resource channel, bandwidth, overhead, generation, unit, mask, mutex, and allocated flag. Dependencies are FireWire core resource manager, card lock/reset timing, jiffies, and logging. Risks include interruptible wait returning `-ERESTARTSYS`, bandwidth overhead estimation from gap count, stale generation on free after repeated resets, and callers forgetting update/free. Test signals: allocation after bus reset, channel mask restrictions, exhausted bandwidth, update failure while streaming, destroy warning when allocated, and speed-dependent bandwidth math.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/iso-resources.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/iso-resources.h -->
## sources/distributed-fs/ceph-client/sound/firewire/iso-resources.h

Purpose: public interface for shared FireWire isochronous resource management. It defines `struct fw_iso_resources` and prototypes for init, destroy, allocate, update, and free.

State model: callers may adjust `channels_mask` after init; the rest is private state recording the target unit, mutex, allocated channel, bandwidth without overhead, current overhead, valid generation, and allocation flag. Integration requires callers to allocate before starting ISO streams, call `fw_iso_resources_update()` from FireWire `.update` after bus reset, and call `fw_iso_resources_free()` before destroy. Dependencies are Linux mutex/types and forward-declared `fw_unit`. Risks are API misuse: using `channel` without successful allocation, destroying while allocated, failing to update after reset, or relying on private fields across modules. Test signals: compile coverage for all FireWire audio drivers, lockdep around resource mutex, channel-mask-limited allocation, and WARN_ON in destroy when cleanup paths are incomplete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/iso-resources.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/lib.c -->
## sources/distributed-fs/ceph-client/sound/firewire/lib.c

Purpose: shared FireWire audio transaction helper implementation. It exports `snd_fw_transaction()`, a synchronous wrapper around `fw_run_transaction()` with generation handling, retries, and error logging.

Control flow: the helper derives the current generation and node ID from the target unit’s parent device unless `FW_FIXED_GENERATION` is supplied. It runs the transaction at the device max speed, returns success on `RCODE_COMPLETE`, returns `-EAGAIN` on fixed-generation mismatch, treats permanent type/address errors or three failed tries as `-EIO`, and sleeps 20 ms between retryable failures. It suppresses logging when `FW_QUIET` is set. State is only local retry/generation tracking; persistence is in the FireWire core and target device. Dependencies are Linux FireWire core, `lib.h` flags, module exports, and device logging. Risks include retrying non-idempotent writes after transient errors, stale node ID if memory barriers are bypassed by callers elsewhere, fixed-generation callers needing explicit generation bits, and broad `-EIO` error collapse. Test signals: successful read/write, permanent address error, generation mismatch with fixed flag, retryable timeout, quiet mode, and use from probe/update/remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/lib.h -->
## sources/distributed-fs/ceph-client/sound/firewire/lib.h

Purpose: public header for miscellaneous FireWire audio helpers. It declares `snd_fw_transaction()`, transaction flags `FW_GENERATION_MASK`, `FW_FIXED_GENERATION`, `FW_QUIET`, and inline `rcode_is_permanent_error()`.

The header has no runtime state but defines semantics used across the FireWire audio drivers. Callers encode an optional generation in the low eight flag bits and use fixed generation when a register write must be tied to a resource allocation generation. `rcode_is_permanent_error()` classifies type and address errors as not worth retrying and is reused by async MIDI completion code. Dependencies are FireWire constants, Linux types/scheduling, and rawmidi includes for broader helper consumers. Risks are flag-bit overlap if future flags exceed the mask, caller mistakes when combining fixed generation and generation value, and too-narrow permanent-error classification for some devices. Test signals: compile coverage, transaction calls with fixed generation, quiet error paths, and async completion paths that branch on permanent errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/Makefile -->
## sources/distributed-fs/ceph-client/sound/firewire/motu/Makefile

Purpose: Kbuild fragment for the MOTU FireWire driver. It adds the source directory to `amdtp-motu.o` include flags for local trace headers and links `snd-firewire-motu.o` from top-level driver, AMDTP codec, transaction, stream, proc, PCM, MIDI, hwdep, protocol v1/v2/v3, and register/command DSP parsers under `CONFIG_SND_FIREWIRE_MOTU`.

There is no runtime state, but the object list shows that the requested files are only part of a larger MOTU module. Dependencies are Kbuild, local tracepoint include path, and the config symbol. Risks include missing parser/protocol objects causing unresolved references from `amdtp-motu.c` and `motu-hwdep.c`, or omitting the include path causing trace header generation failures. Test signals: module build with tracing enabled, modpost symbol resolution, and `CFLAGS_amdtp-motu.o` still matching the trace include path after file moves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/amdtp-motu-trace.h -->
## sources/distributed-fs/ceph-client/sound/firewire/motu/amdtp-motu-trace.h

Purpose: tracepoint definitions for dumping MOTU AMDTP source packet headers and embedded message data. It declares helper prototypes consumed by trace assignment code and defines `data_block_sph` and `data_block_message` events under trace system `snd_firewire_motu`.

Control flow at trace time: each event records FireWire source/destination node IDs based on stream direction, data block count, and a dynamic array filled by `copy_sph()` or `copy_message()` implemented in `amdtp-motu.c`. The include footer sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` so `trace/define_trace.h` can generate trace code. State is only per-event trace payload; there is no persistent driver state. Dependencies are Linux tracepoint infrastructure, `struct amdtp_stream`, and local helper functions marked `__maybe_unused` in the C file. Risks include helper prototype drift, dynamic array size tied to data block count, trace overhead on high-rate streams, and local include path requirements in the Makefile. Test signals: kernel build with tracepoints, enabling each event while streaming, validating node IDs by direction, and ensuring trace output arrays match packet data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/amdtp-motu-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/amdtp-motu.c -->
## sources/distributed-fs/ceph-client/sound/firewire/motu/amdtp-motu.c

Purpose: implements MOTU-specific AMDTP packet processing for PCM, MIDI, source packet headers, event-offset caching, DSP message parsing, and tracepoints. Public APIs are `amdtp_motu_init()`, `amdtp_motu_set_parameters()`, `amdtp_motu_add_pcm_hw_constraints()`, and `amdtp_motu_midi_trigger()`.

Control flow: parameter setup maps rate to mode, computes data block size from message and PCM chunks, configures AMDTP stream, and stores PCM/MIDI offsets plus MIDI byte-rate interval. Capture processing caches event offsets from SPH timestamps, copies 24-bit packed PCM into S32 ALSA buffers, receives MIDI bytes, dispatches register- or command-DSP parsers based on model flags, and optionally emits trace events. Playback processing writes PCM or silence, writes rate-limited MIDI bytes, reconstructs SPH timestamps from cached capture offsets, and emits traces. Init selects quirks for protocol v3 and specific models, sets `s->sph`, and uses fixed FDF for outbound packets. State is per-stream protocol data and shared `amdtp_motu_cache` head/tail/cycle counts. Dependencies are AMDTP core, MOTU spec/protocol flags, DSP parser modules, ALSA rawmidi/PCM, and tracepoints. Risks include cache underrun/overrun between capture and playback, packed 24-bit offset mistakes, MIDI rate limiting for only one port pointer, protocol-v3 invalid CIP quirks, and parser calls from streaming context. Test signals: packet format variants, SPH continuity, PCM wraparound, MIDI timing, DSP meter parsing, tracepoint output, and stream restart resetting cache cycle counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/amdtp-motu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-command-dsp-message-parser.c -->
## sources/distributed-fs/ceph-client/sound/firewire/motu/motu-command-dsp-message-parser.c

Purpose: parses hardware meter messages embedded in isochronous packets for MOTU models whose DSP is configured by asynchronous commands. Public APIs are parser allocation/init, parse, and meter-copy functions.

Control flow: `new()` allocates a parser in card-managed memory and initializes its spinlock. `init()` resets state and sets a message interval based on CIP sampling-frequency code: every data block at base rates, every second at double rates, every fourth at quad rates. `parse()` walks packet descriptors/data blocks under parser lock, consumes one byte at `FRAGMENT_POS` when the interval matches, first searches for a nonzero fragment stream, waits for the all-ones image-end marker, then assembles four fragments per meter value into 32-bit entries until the next image-end marker resets positions. `copy_meter()` snapshots the meter under spinlock. State is parser state machine, interval, counters, fragment position, value index, rolling 64-bit value, and meter array. Dependencies are `amdtp_stream` packet descriptors, `snd_motu` container, and FireWire MOTU UAPI meter structure. Risks include resynchronization after corrupted fragments, skipped last two invalid values, lock hold time over packet batches, and relying on hard-coded byte offsets. Test signals: parser initialization per rate, image-end detection, meter value assembly, corrupted stream recovery, and concurrent ioctl meter copies during streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-command-dsp-message-parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-hwdep.c -->
## sources/distributed-fs/ceph-client/sound/firewire/motu/motu-hwdep.c

Purpose: creates the MOTU hwdep device for FireWire node info, stream lock/unlock, device notification events, register-DSP change events, and DSP meter/parameter ioctls. Entry point is `snd_motu_create_hwdep_device()`.

Control flow: read waits for lock changes, a generic async notification message, or queued register-DSP events. It returns lock status, MOTU notification, or a variable-length register-DSP change event with copied event words. Poll mirrors the same readiness conditions. IOCTL returns node info, manages stream locks through `dev_lock_count`, and copies register-DSP meter/parameter or command-DSP meter snapshots depending on model flags. State includes `motu->msg`, `dev_lock_changed`, register-DSP parser queues, command-DSP meter state, and `motu->hwdep`. Dependencies are ALSA hwdep, FireWire UAPI, MOTU parser modules, spinlocks, and copy_to_user. Risks include mixed locking between `motu->lock` and parser locks, variable-length read truncation, event loss if parser queue overflows elsewhere, and model-flag mismatch returning wrong ioctl support. Test signals: notification read/poll, lock contention with PCM/MIDI, all MOTU-specific ioctls by model flag, compat ioctl, and event reads with small buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-hwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-midi.c -->
## sources/distributed-fs/ceph-client/sound/firewire/motu/motu-midi.c

Purpose: creates a duplex one-port MOTU raw MIDI device and starts/stops the shared duplex stream for MIDI-only use. Public entry point is `snd_motu_create_midi_devices()`.

Control flow: open takes the MOTU stream lock, reserves duplex streaming at the current clock rate by passing rate zero, increments `substreams_counter`, and starts streaming. On failure it releases the stream lock and rolls back the counter. Close decrements the counter, stops/free streams when it reaches zero, and releases the lock. Capture/playback triggers attach or detach the rawmidi substream to `motu->tx_stream` or `motu->rx_stream` through `amdtp_motu_midi_trigger()` under spinlock. Device creation names input/output substreams and sets duplex rawmidi flags. State is shared with MOTU stream code plus per-stream MIDI pointer in `amdtp-motu.c`; this file itself persists no queue. Dependencies are ALSA rawmidi, MOTU stream reservation/start/stop, and AMDTP MOTU MIDI trigger. Risks include one-port assumption, counter imbalance across mixed PCM/MIDI users, start failure after reservation, and direction interpretation. Test signals: MIDI-only open/close, concurrent PCM and MIDI users, trigger attach/detach, stream-lock contention, and bus reset while MIDI is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/motu/motu-midi.c -->
