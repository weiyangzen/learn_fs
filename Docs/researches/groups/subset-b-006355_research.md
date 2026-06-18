# Research: subset-b-006355

Grouped research for `subset-b-006355`. Each section preserves the original source path in its title and is delimited for deterministic splitting into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/rawmidi.c -->
# sources/distributed-fs/ceph-client/sound/core/rawmidi.c

Purpose: implements ALSA's midlevel raw MIDI character-device and kernel API for byte-stream MIDI v1.0 devices, with UMP-aware device enumeration and input timestamp framing support. It registers native `/dev/snd/midiC*D*` devices, optional OSS raw MIDI minors, per-card control ioctls, and proc status entries.

Important APIs, types, and functions: exported constructors and lifecycle APIs include `snd_rawmidi_init()`, `snd_rawmidi_new()`, `snd_rawmidi_free()`, and `snd_rawmidi_set_ops()`. Kernel stream APIs include `snd_rawmidi_kernel_open()`, `snd_rawmidi_kernel_release()`, `snd_rawmidi_kernel_read()`, `snd_rawmidi_kernel_write()`, `snd_rawmidi_receive()`, `snd_rawmidi_transmit_peek()`, `snd_rawmidi_transmit_ack()`, `snd_rawmidi_transmit()`, `snd_rawmidi_transmit_empty()`, `snd_rawmidi_proceed()`, `snd_rawmidi_drop_output()`, `snd_rawmidi_drain_output()`, and `snd_rawmidi_drain_input()`. User entry points are collected in `snd_rawmidi_f_ops`, and control-device entry points are handled by `snd_rawmidi_control_ioctl()`.

Control flow: open resolves native or OSS minor data, pins the card module, adds the file to the card, allocates `struct snd_rawmidi_file`, and waits on `open_wait` until a matching input/output substream can be assigned. `open_substream()` creates `struct snd_rawmidi_runtime`, calls the low-level stream `open` op, marks the substream opened, records PID ownership, and increments stream open counts. Reads trigger input and drain `runtime->buffer` through `snd_rawmidi_kernel_read1()`; writes fill output buffers through `snd_rawmidi_kernel_write1()` and trigger low-level output. Low-level drivers push input with `snd_rawmidi_receive()` and pull output with transmit peek/ack helpers. Close drains or drops streams, synchronizes buffer users, calls low-level close, frees runtime memory, and wakes blocked openers.

State and persistence: state is in memory only. Global `snd_rawmidi_devices` is protected by `register_mutex`; each device has `open_mutex`, `open_wait`, stream substream lists, proc entry, optional OSS registration count, and optional sequencer bridge device. Each substream has `opened`, `append`, `use_count`, PID, byte counters, active sensing, framing mode, clock type, and a spinlock-protected runtime ring buffer with `appl_ptr`, `hw_ptr`, `avail`, `avail_min`, `xruns`, `drain`, `buffer_ref`, and optional event work. UMP rawmidi devices use aligned buffer sizes and packet counts via `runtime->align`.

Dependencies and integration: depends on ALSA core device/card/minor/control/proc APIs, low-level `struct snd_rawmidi_ops`, optional OSS emulation, optional sequencer autobridge through `snd_seq_device_new()`, and optional UMP endpoint/block ioctls. Sequencer MIDI clients call the kernel open/read/write/release APIs, while control clients enumerate devices and set preferred subdevices through registered control ioctls.

Risks: user copy paths temporarily drop spinlocks after advancing pointers, so `buffer_ref` and resize synchronization are critical. Append mode requires whole-message space and rejects blocking append opens. Drain has timeout/error paths and sends active-sensing shutdown bytes. Input timestamp framing requires 32-byte-aligned buffers, and UMP alignment can silently trim counts. `snd_rawmidi_input_params()` computes an error but currently returns `0` unconditionally after validation logic, so callers may not see invalid mode errors if that behavior is not intentional. Device disconnect must wake open/read/write waiters and remove all native/OSS registrations without racing openers.

Test signals: exercise native and OSS opens, blocking/nonblocking open contention, read/write/poll behavior, drop/drain, active sensing close, buffer resize while busy, status/xrun reset, timestamp framing with each clock type, UMP device enumeration and endpoint/block ioctls, sequencer bridge registration, disconnect wakeups, and proc output while streams are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/rawmidi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/rawmidi_compat.c -->
# sources/distributed-fs/ceph-client/sound/core/rawmidi_compat.c

Purpose: provides 32-bit compat ioctl handling for the raw MIDI API when included by `rawmidi.c` under `CONFIG_COMPAT`.

Important APIs, types, and functions: defines packed `struct snd_rawmidi_params32` and `struct compat_snd_rawmidi_status64`, compat ioctl numbers, `snd_rawmidi_ioctl_params_compat()`, `snd_rawmidi_ioctl_status_compat64()`, and `snd_rawmidi_ioctl_compat()`.

Control flow: compat dispatch maps commands with pointer conversion through `compat_ptr()`. Simple commands delegate to native `snd_rawmidi_ioctl()`. Parameters are copied field-by-field into native `struct snd_rawmidi_params`, then routed to input or output parameter setters. Status calls native status helpers and copies size-converted availability/xrun counters back to 32-bit userspace.

State and persistence: no independent persistent state. It mutates the same `struct snd_rawmidi_file` substream runtime settings and xrun counters reached by the native ioctl path.

Dependencies and integration: depends on native rawmidi helpers in the including translation unit, Linux compat APIs, and optional UMP ioctl passthrough.

Risks: field-by-field conversion must preserve ABI layout and avoid leaking uninitialized native padding. Size truncation of `avail` and `xruns` into 32-bit compat fields can lose high bits. The compat params path does not apply the native `user_pversion` legacy-mode adjustment because it bypasses `SNDRV_RAWMIDI_IOCTL_PARAMS` native dispatch.

Test signals: 32-bit userspace ioctl tests should cover params for input/output, status32/status64, invalid stream ids, missing read/write substreams, UMP passthrough when enabled, and pointer fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/rawmidi_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/Kconfig -->
# sources/distributed-fs/ceph-client/sound/core/seq/Kconfig

Purpose: defines build-time configuration for ALSA sequencer support and optional sequencer clients/transports.

Important symbols: `SND_SEQUENCER` enables the sequencer core and selects `SND_TIMER` plus `SND_SEQ_DEVICE`. `SND_SEQ_DUMMY` builds the MIDI-through client. `SND_SEQUENCER_OSS` enables `/dev/sequencer` and `/dev/music` OSS emulation and selects `SND_SEQ_MIDI_EVENT`. `SND_SEQ_HRTIMER_DEFAULT` controls default timer backend. Internal tristates include `SND_SEQ_MIDI_EVENT`, `SND_SEQ_MIDI`, `SND_SEQ_MIDI_EMUL`, `SND_SEQ_VIRMIDI`, and `SND_SEQ_UMP_CLIENT`; `SND_SEQ_UMP` enables Universal MIDI Packet support.

Control flow: the menu is nested under `if SND_SEQUENCER`, so optional clients only exist when the core sequencer is enabled. Default selections wire MIDI rawmidi support into the sequencer and let UMP client support follow both `SND_UMP` and `SND_SEQ_UMP`.

State and persistence: no runtime state; persistent impact is kernel configuration and module availability.

Dependencies and integration: integrates the source files in this folder with ALSA timer, rawmidi, OSS emulation, MIDI event conversion, and UMP support.

Risks: disabling `SND_SEQ_MIDI_EVENT` indirectly by omitting OSS or MIDI sequencer features removes conversion helpers needed by compatibility paths. Timer default choices alter runtime behavior even though the sequencer module parameters can override timer IDs.

Test signals: config-matrix builds for built-in/module/off combinations, with OSS emulation requiring `SND_OSSEMUL`, hrtimer default with and without `SND_HRTIMER`, and UMP support with and without `SND_UMP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/Makefile -->
# sources/distributed-fs/ceph-client/sound/core/seq/Makefile

Purpose: maps sequencer Kconfig symbols to ALSA sequencer object files and modules.

Important build objects: `snd-seq-y` contains core files `seq.o`, `seq_lock.o`, `seq_clientmgr.o`, `seq_memory.o`, `seq_queue.o`, `seq_fifo.o`, `seq_prioq.o`, `seq_timer.o`, `seq_system.o`, and `seq_ports.o`. Optional pieces add `seq_info.o` for procfs and `seq_ump_convert.o` for UMP. Separate modules are built for MIDI, MIDI emulation, MIDI event conversion, dummy, virmidi, and UMP client support.

Control flow: `obj-$(CONFIG_SND_SEQUENCER)` builds the core `snd-seq.o`; `obj-$(CONFIG_SND_SEQUENCER_OSS)` descends into `oss/`; other `obj-*` lines produce optional companion modules.

State and persistence: no runtime state; it controls binary composition and symbol availability.

Dependencies and integration: mirrors `Kconfig` and establishes which files provide exported APIs consumed by rawmidi bridges, OSS emulation, dummy client, and UMP conversion.

Risks: object grouping matters because `seq_clientmgr.c` includes `seq_compat.c` directly, and `seq_info.o` is only present with procfs. Missing `seq_midi_event.o` breaks MIDI byte/event conversion users.

Test signals: validate all configured modules link, particularly `CONFIG_SND_PROC_FS=n`, `CONFIG_SND_SEQ_UMP=y`, and OSS module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/Makefile -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/Makefile

Purpose: builds the OSS sequencer emulation module from its component files.

Important build objects: `snd-seq-oss-y` combines device registration, open/close, timer, ioctl, event conversion, read/write, synth, MIDI, read queue, and write queue objects.

Control flow: `obj-$(CONFIG_SND_SEQUENCER_OSS)` emits `snd-seq-oss.o` only when OSS sequencer emulation is enabled.

State and persistence: no runtime state. The build composition makes the OSS layer a single module that registers both OSS minors and the synth driver.

Dependencies and integration: depends on the parent sequencer module and `SND_SEQ_MIDI_EVENT` selected by Kconfig.

Risks: all OSS subcomponents are linked together, so missing one object leaves unresolved internal APIs. Procfs support is conditional inside `seq_oss.c`, not in this Makefile.

Test signals: module link/load tests for `snd-seq-oss`, with and without procfs and as built-in versus module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss.c

Purpose: top-level OSS sequencer emulation module. It registers `/dev/sequencer` and `/dev/music`, the OSS synth sequencer-device driver, file operations, module init/exit, and optional proc output.

Important APIs, types, and functions: defines `seq_oss_synth_driver`, `alsa_seq_oss_init()`, `alsa_seq_oss_exit()`, `odev_open()`, `odev_release()`, `odev_read()`, `odev_write()`, `odev_ioctl()`, `odev_poll()`, `register_device()`, `unregister_device()`, `register_proc()`, and `unregister_proc()`.

Control flow: init registers OSS minors, proc entry, creates the OSS sequencer kernel client, registers the synth-driver probe/remove hooks, then initializes the MIDI synth pseudo-device. File open maps the minor to synth or music mode and delegates to `snd_seq_oss_open()`. File operations forward to the per-application `seq_oss_devinfo`; ioctl serializes most commands with `register_mutex` but leaves `SNDCTL_SEQ_SYNC` unlocked because it can wait.

State and persistence: holds a module-level `register_mutex`, optional proc `info_entry`, and the registered OSS device state managed by ALSA core. Per-open state lives in `seq_oss_init.c`'s `seq_oss_devinfo`.

Dependencies and integration: depends on ALSA OSS minor registration, `seq_oss_device.h` facade functions, synth registration in `seq_oss_synth.c`, and procfs when enabled.

Risks: init unwind must unregister in exact reverse order to avoid stale OSS minors or synth driver callbacks. File private data must be valid for all forwarded operations. `SNDCTL_SEQ_SYNC` deliberately bypasses the global mutex, so sync code must tolerate concurrent release/reset behavior.

Test signals: load/unload module, open both OSS minors, issue read/write/ioctl/poll on valid and released file descriptors, verify proc `oss` output, and force init failures in each registration stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_device.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_device.h

Purpose: central private header for OSS sequencer emulation state, limits, file-mode helpers, and integration wrappers into the ALSA sequencer core.

Important APIs and types: defines `SNDRV_SEQ_OSS_MAX_CLIENTS`, synth/MIDI device limits, version strings, `reltime_t`, `abstime_t`, `struct seq_oss_chinfo`, `struct seq_oss_synthinfo`, and `struct seq_oss_devinfo`. Declares open/release/read/write/ioctl/poll/reset functions and proc readers. Inline helpers include `is_read_mode()`, `is_write_mode()`, `is_nonblock_mode()`, `snd_seq_oss_dispatch()`, `snd_seq_oss_control()`, and `snd_seq_oss_fill_addr()`.

Control flow: other OSS source files pass a `seq_oss_devinfo` through these declarations. Event writers call `snd_seq_oss_fill_addr()` before dispatch/enqueue; ioctl/writeq paths use `snd_seq_oss_control()` to issue sequencer ioctls against the OSS kernel client.

State and persistence: `seq_oss_devinfo` is per open application and stores client/port/queue ids, mode flags, discovered MIDI and synth counts, per-open synth metadata, read/write queues, and timer state. It is allocated on open and freed by the sequencer port private-free callback.

Dependencies and integration: includes ALSA core, rawmidi, sequencer kernel, OSS legacy API, info/proc, and `seq_clientmgr.h` for kernel client dispatch/control.

Risks: this header defines ownership assumptions for per-open state. Incorrect mode helper use can allow read/write on the wrong queue. `snd_seq_oss_dispatch()` bypasses queueing by using direct kernel dispatch, so callers must set event timestamps and destinations correctly.

Test signals: compile coverage for all OSS files, static checks of mode-guarded entry points, and runtime open in synth/music/read/write/nonblocking combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_event.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_event.c

Purpose: converts legacy OSS sequencer event records into ALSA sequencer events, handles echo events returning from the sequencer, and forwards incoming ALSA events to the OSS MIDI input path.

Important APIs and functions: exports `snd_seq_oss_process_event()` and `snd_seq_oss_event_input()`. Internal converters include `old_event()`, `extended_event()`, `chn_voice_event()`, `chn_common_event()`, `timing_event()`, `local_event()`, `note_on_event()`, `note_off_event()`, `set_note_event()`, `set_control_event()`, and `set_echo_event()`.

Control flow: write-side records are classified by OSS opcode. Timing records may update timer state, sysex goes to synth sysex conversion, `SEQ_MIDIPUTC` feeds the MIDI byte encoder, echo/private events are specially translated, and note/control events resolve a synth target before filling ALSA event data. Input-side `snd_seq_oss_event_input()` handles `SNDRV_SEQ_EVENT_ECHO` locally, waking write sync for `SEQ_SYNCTIMER` or enqueueing echo records to the read queue; non-echo events go to `snd_seq_oss_midi_input()`.

State and persistence: mutates per-open synth channel tracking (`seq_oss_chinfo`) for process-events mode, timer state through timer helpers, read queue content for echoes, and MIDI coder state indirectly through the MIDI path.

Dependencies and integration: depends on OSS legacy event definitions, `seq_oss_synth.c` for device addressing and raw/sysex callbacks, `seq_oss_midi.c` for byte output/input, timer/readq/writeq helpers, and ALSA sequencer event formats.

Risks: legacy encodings have mode-specific validity rules; accepting old 4-byte events in `/dev/music` mode would break ABI expectations. Channel and device indexes must be nospec-bounded. The note-on volume-control convention for note 255 depends on per-voice state. Some endian-sensitive echo construction is explicitly noted in code.

Test signals: exercise old, extended, channel voice/common, sysex, MIDI putc, echo, private, and timing records in synth and music modes; validate invalid opcode rejection; verify echo readback and write-sync wakeups; fuzz device/channel indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_event.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_event.h

Purpose: defines the binary OSS sequencer event-record layouts consumed and produced by the OSS emulation layer.

Important APIs and types: defines `SHORT_EVENT_SIZE`, `LONG_EVENT_SIZE`, `struct evrec_short`, `evrec_note`, `evrec_timer`, `evrec_extended`, `evrec_long`, `evrec_voice`, `evrec_sysex`, and `union evrec`. Declares `snd_seq_oss_process_event()`, `snd_seq_oss_process_timer_event()`, and `snd_seq_oss_event_input()`. Macros `ev_is_long()` and `ev_length()` classify record sizes from opcode values.

Control flow: read/write code uses the macros to decide how many bytes to copy; event conversion code casts the union to the format matching the opcode.

State and persistence: no independent state; it defines the byte ABI stored in read queues and copied to/from userspace.

Dependencies and integration: includes `seq_oss_device.h` for device context and is shared by readq, writeq, timer, rw, ioctl, event, MIDI, and synth code.

Risks: layout, packing-by-C ABI, and opcode-size classification must match OSS userspace expectations. Any change would be ABI-visible. Union casts rely on correct opcode validation before interpreting fields.

Test signals: compile-time size checks through ABI tests, userspace read/write compatibility tests for 4-byte and 8-byte records, and round-trip echo/timestamp records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_init.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_init.c

Purpose: owns OSS sequencer kernel-client creation, per-application open/release/reset, discovery of MIDI ports from sequencer announcements, and per-open queue/timer allocation.

Important APIs and functions: exports `snd_seq_oss_create_client()`, `snd_seq_oss_delete_client()`, `snd_seq_oss_open()`, `snd_seq_oss_release()`, `snd_seq_oss_reset()`, and proc `snd_seq_oss_system_info_read()`. Internal helpers include `receive_announce()`, `translate_mode()`, `create_port()`, `delete_port()`, `alloc_seq_queue()`, `delete_seq_queue()`, `free_devinfo()`, and async MIDI lookup work.

Control flow: module init creates a fixed OSS kernel client, creates a receiver port, subscribes it to system announcements, and schedules a scan of existing MIDI ports. Each open allocates `seq_oss_devinfo`, reserves an application slot, discovers synth/MIDI devices, creates an ALSA port, creates a locked queue, initializes read/write queues by file mode, initializes a timer, sets file private data, and opens MIDI devices according to synth/music mode. Release removes the client table slot, resets devices/queues/timer, cleans synth/MIDI subscriptions, detaches the port, and deletes the queue; actual `dp` memory is freed by the port callback.

State and persistence: module state includes `system_client`, `system_port`, `num_clients`, `client_table`, async lookup work, and `maxqlen` module parameter. Per-open state persists until port detach triggers `free_devinfo()`.

Dependencies and integration: depends on sequencer kernel-client APIs, system announcement events, synth/MIDI/readq/writeq/timer/event components, and ALSA queue ioctls.

Risks: open error paths call cleanup/delete helpers before all fields may be initialized, so sentinel values are important. `client_table` is bounded to 16 applications. Async lookup must be cancelled before deleting the system client. The proc loop iterates `num_clients` rather than the full table, which can miss sparse high-index opens after lower-index closes.

Test signals: create/delete OSS client, open many applications up to limit, open with no devices, force queue/port/readq/writeq/timer allocation failure, process system port start/change/exit announcements, verify release frees queue/port and cancels async work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_ioctl.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_ioctl.c

Purpose: implements OSS sequencer ioctl compatibility for timer control, reset/sync, device enumeration/info, MIDI open tests, queue counts, and synth-driver passthrough.

Important APIs and functions: exports `snd_seq_oss_ioctl()`. Helpers copy synth and MIDI info to userspace (`snd_seq_oss_synth_info_user()`, `snd_seq_oss_midi_info_user()`) and dispatch out-of-band events (`snd_seq_oss_oob_user()`).

Control flow: timer ioctls are routed to `snd_seq_oss_timer_ioctl()`. Reset/panic reset per-open state. `SNDCTL_SEQ_SYNC` loops on `snd_seq_oss_writeq_sync()` until the queued echo confirms completion or a signal interrupts. Device info commands copy legacy `synth_info`/`midi_info`. Unknown write-mode commands fall through to synth ioctl handling for device 0.

State and persistence: mutates timer tempo/timebase/running state, readq pre-event timeout, writeq output-room threshold, MIDI open subscriptions, and synth/device reset state.

Dependencies and integration: depends on readq/writeq/timer/synth/MIDI/event conversion modules and OSS legacy ioctl constants.

Risks: some legacy commands intentionally return success without doing work; tests must distinguish compatibility stubs from missing handling. `SNDCTL_SEQ_PANIC` resets but returns `-EINVAL`, matching historical behavior but surprising to callers. Default passthrough can issue arbitrary synth ioctls when opened for write.

Test signals: ioctl matrix covering timer commands in synth/music mode, sync with echo delivery and signal interruption, get input/output counts, MIDI/synth info copy faults, threshold clamping, pretime conversion, out-of-band event dispatch, and unsupported command behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_midi.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_midi.c

Purpose: tracks ALSA sequencer MIDI ports exposed through OSS emulation, manages per-open subscriptions, encodes OSS MIDI bytes to ALSA events, and decodes ALSA events back to OSS read records.

Important APIs and functions: exports `snd_seq_oss_midi_lookup_ports()`, `snd_seq_oss_midi_check_new_port()`, `snd_seq_oss_midi_check_exit_port()`, `snd_seq_oss_midi_clear_all()`, setup/cleanup/open/close/reset helpers, `snd_seq_oss_midi_putc()`, `snd_seq_oss_midi_input()`, `snd_seq_oss_midi_filemode()`, `snd_seq_oss_midi_make_info()`, and `snd_seq_oss_midi_get_addr()`. Internal state is `struct seq_oss_midi` with client/port/capability/open/coder/devinfo/use-lock fields.

Control flow: lookup walks sequencer clients/ports and registers generic MIDI ports with read or write subscription capability. Open checks permissions and subscribes OSS app port to MIDI port for write, MIDI port to app port for read with timestamping, and records ownership by `seq_oss_devinfo`. Close unsubscribes. Output bytes are encoded by `snd_midi_event_encode_byte()` and addressed to the target port. Input events are matched by source client/port, converted either to synth-style OSS records in `/dev/music` mode or MIDI byte records in synth mode, and timestamped into the read queue.

State and persistence: global `midi_devs[]` and `max_midi_devs` are protected by `register_lock`; each MIDI device uses `use_lock` for removal synchronization and `open_mutex` for subscription state. Per-open `dp->max_mididev` snapshots available devices.

Dependencies and integration: depends on sequencer kernel ioctls for client/port queries and subscriptions, `snd_midi_event` encoder/decoder, readq/timer helpers, and system announcement handling from `seq_oss_init.c`.

Risks: one `seq_oss_midi` can be opened by only one OSS app at a time; `-EBUSY` is expected. Removal must clear the table, drop the lookup reference, synchronize `use_lock`, and free coder memory. Capability masks combine direct and subscription caps, so permission tests must remain exact. `send_midi_event()` starts the timer when receiving while stopped, but its local `len` may be set by the start helper before being overwritten by decode.

Test signals: register/remove MIDI ports, duplicate detection, max-device limit, read/write subscription open and close, busy opens by two apps, byte encoding with running status, sysex decode into readq, timestamp insertion, reset all-notes-off/controller events, and proc capability output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_midi.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_midi.h

Purpose: declares the OSS MIDI-device management interface shared by open/reset, event conversion, ioctl, and proc code.

Important APIs: declarations cover discovery (`lookup_ports`, `check_new_port`, `check_exit_port`, `clear_all`), per-open setup/cleanup, open/close/reset, byte output, ALSA input callback, mode query, legacy `midi_info` creation, and address lookup.

Control flow: `seq_oss_init.c` calls setup/open/cleanup and announcement handlers; `seq_oss_event.c` calls `putc` for `SEQ_MIDIPUTC`; `seq_oss_ioctl.c` queries info/open tests; synth MIDI emulation uses address and open helpers.

State and persistence: no state itself; describes functions manipulating `seq_oss_midi.c` globals and `seq_oss_devinfo` snapshots.

Dependencies and integration: includes the central OSS device header and OSS legacy definitions for `struct midi_info`.

Risks: callers must pair open/cleanup and respect `dp->max_mididev` bounds enforced inside the implementation. Input callback may run in atomic contexts, so exported functions used there must not sleep except where documented.

Test signals: compile users of all prototypes and run OSS MIDI discovery/open/input/output tests through the public interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_midi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_readq.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_readq.c

Purpose: implements the per-open OSS MIDI input/read queue as a fixed-size circular buffer of `union evrec` records.

Important APIs and functions: exports `snd_seq_oss_readq_new()`, `snd_seq_oss_readq_delete()`, `snd_seq_oss_readq_clear()`, `snd_seq_oss_readq_puts()`, `snd_seq_oss_readq_sysex()`, `snd_seq_oss_readq_put_event()`, `snd_seq_oss_readq_pick()`, `snd_seq_oss_readq_wait()`, `snd_seq_oss_readq_free()`, `snd_seq_oss_readq_poll()`, `snd_seq_oss_readq_put_timestamp()`, and proc `snd_seq_oss_readq_info_read()`.

Control flow: producers enqueue MIDI byte records, expanded sysex bytes, echo records, and timestamp records. Consumers lock the queue, peek with `pick()`, copy to userspace, then advance with `free()`. Blocking reads wait on `midi_sleep` with `pre_event_timeout`; poll registers the same wait queue.

State and persistence: per queue state includes record array, max length, current length, head/tail indexes, timeout, last input timestamp, wait queue, and spinlock. It persists only for an open OSS file.

Dependencies and integration: used by read/write file paths, event input, MIDI input conversion, ioctl pretime/count commands, and proc diagnostics. Uses `snd_seq_dump_var_event()` to expand ALSA variable sysex events.

Risks: queue-full threshold is `maxlen - 1`, so one slot is reserved to distinguish full/empty. `snd_seq_oss_readq_poll()` reads `qlen` without taking the spinlock, which is lightweight but racy for exact counts. Timestamp insertion updates `input_time` after enqueue attempts and does not propagate queue-full failure to callers.

Test signals: enqueue/dequeue wraparound, full queue behavior, blocking read timeout and signal interruption via caller, poll readiness, sysex expansion, timestamp de-duplication in synth and music modes, and clear wakeup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_readq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_readq.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_readq.h

Purpose: defines the OSS read queue structure and exported queue operations.

Important APIs and types: `struct seq_oss_readq` stores a `union evrec` ring, length/capacity/head/tail, pre-event timeout, last input timestamp, wait queue, and spinlock. It declares allocation, deletion, clear, poll, enqueue, sysex, timestamp, pick, wait, and free operations plus lock/unlock macros.

Control flow: file read code uses lock/pick/free; producer paths call put functions; ioctl and proc paths inspect queue state.

State and persistence: header-only state description for per-open queues; no globals.

Dependencies and integration: depends on `seq_oss_device.h` and the `union evrec` type from `seq_oss_event.h` through implementation include order.

Risks: callers must hold the queue lock around `pick()` and `free()` according to the contract. The queue exposes integer `qlen`, so non-locked readers should not treat it as stable.

Test signals: static compile coverage and runtime readq producer/consumer tests that enforce lock discipline and queue wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_readq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_rw.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_rw.c

Purpose: implements OSS sequencer file read, write, and poll operations on top of readq/writeq, event conversion, and sequencer enqueue/dispatch.

Important APIs and functions: exports `snd_seq_oss_read()`, `snd_seq_oss_write()`, and `snd_seq_oss_poll()`. Internal `insert_queue()` processes a single OSS event record.

Control flow: read loops while the user buffer can hold at least a short record, peeks a queued record under lock, optionally waits, copies the event length to userspace, and advances the queue. Write copies 4-byte records first, handles `SEQ_FULLSIZE` patch loading as a whole-buffer operation, copies 8-byte long records when needed, rejects mode-incompatible record types, and passes each record to `insert_queue()`. `insert_queue()` consumes timer events, converts records to ALSA events, sets current tick, then dispatches immediately for realtime/stopped timers or enqueues on the ALSA queue otherwise.

State and persistence: mutates readq head/tail, write queue through ALSA pool enqueueing, timer current tick/realtime/running state, and downstream synth/MIDI state from conversion.

Dependencies and integration: depends on readq, writeq, synth patch loading, event conversion, timer state, and sequencer kernel enqueue/dispatch/poll helpers.

Risks: the read size check uses `if (ev_len < count)` where the expected condition appears to be insufficient user buffer when `ev_len > count`; as written it can break when the buffer is larger than the event. This is a high-value behavior to verify against upstream or tests. Patch loading only allowed as the first write item. Blocking behavior is split between readq wait and sequencer pool enqueue.

Test signals: read short/long records with exact, smaller, and larger buffers; blocking and nonblocking read/write; fullsize patch write; invalid mode writes for `/dev/music`; timer wait scheduling; poll readiness for read and write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_synth.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_synth.c

Purpose: manages OSS synth-device registration, per-open synth setup/cleanup, MIDI-as-synth mapping for `/dev/music`, synth addressing, reset, patch loading, sysex/raw event conversion, and legacy synth info/proc output.

Important APIs and functions: exports `snd_seq_oss_synth_init()`, `snd_seq_oss_synth_probe()`, `snd_seq_oss_synth_remove()`, setup/setup_midi/cleanup helpers, `snd_seq_oss_synth_reset()`, `snd_seq_oss_synth_load_patch()`, `snd_seq_oss_synth_info()`, `snd_seq_oss_synth_sysex()`, `snd_seq_oss_synth_addr()`, `snd_seq_oss_synth_ioctl()`, `snd_seq_oss_synth_raw_event()`, `snd_seq_oss_synth_make_info()`, and proc `snd_seq_oss_synth_info_read()`.

Control flow: sequencer-device probe allocates a `seq_oss_synth`, copies registration callbacks, and inserts it in the global table. Per-open setup walks registered synths, pins callback owner modules, calls low-level open, allocates voice tracking, and records opened synths. `/dev/music` setup can append MIDI devices as pseudo synths. Cleanup closes opened synth callbacks, drops module refs, closes MIDI mappings, and frees channel state. Event conversion uses `snd_seq_oss_synth_addr()` before setting note/control/sysex/raw event payloads.

State and persistence: global `synth_devs[]`, `max_synth_devs`, and `midi_synth_dev` are protected by `register_lock` and `snd_use_lock_t`. Per-open `seq_oss_synthinfo` stores callback args, channel state, voice count, MIDI mapping, and opened flags.

Dependencies and integration: registered by `seq_oss.c` as a `snd_seq_driver`; uses callbacks from low-level OSS synth providers, module owner refs, MIDI device helpers, sequencer dispatch, and procfs.

Risks: cleanup sets `rec->opened = 0` rather than decrementing, so multiple opens of the same synth require careful review of historical semantics. MIDI synth reset calls `snd_seq_oss_midi_close(dp, dev)` with the synth index rather than `midi_mapped`, which should be tested. Use-lock synchronization protects removal from active users. Channel arrays depend on driver voice counts.

Test signals: synth probe/remove under use, open/cleanup with failing callbacks or allocation, multiple OSS opens, MIDI pseudo-synth mapping, reset with and without low-level callback, patch/ioctl passthrough, sysex termination at `0xff`, raw event conversion, and proc listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_synth.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_synth.h

Purpose: declares the OSS synth management and conversion interface for the OSS sequencer module.

Important APIs: registration callbacks `snd_seq_oss_synth_probe()`/`remove()`, per-open setup/cleanup, reset, patch loading, synth info lookup, sysex/address/ioctl/raw-event conversion, and legacy `synth_info` creation.

Control flow: `seq_oss.c` registers the probe/remove driver, `seq_oss_init.c` calls setup/cleanup/reset, `seq_oss_event.c` uses info/address/sysex/raw conversion, and ioctl paths use make-info/ioctl/load-patch.

State and persistence: no state in the header, but the declarations operate on global synth registrations and per-open `seq_oss_devinfo` synth arrays.

Dependencies and integration: includes central OSS state, OSS legacy structs, and sequencer-device registration.

Risks: exported functions often accept an OSS device index; callers must pass indexes validated against per-open `max_synthdev`, and implementations may map MIDI pseudo-synths differently from real synths.

Test signals: compile all users and run open/reset/ioctl/event conversion tests through the declared APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_synth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_timer.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_timer.c

Purpose: translates OSS sequencer timing semantics into ALSA sequencer queue tempo and timer events.

Important APIs and functions: exports `snd_seq_oss_timer_new()`, `snd_seq_oss_timer_delete()`, `snd_seq_oss_process_timer_event()`, `snd_seq_oss_timer_start()`, `snd_seq_oss_timer_stop()`, `snd_seq_oss_timer_continue()`, `snd_seq_oss_timer_tempo()`, and `snd_seq_oss_timer_ioctl()`. Internal helpers are `calc_alsa_tempo()` and `send_timer_event()`.

Control flow: new timers initialize OSS tempo/timebase and derived ALSA tempo/PPQ. Write-side timer records update `cur_tick`, realtime mode, or start the queue. Starting sets queue tempo with `snd_seq_set_queue_tempo()` and dispatches a system timer START event. Stop/continue/tempo dispatch system timer events. Ioctl handles control rate, start/stop/continue, tempo, timebase, and ignored metronome/source/select commands.

State and persistence: per-open timer state includes current tick, realtime flag, running flag, ALSA tempo/PPQ, OSS tempo/timebase, and owning `seq_oss_devinfo`. No state persists after close.

Dependencies and integration: depends on ALSA sequencer system timer port events, queue tempo API from `seq_clientmgr.c`, OSS event records, and write/read paths that consult `cur_tick`.

Risks: tempo/timebase clamping must match OSS expectations. Timer events are dispatched atomically with `atomic=1`, so callbacks must be safe. Realtime mode bypasses queueing in write path. `SNDCTL_SEQ_CTRLRATE` rejects nonzero requested rates.

Test signals: relative/absolute waits, zero wait enabling realtime, start/stop/continue idempotence, tempo/timebase clamp boundaries, control-rate query, and queued versus direct dispatch decisions in `seq_oss_rw.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_timer.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_timer.h

Purpose: defines per-open OSS timer state and declares timer operations.

Important APIs and types: `struct seq_oss_timer` stores owner device, current tick, realtime/running flags, ALSA tempo/PPQ, and OSS tempo/timebase. Declares allocation, deletion, start/stop/continue/tempo, ioctl, reset alias, and `snd_seq_oss_timer_cur_tick()`.

Control flow: write/event code reads the current tick and invokes timer-event processing; ioctl code calls timer controls; release deletes the timer.

State and persistence: documents per-open transient timer state only.

Dependencies and integration: includes the central OSS device header and participates in queue timing through ALSA sequencer timer events.

Risks: direct inline access to `cur_tick` has no locking; the design assumes per-file serialized write/ioctl paths or tolerates approximate reads.

Test signals: compile all consumers and run timing behavior tests around current tick and running/realtime flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_writeq.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_writeq.c

Purpose: manages OSS write-side queue sizing, output-pool thresholds, queue clearing, and `SNDCTL_SEQ_SYNC` echo synchronization.

Important APIs and functions: exports `snd_seq_oss_writeq_new()`, `snd_seq_oss_writeq_delete()`, `snd_seq_oss_writeq_clear()`, `snd_seq_oss_writeq_sync()`, `snd_seq_oss_writeq_wakeup()`, `snd_seq_oss_writeq_get_free_size()`, and `snd_seq_oss_writeq_set_output()`.

Control flow: allocation sets the sequencer client's output pool and output room through `SNDRV_SEQ_IOCTL_SET_CLIENT_POOL`. Clear removes all queued output events and wakes sync sleepers. Sync compares requested timer tick with last completed sync time; if needed it enqueues an echo event containing `SEQ_SYNCTIMER`, waits up to one second for `snd_seq_oss_writeq_wakeup()` from event input, and repeats until complete or interrupted. Free-size and threshold operations proxy client-pool ioctls.

State and persistence: per-open writeq state includes owner `dp`, max length, last sync time, whether a sync event is pending, wait queue, and spinlock.

Dependencies and integration: depends on `seq_oss_event.c` echo handling, timer current tick, sequencer kernel enqueue/control APIs, and client pool management in the sequencer core.

Risks: sync relies on echo delivery from the same queue, so event filtering or queue removal can stall until timeout. `snd_seq_kernel_client_enqueue()` return value during sync is ignored. Wakeup updates state under spinlock, but sync reads `sync_time` and `sync_event_put` without always holding it.

Test signals: output pool sizing, threshold ioctl, remove-events clear, sync when already complete, sync echo success, timeout/retry behavior, signal interruption, and release during pending sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_writeq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_writeq.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_writeq.h

Purpose: defines the OSS write queue synchronization structure and public writeq operations.

Important APIs and types: `struct seq_oss_writeq` stores the owning `seq_oss_devinfo`, max length, sync time, pending flag, wait queue, and spinlock. Declares allocation, deletion, clear, sync, wakeup, free-size query, and output threshold setting.

Control flow: open allocates a writeq, ioctl sync/threshold uses it, reset/release clears and deletes it, and echo event input calls wakeup.

State and persistence: no globals; per-open transient queue metadata.

Dependencies and integration: includes central OSS device state and works with ALSA sequencer client pools and echo events.

Risks: users must not call sync on a freed writeq; release/reset ordering relies on file-level serialization in `seq_oss.c`.

Test signals: compile all users and run sync/clear/free-size/threshold tests through an OSS write-open file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_writeq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq.c

Purpose: main ALSA sequencer module entry point and module parameter owner.

Important APIs and state: defines `seq_client_load[]` autoload list, default timer module parameters (`seq_default_timer_class`, `seq_default_timer_sclass`, card/device/subdevice/resolution), module aliases for `/dev/snd/seq`, and init/exit functions `alsa_seq_init()` and `alsa_seq_exit()`.

Control flow: init clears client data, registers the sequencer character device, creates proc entries, creates the internal system client, and initializes autoload support. Exit tears down system client, proc entries, queues, device registration, and autoload in reverse order.

State and persistence: module parameters persist while the module is loaded and influence default queue timer selection and global client autoloading. No on-disk persistence.

Dependencies and integration: orchestrates `seq_clientmgr`, `seq_info`, `seq_system`, `seq_queue`, `seq_timer`, `seq_memory`, `seq_lock`, and sequencer-device autoload support.

Risks: init unwind must match successfully completed stages. Queue deletion happens after system client/proc removal on exit, so queued events must not call into removed clients. Timer defaults depend on Kconfig hrtimer setting.

Test signals: module load/unload, failure injection at each init stage, parameter parsing, dummy-client autoload default with module config, and device node alias creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_clientmgr.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_clientmgr.c

Purpose: core ALSA sequencer client manager. It owns `/dev/snd/seq` file operations, user and kernel client allocation, event read/write, routing, subscription fanout, queue/ioctl control, kernel-client exported APIs, UMP client info, proc client dumps, and sequencer device registration.

Important APIs and functions: file operations are `snd_seq_open()`, `snd_seq_release()`, `snd_seq_read()`, `snd_seq_write()`, `snd_seq_poll()`, and `snd_seq_ioctl()`. Exported APIs include `snd_seq_client_use_ptr()`, `snd_seq_dispatch_event()`, `snd_seq_set_queue_tempo()`, `snd_seq_create_kernel_client()`, `snd_seq_delete_kernel_client()`, `snd_seq_kernel_client_enqueue()`, `snd_seq_kernel_client_dispatch()`, `snd_seq_kernel_client_ctl()`, `snd_seq_kernel_client_ioctl()`, `snd_seq_kernel_client_write_poll()`, `snd_seq_kernel_client_get()`, and `snd_seq_kernel_client_put()`. Device lifecycle is `client_init_data()`, `snd_sequencer_device_init()`, and `snd_sequencer_device_done()`.

Control flow: user open allocates a dynamic client, configures input/output acceptance from file mode, creates a FIFO for readable clients, assigns a PID owner, and broadcasts client-start. Writes copy fixed or UMP event records from userspace, validate type/length and compatibility, attach variable payload pointers, allocate event cells from the client pool, and either deliver direct events immediately or enqueue scheduled events. Dispatch resolves source client, handles note-duration requeueing, and routes to destinations or subscribers with hop-limit enforcement. Reads drain the user FIFO into legacy or UMP-sized user records, expanding variable payloads. Ioctl copies a bounded stack union, serializes with `ioctl_mutex`, calls the handler table, and copies results back.

State and persistence: global `clienttab[]`, `clienttablock[]`, `client_usage`, `clients_lock`, and `register_mutex` exist for the module lifetime. Each `snd_seq_client` owns type, accepted directions, MIDI/UMP mode, filters, use lock, ports, ioctl mutex, convert32 flag, UMP endpoint port, event pool, and user/kernel data. State is in memory only and is announced through system events/proc.

Dependencies and integration: integrates sequencer memory pools, queues, timers, ports, system client notifications, UMP conversion, seq_device autoload, module loading, and optional procfs. Kernel modules such as rawmidi MIDI, OSS emulation, dummy, and virmidi create kernel clients or use kernel dispatch/enqueue APIs.

Risks: routing is highly concurrent; use locks protect clients during removal, port locks protect subscription lists, and ioctl mutex protects mutable client state. Variable events with user pointers cannot be delivered from atomic contexts. Hop-limit and bounce-error handling prevent routing loops. UMP conversion paths must preserve compatibility and group filtering. `snd_seq_delete_kernel_client()` reads `clientptr()` without taking `clients_lock` before freeing, relying on higher-level constraints. Large ioctl stack union must remain large enough for all table commands.

Test signals: user open/read/write/poll/ioctl ABI tests, client/port create/delete, subscription permission and no-export rules, queue lifecycle/tempo/timer ioctls, direct versus queued delivery, note-duration requeueing, bounce error events, event filters, module autoload for global/card clients, UMP client info get/set and conversion, proc client dump, kernel-client APIs, and concurrent client removal during delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_clientmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_clientmgr.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_clientmgr.h

Purpose: declares internal sequencer client-manager structures and APIs shared across sequencer core files and kernel clients.

Important APIs and types: defines `SND_SEQ_GROUP_FILTER_MASK`, `struct snd_seq_user_client`, `struct snd_seq_kernel_client`, `struct snd_seq_client`, and `struct snd_seq_usage`. Declares initialization/device APIs, client reference helpers, `DEFINE_FREE(snd_seq_client)`, event dispatch, kernel write-poll, subscription notification, low-level single-event delivery, OSS-only kernel ioctl wrapper, kernel client get/put, and UMP mode predicates.

Control flow: other modules acquire client references via `snd_seq_client_use_ptr()` or kernel get/put, dispatch event cells through `snd_seq_dispatch_event()`, and call kernel client control paths. Reference helpers wrap `snd_use_lock_t`.

State and persistence: describes in-memory client state including ports, locks, pools, filters, UMP info, and user/kernel owner data. No storage beyond module memory.

Dependencies and integration: includes sequencer kernel API, FIFO, ports, and use-lock headers. Used by `seq_clientmgr.c`, OSS emulation, dummy client, and other sequencer internals.

Risks: structure fields are internal but widely shared, so changes can affect UMP conversion, proc dumps, and kernel clients. Reference helper misuse leads to use-after-free during client teardown.

Test signals: build all sequencer modules after structure changes, run client creation/removal under concurrent dispatch, and verify UMP predicate behavior for legacy/MIDI1/MIDI2 clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_clientmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_compat.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_compat.c

Purpose: provides 32-bit compat ioctl handling for ALSA sequencer when included from `seq_clientmgr.c`.

Important APIs and types: defines `struct snd_seq_port_info32`, compat command constants for port operations, `snd_seq_call_port_info_ioctl()`, and `snd_seq_ioctl_compat()`.

Control flow: most ioctl commands are ABI-compatible and delegate directly to native `snd_seq_ioctl()` after `compat_ptr()`. Port-info commands need conversion because the embedded kernel callback pointer/flags/time fields differ in 32-bit layout; the helper copies the 32-bit struct into a native `snd_seq_port_info`, clears the kernel callback pointer, calls native kernel client control, and copies results back.

State and persistence: no independent state; mutates sequencer client, port, queue, subscription, and UMP state through native ioctl handlers.

Dependencies and integration: depends on native client manager functions, Linux compat APIs, and kernel allocation helpers.

Risks: port-info conversion must not allow user-provided `kernel` callback pointers. Direct delegation for other commands assumes identical compat layout. UMP info commands are delegated, so their user-pointer handling must already be compat-safe.

Test signals: 32-bit userspace tests for create/delete/get/set/query port, all directly delegated ioctls, invalid pointers, and running-mode convert32 interaction with variable user pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_dummy.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_dummy.c

Purpose: implements the autoloadable ALSA sequencer MIDI-through client at `SNDRV_SEQ_CLIENT_DUMMY`, forwarding received events to subscribers.

Important APIs and types: module parameters `ports`, `duplex`, and optional `ump`; `struct snd_seq_dummy_port`; callbacks `dummy_input()` and `dummy_free()`; setup helpers `create_port()`, `register_client()`, `delete_client()`, and module init/exit.

Control flow: init creates a kernel sequencer client named "Midi Through", optionally sets its UMP/MIDI conversion mode, and creates one or two ports per requested index. Each port has read/write/subscription capabilities and a kernel input callback. On input, non-system/non-error events are copied, source port is rewritten to the same port or paired duplex port, destination becomes subscribers, and the event is dispatched through the kernel client.

State and persistence: module state is `my_client`, module parameters, and per-port private `snd_seq_dummy_port` records freed by port private-free callback. No persistent storage.

Dependencies and integration: depends on sequencer kernel client create/delete/control/dispatch APIs and optional UMP client fields from `seq_clientmgr.h`.

Risks: invalid `ports < 1` is rejected, but very large `ports` relies on sequencer port limits. Duplex setup must clean up the whole client on second-port failure. UMP filter choices affect whether events are converted or passed through.

Test signals: load with default, multiple ports, duplex, and UMP modes; connect ports with `aconnect`; verify event forwarding, subscriber delivery, module autoload alias, and cleanup on partial port creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_fifo.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_fifo.c

Purpose: implements FIFO queues of sequencer event cells for user-client input delivery.

Important APIs and functions: exports `snd_seq_fifo_new()`, `snd_seq_fifo_delete()`, `snd_seq_fifo_clear()`, `snd_seq_fifo_event_in()`, `snd_seq_fifo_cell_out()`, `snd_seq_fifo_cell_putback()`, `snd_seq_fifo_poll_wait()`, `snd_seq_fifo_resize()`, and `snd_seq_fifo_unused_cells()`.

Control flow: allocation creates a sequencer memory pool, initializes locks and wait queue. Event input duplicates an event into a pool cell nonblocking, appends it to the tail under spinlock, increments cell count, and wakes readers. Read drains cells with optional blocking wait and signal interruption. Clear synchronizes use-lock users then frees all cells. Resize swaps in a new initialized pool under lock, closes the old pool, waits for users, frees old cells, and deletes old pool.

State and persistence: per FIFO state includes pool, head/tail linked list, cell count, spinlock, use lock, wait queue, and overflow atomic. It is transient per user client.

Dependencies and integration: depends on sequencer memory pool/cell helpers, use-lock primitive, scheduler signal handling, and `seq_clientmgr.c` read/poll/pool ioctls.

Risks: overflow is reported separately and causes `snd_seq_read()` to clear the FIFO and return `-ENOSPC`. Cell putback is needed when userspace copy fails after dequeue. Resize drops queued events by design. Blocking reads must remove waitqueue entries on all paths.

Test signals: FIFO enqueue/dequeue order, blocking/nonblocking reads, overflow increment and read error, putback on copy failure, poll readiness, resize with active users, clear/delete wakeups, and unused-cell accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_fifo.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_fifo.h

Purpose: declares the sequencer FIFO structure and operations used by user clients.

Important APIs and types: `struct snd_seq_fifo` stores a memory pool, head/tail event-cell list, cell count, spinlock, use-lock, wait queue, and overflow counter. Declares FIFO allocation/deletion, event input, dequeue/putback, clear, poll, resize, unused-cell query, and guard macros around `snd_use_lock_t`.

Control flow: `seq_clientmgr.c` uses the FIFO API to deliver events to user clients and read them back to userspace. Guard macros prevent deletion while a thread operates on a FIFO.

State and persistence: no globals; per-client transient queue state only.

Dependencies and integration: includes sequencer memory and lock headers.

Risks: callers must pair FIFO lock/unlock guards for operations that depend on use-lock protection. The queue is backed by a finite pool, so overflow handling is part of the ABI.

Test signals: compile all users and run user-client read/delivery tests that cover overflow, resize, and deletion while blocked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_fifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_info.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_info.c

Purpose: creates and removes ALSA sequencer procfs entries for queues, clients, and timer state.

Important APIs and functions: `create_info_entry()`, `snd_seq_info_init()`, and `snd_seq_info_done()`.

Control flow: init creates module entries under `snd_seq_root`, assigns text read callbacks from client manager, queue, and timer modules, registers them, and unwinds all entries on any failure. Done frees all stored entries.

State and persistence: module-static `queues_entry`, `clients_entry`, and `timer_entry` hold proc entry handles while the sequencer is loaded. Proc contents are generated live; no data persists.

Dependencies and integration: depends on ALSA info/proc APIs and read callbacks `snd_seq_info_queues_read()`, `snd_seq_info_clients_read()`, and `snd_seq_info_timer_read()`.

Risks: only built with `CONFIG_SND_PROC_FS`; header stubs make callers no-op otherwise. Partial init must free earlier entries to avoid dangling proc nodes.

Test signals: procfs-enabled load/unload, failure injection for each entry registration, reading `/proc/asound/seq/{queues,clients,timer}`, and build with procfs disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_info.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_info.h

Purpose: declares sequencer procfs initialization and read callbacks, with no-op stubs when procfs is disabled.

Important APIs: `snd_seq_info_clients_read()`, `snd_seq_info_timer_read()`, `snd_seq_info_queues_read()`, `snd_seq_info_init()`, and `snd_seq_info_done()`.

Control flow: `seq.c` calls init/done unconditionally; this header resolves to real functions or stubs based on `CONFIG_SND_PROC_FS`.

State and persistence: no state in the header.

Dependencies and integration: includes ALSA info and sequencer kernel headers; links client manager, timer, and queue proc readers.

Risks: callbacks are declared regardless of procfs, so implementations must be conditionally compiled consistently to avoid link errors.

Test signals: build with `CONFIG_SND_PROC_FS=y` and `n`, and read all proc entries when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_lock.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_lock.c

Purpose: implements a simple use-counter synchronization helper for sequencer objects that need to wait until active users leave before freeing memory.

Important APIs and functions: exports `snd_use_lock_sync_helper()`, backing the `snd_use_lock_sync()` macro.

Control flow: if the atomic counter is negative, it warns and returns. Otherwise it sleeps one tick at a time until the counter reaches zero, warning once after roughly five seconds of waiting.

State and persistence: no module state; operates on caller-owned `snd_use_lock_t` atomics.

Dependencies and integration: used by FIFO cleanup, client teardown, OSS MIDI/synth removal, and other sequencer structures to coordinate with lockless referenced users.

Risks: this is not a full refcount with lifetime ownership; callers must remove objects from lookup tables before waiting. Sleeping makes it unsuitable for atomic contexts. A stuck positive counter can block teardown indefinitely with periodic warning only once per call.

Test signals: teardown while concurrent users hold/release locks, negative-counter warning path, and ensuring all callers invoke it only from sleepable context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_lock.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_lock.h

Purpose: defines the sequencer use-lock primitive as an atomic use counter plus helper macros.

Important APIs and types: `typedef atomic_t snd_use_lock_t`, `snd_use_lock_init()`, `snd_use_lock_use()`, `snd_use_lock_free()`, and `snd_use_lock_sync()` which records source file/line for diagnostics.

Control flow: users increment before using a shared object, decrement after use, and teardown removes object visibility then calls sync to wait for the counter to drain.

State and persistence: no global state; the counter lives inside protected structures such as clients, FIFOs, MIDI devices, and synth records.

Dependencies and integration: includes scheduler support for the sync implementation and is used throughout the sequencer core and OSS compatibility code.

Risks: macros do not prevent underflow or enforce object lifetime by themselves. Missing `free()` calls can hang teardown; extra `free()` calls drive the counter negative and trigger warnings.

Test signals: static audit of every use/free pair, concurrent lookup/removal stress, and lockdep-style validation that sync is only used in sleepable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_lock.h -->
