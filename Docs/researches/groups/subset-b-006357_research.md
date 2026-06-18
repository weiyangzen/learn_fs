# subset-b-006357 ALSA timer, UMP, virtual control, and generic driver research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/timer.c -->
# sources/distributed-fs/ceph-client/sound/core/timer.c

## Purpose

This file implements the ALSA timer core and the `/dev/snd/timer` userspace API. It manages global/card/PCM timer devices, opens master and slave timer instances, dispatches periodic callbacks, exposes ioctl/read/poll/fasync behavior to applications, registers the built-in jiffies-based system timer, and optionally supports userspace-driven timers via anonymous file descriptors.

## Important APIs, types, and functions

The exported kernel APIs are `snd_timer_instance_new()`, `snd_timer_instance_free()`, `snd_timer_open()`, `snd_timer_close()`, `snd_timer_resolution()`, `snd_timer_start()`, `snd_timer_stop()`, `snd_timer_continue()`, `snd_timer_pause()`, `snd_timer_interrupt()`, `snd_timer_new()`, `snd_timer_notify()`, `snd_timer_global_new()`, `snd_timer_global_free()`, and `snd_timer_global_register()`. Core state is held in `struct snd_timer`, `struct snd_timer_instance`, `struct snd_timer_hardware`, and the local `struct snd_timer_user`. User ABI helpers define 32-bit and 64-bit timestamped read records, status structs, queue management, ioctl dispatch, and optional `struct snd_utimer`.

## Control Flow

Timer registration starts with `snd_timer_new()` and `snd_timer_dev_register()`, which validate hardware callbacks and add devices to `snd_timer_list` in timer-id order. `snd_timer_open()` either links a slave instance into `snd_timer_slave_list` or resolves a real timer, opens hardware on first use, references the module/card, and links matching slave/master instances. Start, stop, pause, and continue route through master or slave helpers, update instance flags, program hardware, and notify control callbacks. Hardware drivers call `snd_timer_interrupt()`, which advances active instances, queues fast callbacks on `ack_list_head`, slow callbacks on `sack_list_head`, reschedules the hardware, and runs or schedules callbacks. The character-device path opens `struct snd_timer_user`, selects a timer via ioctl, configures parameters/filter/queue mode, starts or stops the instance, and serves queued tick or timestamped events through `read()` and `poll()`. Module init allocates the timer device, registers the system timer, registers the ALSA timer char device, and creates procfs output.

## State and Persistence Behavior

Persistent kernel state is list-based: registered timers, pending slaves, open master instances, per-timer active/ack lists, and per-user ring queues. `register_mutex` protects global registration/open/close linkage; per-timer spinlocks protect active and callback lists; `slave_active_lock` coordinates slave activation. Timer instance flags encode running, start-delayed, paused, auto, exclusive, early event, slave, callback, and dead states. User state persists across file operations in `file->private_data`, including queue positions, overrun count, filter mask, timestamp mode, async wakeups, and disconnect state. The system timer keeps correction and jiffies accounting in timer private data. Optional userspace-driven timers allocate global ids with an IDA and persist until the anon fd release path frees the timer.

## Dependencies and Integration Points

The code depends on ALSA core device registration, `sound/timer.h`, controls, procfs info, minors/char device registration, module autoloading, workqueues, Linux timers, wait queues, fasync, anon inodes, IDA, and card lifetime references. Integration points include PCM and MIDI drivers using ALSA timers, loopback sound-timer mode, sequencer/OSS users that open slave timers, userspace through `snd/timer`, and optional `timer_compat.c` for compat ioctls.

## Risks

The highest-risk areas are lifetime and locking between close, callbacks, card shutdown, slave/master relinking, and userspace reads. Timer callbacks deliberately drop `timer->lock`, so dead/callback flags and close waiting are critical. User queue resizing and timestamp mode changes must stay serialized by `ioctl_lock` and `qlock`. ABI risks include 32/64-bit timestamp/status layout, old ioctl numbers, filter validation, and `read()` unit sizing. Userspace-driven timers expose triggerable global timers and need strict id/fd cleanup. Resolution checks reject too-small periods, so behavior changes can break low-latency clients.

## Test Signals

Useful signals include ALSA timer ioctl tests for select/params/status/start/stop/read/poll/fasync, compat ioctl coverage on 32-bit userspace over 64-bit kernels, concurrent close while callbacks are running, slave/master attach and detach cases, card shutdown disconnect wakeups, procfs timer listing, module autoload for timer ids, system timer drift/reschedule tests, and `CONFIG_SND_UTIMER` create/trigger/fd-release tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/timer_compat.c -->
# sources/distributed-fs/ceph-client/sound/core/timer_compat.c

## Purpose

This included source provides the 32-bit compat ioctl bridge for the ALSA timer userspace API. It adapts timer structures whose layout differs between ILP32 and LP64 processes and forwards compatible commands into the shared timer ioctl implementation.

## Important APIs, Types, and Functions

The local ABI types are packed `struct snd_timer_gparams32` and `struct snd_timer_info32`. `snd_timer_user_gparams_compat()` copies a 32-bit global-params request and calls `timer_set_gparams()`. `snd_timer_user_info_compat()` builds a 32-bit info record for the currently selected timer. `__snd_timer_user_ioctl_compat()` maps compat command numbers to native handlers or compat-specific helpers. `snd_timer_user_ioctl_compat()` serializes access with the same per-file `ioctl_lock` used by native ioctl.

## Control Flow

The file is included from `timer.c` only when `CONFIG_COMPAT` is enabled. Most commands are layout-compatible and are forwarded to `__snd_timer_user_ioctl(..., compat=true)` after converting the argument with `compat_ptr()`. Commands with `long` or alignment-sensitive layout use local compat command numbers and local copy logic. Unsupported commands return `-ENOIOCTLCMD`, allowing higher ioctl layers to report the appropriate failure.

## State and Persistence Behavior

This file owns no standalone state. It reads and writes `struct snd_timer_user` stored on the open file, reads selected timer metadata, and can update global timer parameters through `timer_set_gparams()`. Serialization and persistence are inherited from `timer.c`.

## Dependencies and Integration Points

It depends on `linux/compat.h` and on static symbols from the including translation unit, including `timer_set_gparams()`, `snd_timer_user_status32()`, `snd_timer_user_status64()`, and `__snd_timer_user_ioctl()`. It is wired into `snd_timer_f_ops.compat_ioctl`.

## Risks

The main risks are ABI drift, wrong ioctl direction/size constants, packed alignment mismatches, and differences from native info retrieval. Notably the compat info path reports `t->hw.resolution` directly rather than `snd_timer_hw_resolution()`, so dynamic-resolution timers may differ from native `SNDRV_TIMER_IOCTL_INFO`. Missing coverage for newly added native ioctls would strand 32-bit applications.

## Test Signals

Run 32-bit ALSA timer clients against a 64-bit kernel for `PVERSION`, `TREAD`, `GINFO`, `GPARAMS`, `GSTATUS`, `SELECT`, `PARAMS`, both status layouts, and start/stop/continue/pause. Compare native and compat info/status output for dynamic-resolution timers and verify invalid pointers return `-EFAULT`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/timer_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/ump.c -->
# sources/distributed-fs/ceph-client/sound/core/ump.c

## Purpose

This file implements ALSA Universal MIDI Packet endpoint support on top of rawmidi. It creates UMP rawmidi devices, parses UMP stream messages, maintains endpoint and function-block metadata, forwards packets to userspace and the sequencer, and optionally exposes legacy MIDI 1.0 rawmidi devices backed by UMP conversion.

## Important APIs, Types, and Functions

The exported APIs are `snd_ump_endpoint_new()`, `snd_ump_receive_ump_val()`, `snd_ump_receive()`, `snd_ump_transmit()`, `snd_ump_block_new()`, `snd_ump_update_group_attrs()`, `snd_ump_switch_protocol()`, `snd_ump_parse_endpoint()`, and, with legacy support, `snd_ump_attach_legacy_rawmidi()`. Important state includes `struct snd_ump_endpoint`, `struct snd_ump_block`, `struct snd_ump_group`, rawmidi substream arrays, stream-discovery wait state, sequencer device hooks, and legacy mapping/converter arrays.

## Control Flow

Endpoint creation allocates an `snd_ump_endpoint`, initializes rawmidi with the UMP info flag, assigns UMP-specific global and stream ops, and initializes lists and locks. Device registration optionally creates a sequencer device. Receive flow accumulates 32-bit words with `snd_ump_receive_ump_val()`, handles complete stream messages, forwards to sequencer input hooks, converts to legacy input streams if enabled, then copies raw UMP data to the UMP input substream. Transmit flow reads UMP bytes from the UMP output substream and, when no UMP data is available, can synthesize UMP from opened legacy output streams. Endpoint parsing opens an internal rawmidi output stream, sends discovery requests, waits for matching stream-message replies, fills endpoint/device/name/product/protocol fields, creates function blocks, updates group attributes, then closes the internal stream.

## State and Persistence Behavior

Endpoint metadata persists in `ump->info`, block list entries, per-group attributes, and rawmidi names. Stream discovery uses `stream_wait_for`, `stream_finished`, `input_buf`, and a wait queue with a 500 ms timeout per request. Function block updates after initial parsing may refresh group attributes, legacy substream names, and sequencer clients, except static-block endpoints suppress updates. Legacy rawmidi support persists group-to-substream mapping, output converter state per group, open counts, and tied rawmidi devices.

## Dependencies and Integration Points

The file depends on ALSA rawmidi, UMP protocol definitions, UMP conversion helpers, ALSA sequencer device hooks, procfs info, kernel list/mutex/spinlock/wait primitives, and card/device registration. Hardware-specific UMP drivers supply `ump->ops` for open/close/trigger/drain and call `snd_ump_receive()` and `snd_ump_transmit()`.

## Risks

Risks include malformed or partial UMP packets leaving stale input state, stream-discovery timeouts, deadlocks around internal rawmidi open/write during parsing, incorrect static function-block update handling, bounds errors in group ranges, legacy conversion mismatches, and race-prone name/substream updates while legacy devices are open. The fallback behavior when devices do not respond to optional discovery messages needs to remain tolerant.

## Test Signals

Use UMP-capable virtual or USB MIDI devices to verify endpoint parse, stream config, function-block creation, dynamic function-block update, procfs output, UMP rawmidi read/write, sequencer notifications, and legacy rawmidi group mapping. Include malformed stream messages, timeout-only devices, MIDI 1.0 function blocks under MIDI 2 protocol, and concurrent UMP plus legacy opens.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/ump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/ump_convert.c -->
# sources/distributed-fs/ceph-client/sound/core/ump_convert.c

## Purpose

This file implements conversion helpers between Universal MIDI Packet data and legacy MIDI 1.0 byte streams. It is used by UMP legacy rawmidi bridging to translate incoming UMP packets into MIDI bytes and outgoing legacy MIDI bytes into MIDI 1.0 or MIDI 2.0 UMP packets.

## Important APIs, Types, and Functions

The exported APIs are `snd_ump_convert_from_ump()` and `snd_ump_convert_to_ump()`. Internal helpers scale values between 7-, 14-, 16-, and 32-bit MIDI encodings, convert UMP system/channel/SysEx7 messages to MIDI bytes, convert MIDI byte streams to UMP system/SysEx/channel messages, and track bank/RPN/NRPN state in `struct ump_cvt_to_ump` and `struct ump_cvt_to_ump_bank`.

## Control Flow

UMP-to-legacy conversion dispatches on UMP message type, returns the target group, and emits MIDI bytes for system, MIDI 1 channel voice, MIDI 2 channel voice, and SysEx7 packets. Legacy-to-UMP conversion is byte-stream driven: status bytes establish expected command length, realtime/system messages are emitted when complete, SysEx bytes are packed into 6-byte UMP data chunks, and channel messages are converted according to the requested endpoint protocol. MIDI 2 output expands controller, pressure, pitch bend, notes, program/bank select, and RPN/NRPN sequences into the wider UMP encodings.

## State and Persistence Behavior

`snd_ump_convert_from_ump()` is stateless. `snd_ump_convert_to_ump()` mutates the caller-owned converter context, including partial command bytes, SysEx state, generated packet bytes, per-channel bank select state, and deferred RPN/NRPN data. This persistence is required for running-status-like byte stream assembly and multi-message controller sequences.

## Dependencies and Integration Points

It depends on ALSA UMP protocol macros and structures from `sound/ump.h` and `sound/ump_convert.h`. `sound/core/ump.c` uses it for legacy rawmidi input and output conversion, and any other driver can reuse the exported conversion helpers.

## Risks

Conversion is intentionally lossy when downscaling MIDI 2 values to MIDI 1. Edge cases include note-on with zero velocity, bank select state lifetime, incomplete RPN/NRPN sequences, SysEx chunk boundaries, unsupported UMP message types, realtime bytes interrupting SysEx, and host endianness assumptions around casting UMP words to unions. A zero return means "no complete output" rather than hard failure, so callers must preserve converter state.

## Test Signals

Round-trip tests should cover all channel voice statuses, MIDI 2 value scaling boundaries, program changes with and without bank select, pitch bend extremes, RPN and NRPN complete and partial sequences, SysEx single/start/continue/end packets, realtime/system messages, unsupported data types, and group preservation across conversions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/ump_convert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/vmaster.c -->
# sources/distributed-fs/ceph-client/sound/core/vmaster.c

## Purpose

This file implements ALSA virtual master controls. A virtual master exposes a mixer control whose value attenuates or gates one or more existing follower controls while preserving the followers' original callbacks and cached values.

## Important APIs, Types, and Functions

The exported APIs are `_snd_ctl_add_follower()`, `snd_ctl_add_followers()`, `snd_ctl_make_virtual_master()`, `snd_ctl_add_vmaster_hook()`, `snd_ctl_sync_vmaster()`, and `snd_ctl_apply_vmaster_followers()`. Local state is modeled by `struct link_master`, `struct link_follower`, and `struct link_ctl_info`. Core helpers include `follower_init()`, `follower_update()`, `follower_get_val()`, `follower_put_val()`, `master_init()`, `sync_followers()`, and overridden control callbacks for master and followers.

## Control Flow

`snd_ctl_make_virtual_master()` creates a mono mixer kcontrol backed by `link_master` and optional TLV dB metadata. `_snd_ctl_add_follower()` copies an existing follower kcontrol, stores the copy, replaces the live kcontrol's info/get/put/TLV/free callbacks, and links it under the master. Master initialization lazily inspects the first follower to derive type/range and defaults the master value to maximum. Follower gets return cached unattenuated values; follower puts validate and cache requested values, then write attenuated values to the original callback. Master puts validate the new value, read each follower using the old master value, and rewrite each follower using the new master value.

## State and Persistence Behavior

The master persists follower list, derived type/range, current master value, optional TLV array, and an optional hook. Each follower persists a copy of the original control, its current unattenuated values, flags, and a backpointer to the live kcontrol. Freeing the master restores original follower kcontrol contents while preserving list linkage. `SND_CTL_FOLLOWER_NEED_UPDATE` forces refresh from the original control on initialization.

## Dependencies and Integration Points

It depends on ALSA control core, mixer element callbacks, TLV dB metadata, and kcontrol private data/free semantics. Codec and card drivers use it to build "Master" controls over several hardware-specific volume or switch controls.

## Risks

The code assumes follower controls are integer or boolean, have at most two channels, and share compatible range/type semantics; callers are responsible for selecting sane followers. Attenuation assumes max volume is 0 dB and master cannot add gain. Restoring copied kcontrols in `master_free()` is sensitive to control layout changes. Lack of explicit locking means correctness depends on ALSA control core serialization around callbacks.

## Test Signals

Mixer tests should create virtual masters over mono/stereo integer and boolean followers, verify range validation, attenuation at min/max/mid values, hook invocation, TLV exposure, follower cached value preservation, `snd_ctl_sync_vmaster()`, `snd_ctl_apply_vmaster_followers()`, and correct restoration/removal on card teardown.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/vmaster.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/Kconfig -->
# sources/distributed-fs/ceph-client/sound/drivers/Kconfig

## Purpose

This Kconfig file defines ALSA generic sound-driver configuration entries and shared library symbols used by several sound drivers. It controls availability of dummy, loopback, virtual MIDI, MPU-401, PC speaker, serial MIDI, parallel-port MIDI, AC97, OPL, VX, and related support.

## Important APIs, Types, and Functions

The important symbols for this subset are `SND_DRIVERS`, `SND_DUMMY`, `SND_ALOOP`, `SND_MPU401`, and `SND_MPU401_UART`. `SND_DUMMY` selects `SND_PCM`; `SND_ALOOP` selects `SND_PCM` and `SND_TIMER`; `SND_MPU401` depends on `HAS_IOPORT` and selects `SND_MPU401_UART`; `SND_MPU401_UART` selects `SND_RAWMIDI`. The file also defines generic library symbols such as `SND_AC97_CODEC`, `SND_OPL3_LIB`, `SND_OPL4_LIB`, and sequencer helper selections.

## Control Flow

Kconfig evaluation starts with shared tristate library symbols, then exposes `menuconfig SND_DRIVERS`. Inside the menu, user-visible drivers declare dependencies, select required ALSA subsystems, and provide help text/module names. Build inclusion is later consumed by the Makefiles through `obj-$(CONFIG_...)` variables.

## State and Persistence Behavior

The persistent state is the generated kernel `.config`. Tristate values determine built-in, module, or disabled compilation. Selects force dependent ALSA core components into compatible states.

## Dependencies and Integration Points

It integrates with the top-level ALSA Kconfig tree, `sound/drivers/Makefile`, `sound/drivers/mpu401/Makefile`, and downstream driver source files. External dependencies include architecture capabilities such as `X86`, `HAS_IOPORT`, `HIGH_RES_TIMERS`, `PARPORT`, `OF`, `SERIAL_DEV_BUS`, `DEBUG_FS`, and `INPUT`.

## Risks

Incorrect dependencies can expose drivers on unsupported platforms or omit required subsystems. `select` can force hidden symbols in surprising ways, so adding dependencies to selected libraries must be done carefully. User help text affects module expectations, especially for virtual/test drivers that can become default audio devices.

## Test Signals

Run kernel config builds for built-in, module, and disabled combinations of `SND_DUMMY`, `SND_ALOOP`, and `SND_MPU401`; verify dependencies prevent unsupported selections; and confirm module names match generated objects (`snd-dummy`, `snd-aloop`, `snd-mpu401`, `snd-mpu401-uart`).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/Makefile -->
# sources/distributed-fs/ceph-client/sound/drivers/Makefile

## Purpose

This Makefile maps generic ALSA driver Kconfig symbols to their module objects and recurses into driver subdirectories. It is the build glue for top-level generic drivers such as dummy, loopback, virtual MIDI, serial MIDI, PCM test, and parallel-port MIDI.

## Important APIs, Types, and Functions

The key object mappings are `snd-dummy-y := dummy.o`, `snd-aloop-y := aloop.o`, and related `snd-*-y` composite module definitions. `obj-$(CONFIG_SND_DUMMY)`, `obj-$(CONFIG_SND_ALOOP)`, and peers add those modules to the build. `obj-$(CONFIG_SND) += opl3/ opl4/ mpu401/ vx/ pcsp/` recurses into subdirectories when ALSA is enabled.

## Control Flow

Kbuild evaluates the `snd-*-y` module composition first, then includes each object or subdirectory according to generated `CONFIG_*` values. The mpu401 UART and front-end driver are handled by the nested `mpu401/Makefile`.

## State and Persistence Behavior

No runtime state exists. Build state is generated objects, modules, and built-in archives determined by Kconfig tristates.

## Dependencies and Integration Points

It depends on Kbuild conventions and symbols from `sound/drivers/Kconfig`. It integrates with the source files researched here by building `dummy.o` into `snd-dummy.o`, `aloop.o` into `snd-aloop.o`, and delegating `mpu401` builds to the child Makefile.

## Risks

Risks are build-only: stale object names, missing subdirectory recursion, or mismatched Kconfig symbols can silently exclude a driver or build it under the wrong module name. Composite modules with one object are simple but still need consistent names for modprobe aliases and documentation.

## Test Signals

Kbuild smoke tests should enable each mapped symbol as `m` and `y`, verify expected `.ko` names, and ensure `make M=sound/drivers` or full kernel builds reach the `mpu401` subdirectory when `CONFIG_SND` is enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/aloop.c -->
# sources/distributed-fs/ceph-client/sound/drivers/aloop.c

## Purpose

This file implements the ALSA loopback PCM sound card. It creates two PCM devices whose playback side of one device feeds the capture side of the paired device, with optional jiffies timing or synchronization to an external ALSA sound timer.

## Important APIs, Types, and Functions

Important structures are `struct loopback`, `struct loopback_cable`, `struct loopback_pcm`, `struct loopback_setup`, and `struct loopback_ops`. PCM callbacks are `loopback_open()`, `loopback_close()`, `loopback_prepare()`, `loopback_trigger()`, `loopback_pointer()`, and `loopback_hw_free()`. Timer backends are represented by `loopback_jiffies_timer_ops` and `loopback_snd_timer_ops`. Mixer/proc helpers expose rate shift, notify mode, active state, captured format/rate/channels/access, cable state, and `timer_source`.

## Control Flow

Module init registers a platform driver and creates enabled platform devices. Probe allocates an ALSA card, initializes two PCM devices, creates per-substream mixer controls, creates procfs cable/timer-source entries, and registers the card. Opening a PCM substream allocates a `loopback_pcm`, creates or reuses its paired cable, selects the timer backend, installs dynamic hardware rules that mirror peer constraints, and records the stream in the cable. Prepare computes byte alignment, buffer size, period size, bytes per second, clears capture buffers, and marks stream validity. Trigger validates peer format, toggles running/pause bits, and starts or stops the backend timer. Timer callbacks update positions, copy playback data into capture buffers, fill silence when needed, and call `snd_pcm_period_elapsed()`.

## State and Persistence Behavior

Loopback state persists per card in `struct loopback`, per paired substream in `struct loopback_cable`, and per open stream in `struct loopback_pcm`. The cable tracks valid/running/pause bits, peer stream pointers, timer instance, external timer id, in-flight stop count, and shared hardware constraints. `loopback_setup` persists user-visible mixer state such as notify flag, rate shift, last playback format/rate/channels/access, and control ids for notifications. `timer_source` is devm-managed and can be changed through procfs while holding `cable_lock`.

## Dependencies and Integration Points

It depends on ALSA PCM, control, procfs, timer core, platform devices, jiffies timers, wait queues, and module parameters. It integrates directly with `sound/core/timer.c` when an external timer source is configured, and with userspace through ALSA PCM devices and mixer controls.

## Risks

The main risks are peer-stream lifetime and locking. Format changes can stop a running capture stream outside `cable->lock`, so `stop_count` and `stop_wait` must prevent cable teardown races. External sound-timer callbacks intentionally avoid taking locks in timer callback order and defer MSTOP handling to workqueue to avoid deadlocks. Non-interleaved copy logic depends on channel buffer math. Timer source parsing mutates temporary string separators and must restore them. Dynamic hardware rules must reflect peer constraints without using stale PCM midlevel cached rules.

## Test Signals

Test paired playback/capture with interleaved and non-interleaved formats, format/rate/channel mismatches, notify mode, rate-shift changes, start/stop/pause/resume/drain, capture silence when playback is absent, external `timer_source` parsing by card id/index/global id, procfs cable output, and concurrent close during forced capture stop. ALSA loopback integration tests should compare captured bytes with playback bytes across ring wrap boundaries.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/aloop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/dummy.c -->
# sources/distributed-fs/ceph-client/sound/drivers/dummy.c

## Purpose

This file implements the ALSA dummy sound card, a virtual `/dev/null`-style card for testing ALSA PCM and mixer behavior. It exposes configurable PCM devices/substreams, optional hardware-profile constraints, fake or real buffers, timer-driven PCM position advancement, and dummy mixer controls.

## Important APIs, Types, and Functions

Important structures are `struct snd_dummy`, `struct dummy_model`, `struct dummy_timer_ops`, `struct dummy_systimer_pcm`, and, when high-resolution timers are enabled, `struct dummy_hrtimer_pcm`. PCM callbacks are `dummy_pcm_open()`, `dummy_pcm_close()`, `dummy_pcm_prepare()`, `dummy_pcm_trigger()`, `dummy_pcm_pointer()`, `dummy_pcm_hw_params()`, and optional fake-buffer copy/silence/page callbacks. Mixer callbacks implement volume, capture-source, and external I/O box controls. Probe/init functions are `snd_dummy_probe()`, `snd_card_dummy_pcm()`, `snd_card_dummy_new_mixer()`, and `alsa_card_dummy_init()`.

## Control Flow

Module init registers a platform driver, allocates fake pages when requested, and creates enabled platform devices. Probe creates an ALSA card, applies a named dummy hardware model if configured, creates requested PCM devices, adjusts hardware constraints, creates mixer controls, optionally exposes debug procfs hardware fields, and registers the card. PCM open chooses hrtimer or system timer ops, allocates per-substream timer state, applies model constraints, and adjusts interleaved/mmap capabilities by PCM device number. Trigger starts or stops the selected timer; prepare initializes period timing; pointer calculates current frame position from jiffies or monotonic hrtimer time.

## State and Persistence Behavior

Card state persists in `struct snd_dummy`, including current PCM hardware template, model pointer, mixer volumes, capture source bits, external I/O state, and references to CD controls. Per-substream timer state persists in `runtime->private_data`. Fake-buffer mode uses two global zero pages, one per stream, and reports `runtime->dma_bytes` manually for mmap. Debug procfs can mutate fields of `dummy->pcm_hw` at runtime when enabled.

## Dependencies and Integration Points

It depends on ALSA core, PCM, rawmidi headers, controls, TLV, procfs, platform devices, jiffies timers, hrtimers, and module parameters. Kconfig builds it through `CONFIG_SND_DUMMY`, and userspace sees standard ALSA PCM/mixer devices.

## Risks

Timer correctness affects PCM period wakeups and pointer monotonicity. The hrtimer start path sets running after starting the timer, so callback ordering is subtle. Fake buffer mmap maps the same page repeatedly, intentionally discarding all data; users must not infer real buffering. Mixer capture-source change detection uses logical AND between channel changes, so single-channel changes may report unchanged even though state changes. Debug procfs can create invalid hardware constraints if written incorrectly.

## Test Signals

Run PCM playback/capture with hrtimer and jiffies modes, fake and real buffers, mmap and non-mmap device variants, all built-in model presets, suspend/resume, period elapsed timing, XRUN/drain behavior, mixer volume and capture controls, external I/O inactive notifications, debug procfs reads/writes, and multi-card module-parameter combinations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/mpu401/Makefile -->
# sources/distributed-fs/ceph-client/sound/drivers/mpu401/Makefile

## Purpose

This Makefile builds the ALSA MPU-401 UART support modules. It separates the generic platform/PnP front-end from the reusable UART-mode rawmidi implementation.

## Important APIs, Types, and Functions

`snd-mpu401-y := mpu401.o` defines the generic MPU-401 card driver module. `snd-mpu401-uart-y := mpu401_uart.o` defines the reusable UART helper module. `obj-$(CONFIG_SND_MPU401_UART)` and `obj-$(CONFIG_SND_MPU401)` include the helper and front-end modules according to Kconfig.

## Control Flow

Kbuild composes each module object from its source object and includes it when the matching config symbol is enabled. Since `SND_MPU401` selects `SND_MPU401_UART`, normal front-end builds include both modules.

## State and Persistence Behavior

No runtime state exists. Build state is the generated built-in object or loadable modules selected by Kconfig.

## Dependencies and Integration Points

It depends on `sound/drivers/Kconfig` symbols and Kbuild. The modules produced here provide `snd_mpu401` and `snd_mpu401_uart`, with the front-end calling the exported `snd_mpu401_uart_new()` helper.

## Risks

Build risks are symbol/object mismatches and missing helper inclusion if Kconfig select relationships change. Because the UART helper exports APIs for other drivers, changing module boundaries can affect link dependencies.

## Test Signals

Build `CONFIG_SND_MPU401_UART=m`, `CONFIG_SND_MPU401=m`, and built-in variants; verify both modules are generated and that `snd-mpu401` resolves `snd_mpu401_uart_new`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/mpu401/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/mpu401/mpu401.c -->
# sources/distributed-fs/ceph-client/sound/drivers/mpu401/mpu401.c

## Purpose

This file implements the generic ALSA MPU-401 UART card front-end for legacy MIDI ports. It handles module parameters, platform-device probing, optional PnP discovery, ALSA card creation, and registration of an MPU-401 rawmidi UART instance.

## Important APIs, Types, and Functions

The central helpers are `snd_mpu401_create()`, `snd_mpu401_probe()`, optional `snd_mpu401_pnp()` and `snd_mpu401_pnp_probe()`, `snd_mpu401_unregister_all()`, `alsa_card_mpu401_init()`, and `alsa_card_mpu401_exit()`. Module parameters configure card index/id/enable, PnP use, I/O port, IRQ, and obsolete `uart_enter`.

## Control Flow

Module init registers the platform driver, creates platform devices for enabled non-PnP slots with explicit port/IRQ settings, registers the PnP driver, and fails if no devices are created. Platform probe validates that port and IRQ are specified or disabled, calls `snd_mpu401_create()`, registers the card, and stores drvdata. PnP probe finds the next enabled PnP slot, reads port and IRQ resources from the PnP device, creates/registers the card, stores PnP drvdata, and increments the device count. Exit unregisters PnP, platform devices, and the platform driver.

## State and Persistence Behavior

Persistent module state includes module parameter arrays, `platform_devices[]`, `pnp_registered`, and `snd_mpu401_devices`. Each detected device owns an ALSA card created with devm card lifetime, and the rawmidi hardware instance is owned by the card.

## Dependencies and Integration Points

It depends on ALSA core, `sound/mpu401.h`, platform devices, optional PnP, I/O port resources, and the UART helper exported from `mpu401_uart.c`. Kconfig requires `HAS_IOPORT` for the generic front-end.

## Risks

Resource discovery is fragile on legacy hardware. A static `dev` counter in PnP probe means probe ordering controls slot assignment. Platform mode requires explicit port and IRQ disable/selection. PnP registration is attempted even when `CONFIG_PNP` is absent via an empty driver object, so init behavior depends on PnP core stubs. The obsolete `uart_enter` warning indicates retained compatibility but no functional use.

## Test Signals

Test platform mode with valid port/IRQ, polling IRQ `-1`, missing port, missing IRQ, multiple card slots, and PnP resource discovery with and without IRQ. Verify card long names, rawmidi device creation, cleanup on partial init failure, and module unload.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/mpu401/mpu401.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/mpu401/mpu401_uart.c -->
# sources/distributed-fs/ceph-client/sound/drivers/mpu401/mpu401_uart.c

## Purpose

This file provides the reusable ALSA MPU-401 UART rawmidi implementation. It handles low-level port or MMIO access, command/reset sequencing, IRQ and polling-driven input/output, rawmidi stream callbacks, resource ownership, and creation of the rawmidi device.

## Important APIs, Types, and Functions

Exported APIs are `snd_mpu401_uart_interrupt()`, `snd_mpu401_uart_interrupt_tx()`, and `snd_mpu401_uart_new()`. Internal helpers include low-level `mpu401_read/write_port/mmio`, `snd_mpu401_uart_cmd()`, `snd_mpu401_do_reset()`, input/output open/close/trigger callbacks, `snd_mpu401_uart_input_read()`, `snd_mpu401_uart_output_write()`, polling timer add/remove callbacks, and `snd_mpu401_uart_free()`.

## Control Flow

Creation builds an ALSA rawmidi device, allocates `struct snd_mpu401`, requests I/O regions unless integrated, selects port or MMIO accessors, requests IRQ when provided, enables timer polling when no IRQ/hook is available, assigns rawmidi ops, and returns the rawmidi object. Open callbacks run optional board hooks, reset and enter UART mode if the opposite stream is not already open, then set stream mode bits. Input trigger flushes FIFO on first enable, optionally starts polling, and performs an initial read. Output trigger sets output-trigger mode, optionally starts polling, and writes pending bytes. IRQ handlers read input and opportunistically write output; timer polling requeues itself each jiffy and calls the same interrupt worker. Close callbacks clear mode bits, reset hardware when both streams are closed, and run optional close hooks.

## State and Persistence Behavior

`struct snd_mpu401` persists accessors, ports, IRQ, rawmidi pointer, substream pointers, mode bits, timer state, locks, resource handle, hardware type, board hooks, and info flags. The polling timer persists while input or output timer bits are set. Rawmidi transmit buffers own queued output bytes; the driver peeks, writes to hardware, and acknowledges bytes after successful writes.

## Dependencies and Integration Points

It depends on ALSA rawmidi/core, `sound/mpu401.h`, Linux I/O port/MMIO APIs, IRQ APIs, timers, spinlocks, and optional hardware hook callbacks. The generic `mpu401.c` front-end and other ALSA drivers can instantiate this helper through `snd_mpu401_uart_new()`.

## Risks

Hardware timing is the main risk. Command ACK waits, reset sequencing, and FIFO polling use bounded busy loops and may fail on slow or nonstandard devices. Polling mode runs every jiffy and can perform poorly. Output has no real transmit IRQ on standard UART mode, so output latency depends on opportunistic input IRQs or polling. Locking spans input, output, and timer state; timer removal uses non-sync deletion, so lifetime is protected by rawmidi/card teardown assumptions. Resource cleanup must match requested regions and IRQs.

## Test Signals

Test port and MMIO access modes, IRQ and polling modes, input-only/output-only/duplex flags, reset failure paths, command ACK/no-ACK hardware flags, transmit FIFO full behavior, rawmidi trigger start/stop races, timer polling add/remove balance, module unload while streams are closed, and legacy MPU hardware variants such as PC98II port layout.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/mpu401/mpu401_uart.c -->
