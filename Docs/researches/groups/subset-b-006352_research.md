# Research: subset-b-006352

This grouped report covers ALSA core control, device, card lifecycle, memory, jack, hwdep, proc-info, and OSS compatibility sources under `sources/distributed-fs/ceph-client/sound/core`. Each file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/control_compat.c -->
# sources/distributed-fs/ceph-client/sound/core/control_compat.c

## Purpose
`control_compat.c` is included by the ALSA control core to implement 32-bit and x32 compatibility ioctls for the control API. Its job is ABI translation: map 32-bit user structures and pointers into native `snd_ctl_elem_*` structures, call the normal control implementation, then copy results back in the layout expected by compat userspace.

## Important APIs, Types, and Functions
Key compat layouts are `snd_ctl_elem_list32`, `snd_ctl_elem_info32`, `snd_ctl_elem_value32`, and, under `CONFIG_X86_X32_ABI`, `snd_ctl_elem_value_x32`. `snd_ctl_elem_list_compat()` translates the PID pointer and delegates to `snd_ctl_elem_list()`. `snd_ctl_elem_info_compat()` copies the element id and enumerated item selector, takes a power reference with `snd_power_ref_and_wait()`, calls `snd_ctl_elem_info()`, and serializes type-specific return fields. `copy_ctl_value_from_user()` and `copy_ctl_value_to_user()` are the shared value marshalling helpers for read and write. `snd_ctl_elem_add_compat()` converts user-control metadata, including enum names pointer conversion via `compat_ptr()`. `snd_ctl_ioctl_compat()` is the dispatch point for native-pass-through ioctls, compat-specific element ioctls, x32 variants, and registered driver compat ioctl hooks.

## Control Flow and State
Read/write paths first copy the id and reject indirect values, then `get_ctl_type()` looks up the kcontrol under `card->controls_rwsem` and invokes `kctl->info()` to determine type and count. Boolean/integer values are copied element-by-element through 32-bit integers; bytes, IEC958, enum, and integer64 payloads use size-based raw copies. Public wrappers take and release a card power reference around the actual read/write. The file does not own persistent state; it protects access by using the card control rwsem and the control core's existing power and control locking.

## Dependencies and Integration Points
This file depends on the native control core functions and global compat ioctl list `snd_control_compat_ioctls`. It integrates with power management, ALSA kcontrol lookup, user-control add/replace handling, and architecture-specific ABI differences. It is compiled by textual inclusion from `control.c`, so static helpers share the parent compilation unit.

## Risks and Test Signals
Primary risk is ABI drift: field offsets, union sizes, pointer conversions, and x32 alignment must match userspace headers. Count-derived copies depend on trusted `kctl->info()` results; malformed counts would stress fixed arrays in `snd_ctl_elem_value`. Tests should exercise 32-bit and x32 control list/info/read/write/add/replace ioctls, enum names pointers, integer64 values, TLV pass-through, unknown driver compat ioctl fallbacks, power-suspended cards, and removal races around `controls_rwsem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/control_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/control_led.c -->
# sources/distributed-fs/ceph-client/sound/core/control_led.c

## Purpose
`control_led.c` connects ALSA control elements to Linux LED audio triggers. Controls marked with speaker or microphone LED access bits can drive `audio-mute` and `audio-micmute` LED triggers. It also exposes sysfs controls for selecting LED mode and manually attaching or detaching kcontrols to LED groups per card.

## Important APIs, Types, and Functions
Core types are `snd_ctl_led`, representing one LED group, `snd_ctl_led_card`, representing one per-card sysfs child, and `snd_ctl_led_ctl`, representing a tracked kcontrol/index offset. `snd_ctl_led_set_state()` aggregates all controls in a group and updates the LED trigger. `snd_ctl_led_notify()` reacts to ALSA control layer add, remove, info, and value events. `snd_ctl_led_set_id()`, `set_led_id()`, `attach_store()`, `detach_store()`, `reset_store()`, and `list_show()` implement sysfs control binding. `snd_ctl_led_register()` and `snd_ctl_led_disconnect()` are layer callbacks registered through `snd_ctl_register_layer()`.

## Control Flow and State
Global state includes `snd_ctl_leds[]`, `snd_ctl_led_card_valid[]`, LED trigger pointers, and `snd_ctl_led_mutex`. On module init the file registers `audio-mute` and `audio-micmute` triggers, creates `/sys/class/sound/ctl-led`, creates speaker and mic child devices, and registers a control layer. When a card registers, existing controls are scanned and kcontrols with LED access bits are added to per-LED tracking lists. Each update calls `snd_ctl_led_get()` for every tracked control and aggregates route state. The mode transforms the aggregate: follow-mute is direct, follow-route inverts route, off forces LED off, and on forces LED on. Card disconnect removes sysfs links, invalidates the card, cleans tracked controls for that card, and refreshes trigger state.

## Dependencies and Integration Points
The file depends on ALSA control access bits, `card->controls_rwsem`, card references via `snd_card_ref()`, control layer callbacks, Linux device/sysfs APIs, and LED trigger APIs. Sysfs links are created both from the control device to `led-speaker`/`led-mic` and from LED-card devices back to the card.

## Risks and Test Signals
Risks include stale kcontrol pointers if notify/remove ordering is wrong, incorrect LED polarity for route versus mute modes, and parser ambiguity in sysfs attach strings. The static `snd_ctl_led_get()` buffers require `snd_ctl_led_mutex` coverage. Tests should cover automatic LED access-bit discovery, value changes across multiple controls, sysfs mode changes, attach/detach by numid and name, reset, card unregister, trigger brightness, invalid card numbers, and controls changing LED group through info notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/control_led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/control_trace.h -->
# sources/distributed-fs/ceph-client/sound/core/control_trace.h

## Purpose
`control_trace.h` defines the tracepoint metadata for ALSA control put operations. It gives tracing users visibility into whether a control write reached the expected value and records the element identity and card context.

## Important APIs, Types, and Functions
The file defines `TRACE_SYSTEM snd_ctl` and a single `TRACE_EVENT(snd_ctl_put)`. The event arguments are `struct snd_ctl_elem_id *id`, interface name string, card number, expected value, and actual value. The trace payload stores numid, interface name, kcontrol name, index, device, subdevice, card, expected, and actual. `TP_printk()` formats success/fail status based on expected/actual equality.

## Control Flow and State
There is no runtime state in this header. At build time it expands through Linux tracepoint machinery. The final `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `#include <trace/define_trace.h>` section must remain outside the include guard, as required by tracepoint generation.

## Dependencies and Integration Points
It depends on `linux/tracepoint.h` and UAPI ALSA control ids from `uapi/sound/asound.h`. It is consumed by the ALSA control implementation that emits `trace_snd_ctl_put()` on control writes or verification paths.

## Risks and Test Signals
Risks are trace ABI compatibility and string lifetime: event strings are copied via trace macros, so callers must supply valid strings at call time. Tests should build with tracing enabled, verify generated trace events appear under ftrace/perf, and exercise successful and failed control put cases with meaningful element metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/control_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/ctljack.c -->
# sources/distributed-fs/ceph-client/sound/core/ctljack.c

## Purpose
`ctljack.c` provides small helper functions for representing jack detection state as ALSA read-only kcontrols. It is used by the higher-level jack abstraction to create controls such as `"Headphone Jack"` and report plugged/unplugged status through the control API.

## Important APIs, Types, and Functions
The static `jack_detect_kctl` template uses CARD iface, read-only access, boolean mono info, and `jack_detect_kctl_get()`. `snd_kctl_jack_new()` creates a new kcontrol from that template, generates a name with `jack_kctl_name_gen()`, chooses a non-conflicting index with `get_available_index()`, and initializes `private_value` to zero. `snd_kctl_jack_report()` updates `private_value` and emits `snd_ctl_notify()` with `SNDRV_CTL_EVENT_MASK_VALUE` when the state changes.

## Control Flow and State
The only per-control state is the boolean status stored in `kctl->private_value`. Name generation appends `" Jack"` unless the source name already ends with that suffix. Index allocation scans existing CARD iface controls with the same name and increments `sid.index`, resetting `sid.numid` before each lookup so `snd_ctl_find_id()` does not match by stale numid.

## Dependencies and Integration Points
This helper depends on the ALSA control core and is integrated by `jack.c` through `snd_kctl_jack_new()` and `snd_kctl_jack_report()`. It relies on callers to add/remove the returned kcontrol to the card and to serialize lifetime with normal control-device rules.

## Risks and Test Signals
Risks are mostly naming and duplicate-index behavior. Tests should create multiple jacks with identical labels, verify suffix handling, verify read-only boolean values, and ensure no duplicate control ids appear. Reporting should notify only on transitions, not repeated identical state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/ctljack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/device.c -->
# sources/distributed-fs/ceph-client/sound/core/device.c

## Purpose
`device.c` implements the generic ALSA per-card device-component lifecycle. Drivers and core subsystems register components with a card, and the card lifecycle later registers, disconnects, and frees those components in a consistent order.

## Important APIs, Types, and Functions
Public APIs include `snd_device_new()`, `snd_device_register()`, `snd_device_disconnect()`, `snd_device_free()`, `snd_device_register_all()`, `snd_device_disconnect_all()`, and `snd_device_free_all()`. Internals include `look_for_dev()`, `__snd_device_register()`, `__snd_device_disconnect()`, and `__snd_device_free()`. Each `snd_device` records card, type, state, owner data pointer, and callback table `snd_device_ops`.

## Control Flow and State
`snd_device_new()` allocates a `snd_device`, sets state `SNDRV_DEV_BUILD`, and inserts it into `card->devices` sorted by device type. Registration calls `dev_register` only from BUILD state and transitions to REGISTERED. Disconnect calls `dev_disconnect` only from REGISTERED and transitions to DISCONNECTED. Free removes the node, disconnects if necessary, calls `dev_free`, and releases the wrapper. Bulk register walks forward; bulk disconnect and free walk reverse so later/higher-level devices are torn down before earlier foundations. `snd_device_free_all()` keeps CONTROL and LOWLEVEL devices until a second pass, preserving control and low-level cleanup ordering.

## Dependencies and Integration Points
The file is a core dependency for card init/free logic and subsystems such as hwdep, jack, PCM, rawmidi, and controls. It assumes `device_data` pointers uniquely identify components for lookup.

## Risks and Test Signals
Risks include duplicate `device_data`, wrong type ordering, callbacks that fail during registration/disconnect/free, and drivers calling free/disconnect for unknown devices. Tests should register mock components with ordered types, validate callback ordering and state transitions, inject registration failures, and verify card free leaves CONTROL/LOWLEVEL until the final cleanup pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/hrtimer.c -->
# sources/distributed-fs/ceph-client/sound/core/hrtimer.c

## Purpose
`hrtimer.c` implements the ALSA global high-resolution timer backend. It exposes an ALSA timer device backed by Linux `hrtimer` so ALSA timer clients can get high-resolution periodic callbacks.

## Important APIs, Types, and Functions
`struct snd_hrtimer` stores the ALSA timer pointer, `struct hrtimer`, and an `in_callback` flag. Timer hardware callbacks are `snd_hrtimer_open()`, `snd_hrtimer_close()`, `snd_hrtimer_start()`, and `snd_hrtimer_stop()`. `snd_hrtimer_callback()` is the hrtimer callback and calls `snd_timer_interrupt()`. Module init uses `snd_timer_global_new()` and `snd_timer_global_register()`; exit frees `mytimer`.

## Control Flow and State
Open allocates `snd_hrtimer`, initializes a monotonic relative hrtimer, and stores it in `t->private_data`. Start arms the hrtimer for `t->sticks * resolution` unless already executing inside callback. The callback checks `t->running` under `t->lock`, marks `in_callback`, calculates drift from callback time versus expiry, adds missed ticks, emits `snd_timer_interrupt()`, then re-arms if still running. Stop tries to cancel the hrtimer unless running in callback. Close marks the timer stopped and `in_callback`, cancels the hrtimer, frees state, and clears private data.

## Dependencies and Integration Points
The backend integrates with ALSA timer core via `snd_timer_hardware` and is exposed under `SNDRV_TIMER_GLOBAL_HRTIMER`. It depends on `hrtimer_resolution`, `CLOCK_MONOTONIC`, timer core locking, and module aliasing for timer autoload.

## Risks and Test Signals
Risks include drift calculation overflow if ticks/resolution values are invalid, races between callback and stop/close, and missed cancellation if `in_callback` handling regresses. Tests should open/start/stop/close timers repeatedly, run timer clients at multiple periods, validate drift compensation under delayed callbacks, and unload the module while clients are closing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/hrtimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/hwdep.c -->
# sources/distributed-fs/ceph-client/sound/core/hwdep.c

## Purpose
`hwdep.c` implements ALSA's hardware-dependent device layer. It provides `/dev/snd/hwC*D*` file operations, control ioctls for hwdep discovery, optional OSS direct-FM registration, proc listing, and a driver-facing allocation API for custom hardware access and firmware/DSP loading.

## Important APIs, Types, and Functions
Public creation is `snd_hwdep_new()`. File operations are `snd_hwdep_open()`, `release`, `read`, `write`, `llseek`, `poll`, `mmap`, and `ioctl`. Built-in ioctls include `SNDRV_HWDEP_IOCTL_PVERSION`, `INFO`, `DSP_STATUS`, and `DSP_LOAD`. `snd_hwdep_control_ioctl()` handles `SNDRV_CTL_IOCTL_HWDEP_NEXT_DEVICE` and `SNDRV_CTL_IOCTL_HWDEP_INFO` from the control interface. Device callbacks are `snd_hwdep_dev_register()`, `snd_hwdep_dev_disconnect()`, and `snd_hwdep_dev_free()`.

## Control Flow and State
Global `snd_hwdep_devices` is protected by `register_mutex`. Open resolves ALSA or OSS minor data, pins the card module, waits on `open_wait` if exclusive/open callbacks return `-EAGAIN`, adds the file to the card monitor list, increments `used`, and stores the hwdep pointer. Release calls driver release, decrements `used`, wakes waiters, removes the card file, and drops the module reference. DSP load checks callback presence, enforces index `< 32`, prevents duplicate loads using `dsp_loaded`, and sets the loaded bit after success. Register inserts into the global list, registers the ALSA minor, optionally registers OSS, and disconnect removes devices and wakes waiters.

## Dependencies and Integration Points
It depends on `snd_device_new()` for card lifecycle integration, minor registration helpers, control ioctl registration, card file tracking, module refcounts, and driver-provided `hwdep->ops`. With `CONFIG_SND_PROC_FS`, `/proc/asound/hwdep` lists card/device/name.

## Risks and Test Signals
Risks include exclusive-open wakeup behavior, card shutdown races while blocked in open, global-list consistency during control discovery, and driver callbacks returning inconsistent errors. Tests should cover blocking and nonblocking open, module unload with open files, DSP load duplicate/index cases, control ioctl enumeration, OSS registration constraints, and disconnect during active operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/hwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/hwdep_compat.c -->
# sources/distributed-fs/ceph-client/sound/core/hwdep_compat.c

## Purpose
`hwdep_compat.c` is included by `hwdep.c` when compat support is enabled. It translates 32-bit hardware-dependent DSP image ioctls into native `snd_hwdep_dsp_image` calls.

## Important APIs, Types, and Functions
The main compat type is `snd_hwdep_dsp_image32`, with 32-bit fields for `image` and `driver_data`. `snd_hwdep_dsp_load_compat()` copies index/name prefix, converts the 32-bit image pointer with `compat_ptr()`, copies length and driver data, and calls `snd_hwdep_dsp_load()`. `snd_hwdep_ioctl_compat()` dispatches native-compatible ioctls through `snd_hwdep_ioctl()` and handles `SNDRV_HWDEP_IOCTL_DSP_LOAD32`; unknown commands go to `hw->ops.ioctl_compat` or return `-ENOIOCTLCMD`.

## Control Flow and State
The file has no state of its own. It operates on the open file's `struct snd_hwdep` and preserves the same `dsp_loaded` behavior implemented by the native helper.

## Dependencies and Integration Points
It depends on `linux/compat.h`, the native hwdep ioctl implementation, and driver optional compat callbacks. Because it is textually included, it can call static `snd_hwdep_dsp_load()`.

## Risks and Test Signals
Risks are pointer truncation/extension mistakes, struct layout drift, and inconsistent unknown-command behavior versus native. Tests should run 32-bit userspace DSP status/load ioctls, verify pointer conversion, duplicate load behavior, and fallback to driver `ioctl_compat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/hwdep_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/info.c -->
# sources/distributed-fs/ceph-client/sound/core/info.c

## Purpose
`info.c` implements ALSA's `/proc/asound` information interface. It manages proc entry trees, text and binary proc file operations, card proc directories and symlinks, helper parsing functions, and core entries such as `version`, `cards`, minors, and optional OSS/sequencer roots.

## Important APIs, Types, and Functions
Important public functions are `snd_info_init()`, `snd_info_done()`, `snd_info_create_module_entry()`, `snd_info_create_card_entry()`, `snd_info_register()`, `snd_info_free_entry()`, `snd_info_card_create()`, `snd_info_card_register()`, `snd_info_card_disconnect()`, `snd_info_card_free()`, `snd_card_rw_proc_new()`, `snd_info_get_line()`, and `snd_info_get_str()`. `snd_info_private_data` carries per-open buffers, entry pointer, and callback-private data. Text entries use seq_file through `snd_info_text_entry_ops`; binary/data entries use `snd_info_entry_operations`.

## Control Flow and State
Global roots include `snd_proc_root`, `snd_seq_root`, and optional `snd_oss_root`, protected by `info_mutex` and per-entry `access` mutexes. Init creates `/proc/asound`, optional subdirectories, and core entries. Entry creation allocates `snd_info_entry`, stores name/module/parent, and links into the parent's child list. Registration recursively creates proc dirs/files, choosing text or data ops based on content. Open pins the module and validates access mode against available callbacks. Text writes buffer up to 16 KiB and invoke the write callback on release; reads call the text read callback from seq show. Free removes proc entries, recursively frees children, unlinks from parent, calls `private_free`, and releases names.

## Dependencies and Integration Points
The file depends on Linux procfs, seq_file, module reference counting, ALSA card init/free, minor info registration, and optional OSS/sequencer support. Card id symlinks are maintained under `/proc/asound` and updated by `snd_info_card_id_change()`.

## Risks and Test Signals
Risks include recursive registration/free races, stale `entry->p` after proc removal, module ref leaks on open error paths, and text write truncation above 16 KiB. Tests should create nested entries, register/free repeatedly, open read/write text and data entries, change card ids and verify symlinks, verify reserved word rejection, and check teardown while files are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/info_oss.c -->
# sources/distributed-fs/ceph-client/sound/core/info_oss.c

## Purpose
`info_oss.c` implements OSS-compatible `/proc/asound/oss/sndstat` reporting. It stores per-card OSS device description strings and prints an emulated legacy sound-driver status page.

## Important APIs, Types, and Functions
`snd_oss_info_register()` registers or clears a string for a device class and card number. `snd_sndstat_show_strings()` prints all registered strings for one OSS category. `snd_sndstat_proc_read()` builds the sndstat text, including kernel identity, installed driver text, card config, and Audio/Synth/Midi/Timers/Mixers sections. `snd_info_minor_register()` creates the `sndstat` proc entry below `snd_oss_root`.

## Control Flow and State
Global state is `snd_sndstat_strings[SNDRV_CARDS][SNDRV_OSS_INFO_DEV_COUNT]`, protected by the `strings` mutex. Registering with a non-NULL string duplicates it; registering NULL frees the existing string and clears the slot. The proc reader takes the mutex while enumerating each category.

## Dependencies and Integration Points
It depends on the proc info framework from `info.c`, OSS emulation device categories, `snd_card_info_read_oss()` from card init, and `init_utsname()` for kernel details. OSS mixer and other OSS layers call `snd_oss_info_register()` to populate categories.

## Risks and Test Signals
Risks include stale strings if device unregister paths fail to clear entries and memory leaks on replacement if overwrite semantics change. Tests should register/unregister strings for each category, read `/proc/asound/oss/sndstat`, verify empty categories print the disabled message, and run concurrent register/read operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/info_oss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/init.c -->
# sources/distributed-fs/ceph-client/sound/core/init.c

## Purpose
`init.c` is the ALSA card lifecycle core. It allocates cards, assigns card slots and ids, initializes control and proc infrastructure, registers card devices, tracks open files for hot-unplug, disconnects active file operations, frees resources, exposes card sysfs attributes, and provides PM power wait helpers.

## Important APIs, Types, and Functions
Public APIs include `snd_device_alloc()`, `snd_card_new()`, `snd_devm_card_new()`, `snd_card_free_on_error()`, `snd_card_ref()`, `snd_card_locked()`, `snd_card_disconnect()`, `snd_card_disconnect_sync()`, `snd_card_free_when_closed()`, `snd_card_free()`, `snd_card_set_id()`, `snd_card_add_dev_attr()`, `snd_card_register()`, `snd_component_add()`, `snd_card_file_add()`, `snd_card_file_remove()`, `snd_power_ref_and_wait()`, and `snd_power_wait()`. `snd_monitor_file` tracks open files and their original file ops during shutdown.

## Control Flow and State
Global state includes `snd_cards[]`, `snd_cards_lock` bitmap, `snd_card_mutex`, `shutdown_files`, and `shutdown_lock`. Card creation chooses a slot using module `slots[]` preferences, empty-slot fallback, and `snd_ecards_limit`, then initializes device lists, control lists, file lists, wait queues, card device, control minors, proc card root, and debugfs/value buffers when configured. Registration adds the card device, handles managed devres actions, registers all component devices, derives or uniquifies the card id, publishes `snd_cards[number]`, registers proc info, and notifies OSS mixer emulation.

Disconnect marks shutdown under `files_lock`, replaces every active file's `f_op` with `snd_shutdown_f_ops`, wakes PM sleepers, notifies OSS and devices, synchronizes optional IRQ, removes proc/debugfs/card device publication, clears the global card slot, and syncs power refs. File removal restores original fops refs and wakes `remove_sleep` when the file list empties. Free waits on a completion triggered by device release and then frees devices, private data, card info, debug buffers, and the card allocation.

## Dependencies and Integration Points
This file integrates almost every ALSA core subsystem: control creation, proc info, generic devices, OSS mixer notifications, debugfs, sysfs, devres, PM, and card file tracking used by hwdep/PCM/rawmidi/etc.

## Risks and Test Signals
Risks are hot-unplug races, double-free in managed versus unmanaged cards, card id conflicts, file op replacement lifetime, and slot allocation bugs with module parameters. Tests should cover manual and devm card creation, registration failure paths, card id sysfs writes, duplicate ids, open-file disconnect and release, synchronous disconnect waiting, PM wait during shutdown, OSS mixer callbacks, and repeated register/unregister cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/isadma.c -->
# sources/distributed-fs/ceph-client/sound/core/isadma.c

## Purpose
`isadma.c` provides ALSA helper wrappers for legacy ISA DMA programming, disabling, pointer reporting, and devres-managed DMA channel requests.

## Important APIs, Types, and Functions
Public functions are `snd_dma_program()`, `snd_dma_disable()`, `snd_dma_pointer()`, and `snd_devm_request_dma()`. The internal `snd_dma_data` stores the channel for devres cleanup, and `__snd_release_dma()` disables and frees it.

## Control Flow and State
Programming claims the ISA DMA lock, disables the channel, clears the flip-flop, sets mode/address/count, optionally enables the channel unless `DMA_MODE_NO_ENABLE` is set, then releases the lock. Pointer reporting claims the lock, clears the flip-flop, optionally disables/enables around residue reads, reads the residue twice to avoid lower-byte rollover, selects the higher residue, and returns `size - residue` except for zero/out-of-range values which report zero. Managed request calls `request_dma()`, allocates devres state, and frees the channel if devres allocation fails.

## Dependencies and Integration Points
The file depends on Linux `isa-dma.h`, ISA DMA bridge behavior, and device resource management. It is used by old ISA sound drivers that still rely on 8237-style DMA channels.

## Risks and Test Signals
Risks include hardware-specific residue race behavior, incorrect pointer wrap handling, and cleanup ordering on driver unbind. Tests require ISA-DMA-capable or emulated hardware paths, debug checks for residue greater than size, no-enable programming mode, and devres automatic release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/isadma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/jack.c -->
# sources/distributed-fs/ceph-client/sound/core/jack.c

## Purpose
`jack.c` implements ALSA's jack abstraction. It can expose jack state through ALSA kcontrols, optional Linux input devices, and optional debugfs software-injection nodes for testing jack events.

## Important APIs, Types, and Functions
`struct snd_jack_kctl` links a kcontrol to a jack with a status mask and injection state. Public APIs include `snd_jack_new()`, `snd_jack_add_new_kctl()`, `snd_jack_set_key()`, and `snd_jack_report()`. Device callbacks `snd_jack_dev_register()`, `snd_jack_dev_disconnect()`, and `snd_jack_dev_free()` integrate with card lifecycle. Debugfs helpers include `snd_jack_debugfs_add_inject_node()`, `sw_inject_enable_write()`, and `jackin_inject_write()`.

## Control Flow and State
`snd_jack_new()` optionally creates an initial kcontrol, allocates `snd_jack`, duplicates the id, optionally allocates and configures an input device unless phantom, registers the jack as `SNDRV_DEV_JACK`, and links initial kcontrols. Registration names the input device from card shortname plus jack id, assigns default parent, configures button capabilities, and registers with input core. Reporting caches hardware status, reports non-injected bits to kcontrols, suppresses input bits currently controlled by software injection, then reports keys and switches and syncs the input device. Disconnect removes debugfs and unregisters or frees input devices under `input_dev_lock`; free removes kcontrols, calls private cleanup, disconnects, and frees the jack.

## Dependencies and Integration Points
It depends on `ctljack.c` helpers, ALSA device lifecycle, control core, optional input subsystem, and optional debugfs. Jack type bits map to `SW_*` input switch codes and `SND_JACK_BTN_*` buttons.

## Risks and Test Signals
Risks include kcontrol cleanup order, input-device lifetime during disconnect, software injection masking real hardware state, and phantom jack behavior. Tests should create jacks with and without kcontrols/input devices, add multiple masked kcontrols, report mixed status bits, configure button keys before registration, verify debugfs injection enable/disable restores hardware state, and disconnect/free while input users are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/jack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/memalloc.c -->
# sources/distributed-fs/ceph-client/sound/core/memalloc.c

## Purpose
`memalloc.c` implements ALSA's generic DMA/audio buffer allocation layer. It abstracts different memory backends behind `snd_malloc_ops` so PCM and other audio paths can allocate, free, mmap, sync, and query buffer pages regardless of whether memory is contiguous, vmalloc-backed, coherent DMA, noncontiguous DMA, noncoherent DMA, IRAM, write-combined, or fallback SG.

## Important APIs, Types, and Functions
The central dispatch type is `struct snd_malloc_ops`. Public APIs include `snd_dma_alloc_dir_pages()`, `snd_dma_alloc_pages_fallback()`, `snd_dma_free_pages()`, `snd_devm_alloc_dir_pages()`, `snd_dma_buffer_mmap()`, `snd_dma_buffer_sync()`, `snd_sgbuf_get_addr()`, `snd_sgbuf_get_page()`, and `snd_sgbuf_get_chunk_size()`. Backend functions implement continuous pages, vmalloc, IRAM, coherent device memory, write-combined device memory, DMA noncontiguous memory, noncoherent memory, and optional x86 SG fallback.

## Control Flow and State
Allocation aligns sizes to pages, records device/type/direction, dispatches through `snd_dma_get_ops()`, stores area/address/private data, and records byte size on success. Fallback allocation halves requested size down to a page on `-ENOMEM`. Continuous allocation uses `alloc_pages_exact()` with DMA mask fallback to DMA32 or DMA zones and optional x86 WC attributes. Vmalloc backends translate pages on demand and compute physically contiguous chunks by walking page addresses. DMA noncontiguous allocation stores `sg_table`, vmaps it, records sync need, and implements explicit CPU/device sync. SG fallback tries standard DMA first, then allocates progressively smaller contiguous chunks, maps an sg table, vmaps pages, and exposes mmap/chunk helpers. Noncoherent allocation tracks `need_sync` and uses dma sync APIs.

## Dependencies and Integration Points
The file depends on Linux DMA mapping APIs, genalloc, vmalloc/vmap, scatter-gather iterators, architecture write-combining helpers, and ALSA `snd_dma_buffer` contracts. Consumers rely on these helpers for PCM ring buffers and mmap into user space.

## Risks and Test Signals
Risks include DMA mask fallback leaks, wrong cache synchronization for noncoherent/noncontiguous memory, incorrect chunk calculations across page boundaries, SG fallback partial-allocation cleanup, and write-combine attribute restoration. Tests should allocate/free every enabled type, mmap buffers, validate physical address/page lookup at offsets, exercise fallback under pressure, run DMA sync in both directions, and check no leaks on injected failures in SG/vmap/dma-map stages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/memalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/memory.c -->
# sources/distributed-fs/ceph-client/sound/core/memory.c

## Purpose
`memory.c` provides helpers for copying between userspace or `iov_iter` buffers and MMIO space. It exists because normal user copy helpers cannot directly and portably access `__iomem` addresses on all architectures.

## Important APIs, Types, and Functions
Public functions are `copy_to_user_fromio()`, `copy_to_iter_fromio()`, `copy_from_user_toio()`, and `copy_from_iter_toio()`. User variants import a user buffer into an `iov_iter` and delegate to iterator variants.

## Control Flow and State
There is no persistent state. On i386 and SPARC32, iterator copies cast the MMIO pointer through `__force` and use normal iterator copy helpers. Other architectures copy in 256-byte stack chunks: reads use `memcpy_fromio()` then `copy_to_iter()`, and writes use `copy_from_iter()` then `memcpy_toio()`. Partial iterator copy returns the number of bytes successfully moved; user wrappers convert short copies to `-EFAULT`.

## Dependencies and Integration Points
The file depends on Linux `uaccess`, `io.h`, `iov_iter`, and ALSA PCM users that expose MMIO-backed buffers. It is exported for drivers needing user-visible MMIO data transfers.

## Risks and Test Signals
Risks include partial copy handling, architecture-specific behavior differences, and stack-buffer chunk logic for unaligned sizes. Tests should copy varied lengths including zero, sub-256, multi-256, and faulting user buffers; validate MMIO read/write ordering on supported platforms; and exercise iov_iter short-copy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/misc.c -->
# sources/distributed-fs/ceph-client/sound/core/misc.c

## Purpose
`misc.c` contains small ALSA utility helpers: resource release, PCI subsystem-id quirk lookup, and deferred fasync signal delivery.

## Important APIs, Types, and Functions
`release_and_free_resource()` releases an `ioport` resource and frees it. With PCI enabled, `snd_pci_quirk_lookup_id()` and `snd_pci_quirk_lookup()` scan `snd_pci_quirk` tables by subsystem vendor/device and mask. Deferred async helpers are `snd_fasync_helper()`, `snd_kill_fasync()`, and `snd_fasync_free()`, backed by `struct snd_fasync`, `snd_fasync_lock`, `snd_fasync_list`, and `snd_fasync_work_fn()`.

## Control Flow and State
Fasync setup optionally allocates a wrapper, installs or reuses it under spinlock, records on/off state, and calls `fasync_helper()`. `snd_kill_fasync()` stores signal/poll info, moves the wrapper to the global pending list, and schedules work. The work function drains the list under spinlock, skips disabled entries, drops the lock around `kill_fasync()`, then resumes draining. Free disables the wrapper, removes it from the list, flushes work, and frees memory.

## Dependencies and Integration Points
PCI quirk lookup is used by hardware drivers matching board-specific behavior. Fasync helpers are used by ALSA file implementations that need signal delivery without invoking `kill_fasync()` in lock contexts that could deadlock around tasklist internals.

## Risks and Test Signals
Risks include fasync wrapper lifetime races with queued work, duplicate pending entries, and quirk table mask interpretation. Tests should toggle fasync on/off, queue signals during close, verify no use-after-free after `snd_fasync_free()`, and validate PCI quirk exact and masked matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/Makefile -->
# sources/distributed-fs/ceph-client/sound/core/oss/Makefile

## Purpose
This Makefile defines the build composition for ALSA OSS emulation components under `sound/core/oss`.

## Important APIs, Types, and Functions
It builds `snd-mixer-oss` from `mixer_oss.o`. It builds `snd-pcm-oss` from `pcm_oss.o` and conditionally adds plugin objects `pcm_plugin.o`, `io.o`, `copy.o`, `linear.o`, `mulaw.o`, `route.o`, and `rate.o` when `CONFIG_SND_PCM_OSS_PLUGINS` is enabled. Final object inclusion is gated by `CONFIG_SND_MIXER_OSS` and `CONFIG_SND_PCM_OSS`.

## Control Flow and State
There is no runtime state. Build-time state is controlled entirely by Kconfig symbols and object lists.

## Dependencies and Integration Points
The file integrates OSS mixer and PCM emulation with the kernel build system. The plugin source files in this research set are only linked into OSS PCM emulation when plugin support is enabled.

## Risks and Test Signals
Risks are missing plugin objects when PCM OSS format conversion is expected, or unintended object inclusion when Kconfig changes. Test signals are build matrix coverage for `CONFIG_SND_MIXER_OSS`, `CONFIG_SND_PCM_OSS`, and `CONFIG_SND_PCM_OSS_PLUGINS`, plus module load tests for resulting `snd-mixer-oss` and `snd-pcm-oss` modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/copy.c -->
# sources/distributed-fs/ceph-client/sound/core/oss/copy.c

## Purpose
`copy.c` implements the trivial OSS PCM plugin that copies audio frames unchanged between identical source and destination formats. It is used in plugin chains where a pass-through stage is needed.

## Important APIs, Types, and Functions
`copy_transfer()` is the plugin transfer callback. `snd_pcm_plugin_build_copy()` validates identical format, rate, and channel count, builds a plugin named `"copy"`, and installs the transfer callback.

## Control Flow and State
For each channel, transfer verifies byte-aligned areas, silences wanted destination channels when the source channel is disabled, marks destination enable state, and calls `snd_pcm_area_copy()` for enabled channels. It returns the requested frame count unless input validation fails. The plugin holds no custom private state.

## Dependencies and Integration Points
It depends on OSS PCM plugin infrastructure from `pcm_plugin.h`, PCM area helpers, and format metadata. It is linked only when OSS PCM plugin support is enabled.

## Risks and Test Signals
Risks are incorrect enabled/wanted channel propagation and area alignment assumptions. Tests should pass identical interleaved and noninterleaved formats, disabled source channels, zero frames, and invalid mismatched format/rate/channel inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/io.c -->
# sources/distributed-fs/ceph-client/sound/core/oss/io.c

## Purpose
`io.c` implements the terminal OSS PCM I/O plugin. It bridges plugin-channel buffers to actual OSS PCM read and write helpers for playback and capture.

## Important APIs, Types, and Functions
Macros map local calls to `snd_pcm_oss_write3()`, `snd_pcm_oss_writev3()`, `snd_pcm_oss_read3()`, and `snd_pcm_oss_readv3()`. `io_playback_transfer()` writes interleaved or vector channel data. `io_capture_transfer()` reads into interleaved or vector channel buffers. `io_src_channels()` prepares client channels for interleaved playback. `snd_pcm_plugin_build_io()` builds the `"I/O io"` plugin and selects transfer callbacks based on stream direction.

## Control Flow and State
The builder extracts format/rate/channels/access from hardware params, allocates extra per-channel pointer storage, and records access mode. Playback transfer writes `src_channels->area.addr` for interleaved access; for noninterleaved access it fills the extra pointer array with enabled channel addresses or NULL and calls writev. Capture mirrors this into destination channel buffers. Interleaved playback source channels are marked wanted.

## Dependencies and Integration Points
It depends on OSS PCM read/write helpers, PCM hw params accessors, and plugin infrastructure. It is the boundary between conversion plugins and the real OSS PCM substream.

## Risks and Test Signals
Risks include mismatched source/destination channel counts, NULL vector entries for disabled channels, and wrong access mode selection. Tests should cover playback and capture, interleaved and noninterleaved access, disabled channels, short reads/writes, and hardware parameter combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/linear.c -->
# sources/distributed-fs/ceph-client/sound/core/oss/linear.c

## Purpose
`linear.c` implements an OSS PCM plugin for converting between linear PCM sample formats while preserving rate and channel count. It handles sample width, endian conversion, and signedness conversion.

## Important APIs, Types, and Functions
`struct linear_priv` stores conversion offsets, copy sizes, endian-conversion flag, destination byte count, and signedness flip mask. `init_data()` derives these fields from source and destination formats. `do_convert()` converts one sample through a temporary 32-bit container. `linear_transfer()` validates areas, clamps frames to destination availability, and calls `convert()`. `snd_pcm_plugin_build_linear()` validates linear formats and installs the transfer callback.

## Control Flow and State
Transfer walks channels and frames. Disabled source channels silence wanted destinations and clear destination enabled state. Enabled channels compute byte pointers from area first/step fields and convert each frame by copying significant bytes into a temporary value, optionally swapping endian, XORing the sign bit when signedness differs, and copying the requested destination bytes out at the destination offset.

## Dependencies and Integration Points
It depends on PCM format helpers for width, physical width, endian, signedness, and linear-format checks, plus OSS plugin chain infrastructure.

## Risks and Test Signals
Risks are subtle offset mistakes for packed versus physical sample widths, endian/sign conversion ordering, and frame clamping. Tests should convert among 8/16/24/32-bit signed and unsigned formats, little and big endian variants, disabled channels, odd area steps, and zero/overlarge frame counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/linear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/mixer_oss.c -->
# sources/distributed-fs/ceph-client/sound/core/oss/mixer_oss.c

## Purpose
`mixer_oss.c` implements OSS mixer emulation on top of ALSA mixer controls. It registers legacy OSS mixer devices, answers OSS mixer ioctls, maps ALSA kcontrols into OSS mixer slots, exposes a proc remapping interface, and integrates with card registration/free notifications.

## Important APIs, Types, and Functions
File operations are `snd_mixer_oss_open()`, `snd_mixer_oss_release()`, and `snd_mixer_oss_ioctl()`. Core ioctl helpers include `snd_mixer_oss_info()`, `caps`, `devmask`, `stereodevs`, `recmask`, `get_recsrc`, `set_recsrc`, `get_volume`, and `set_volume`. Mapping state uses `struct slot`, `snd_mixer_oss_slot`, present-bit constants, and `snd_mixer_oss_assign_table`. ALSA-control mapping helpers include `snd_mixer_oss_build_test_all()`, `snd_mixer_oss_build_input()`, `snd_mixer_oss_get_volume1*()`, `snd_mixer_oss_put_volume1*()`, and capture-source helpers. Module/card lifecycle is handled by `snd_mixer_oss_notify_handler()`.

## Control Flow and State
Open resolves an OSS mixer minor to a card, checks `card->mixer_oss`, adds the file to the card file list, allocates per-open `snd_mixer_oss_file`, and pins the module. Ioctls dispatch OSS mixer info/version/mask/caps/recsrc operations and generic read/write volume commands based on the command bits. Volume values are exposed as 0-100 left/right bytes and converted to/from ALSA native ranges with `snd_mixer_oss_conv*()`. Mapping scans common ALSA names such as Master, PCM, Mic, Line, Capture, IEC958, and fallback names; for each OSS slot it records present ALSA control numids for global/playback/capture volume, switch, route, and capture-source enum items. Runtime get/put functions find controls by numid under `controls_rwsem`, call `info/get/put`, and notify on changes.

`reg_mutex` protects mixer slot state. `mask_recsrc`, `oss_recsrc`, and optional exclusive get/put recsrc callbacks track recording-source behavior. `/proc/asound/card*/oss_mixer` can read current assignments and write new mappings, dynamically replacing slot assignment tables. On card register, the module registers the OSS device, allocates and initializes `snd_mixer_oss`, populates slots, registers OSS info strings, and creates proc state. Disconnect unregisters the OSS device but leaves mixer memory until free; free removes proc and releases slots.

## Dependencies and Integration Points
It depends on OSS minor registration, ALSA card file tracking, control lookup and notification, proc info helpers, the global `snd_mixer_oss_notify_callback` exported by card init, and optional compat ioctl pointer conversion. It is the main user-visible compatibility bridge for legacy `/dev/mixer`.

## Risks and Test Signals
Risks include fragile name-based control mapping, recsrc semantics differences between exclusive enum and per-slot switches/routes, control removal races, proc remap validation, and lifetime during disconnect with open OSS mixer files. Tests should cover OSS ioctl masks and volume commands, 0-100 conversion edge cases, stereo/mono controls, capture source enum mapping, proc read/write remaps, card disconnect with open mixer, compat ioctls, and fallback table behavior on diverse control layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/mixer_oss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/mulaw.c -->
# sources/distributed-fs/ceph-client/sound/core/oss/mulaw.c

## Purpose
`mulaw.c` implements an OSS PCM plugin for converting between Mu-Law encoded samples and linear PCM formats. It supports both encode and decode directions while preserving rate and channel count.

## Important APIs, Types, and Functions
Low-level conversion helpers are `val_seg()`, `linear2ulaw()`, and `ulaw2linear()`. `struct mulaw_priv` stores the chosen conversion function plus endian, offset, byte-count, and signedness flip settings. `mulaw_encode()` converts native linear samples to Mu-Law; `mulaw_decode()` converts Mu-Law bytes to native linear samples; `mulaw_transfer()` dispatches the selected direction. `snd_pcm_plugin_build_mulaw()` validates formats, chooses encode/decode direction, initializes private data, and installs the transfer callback.

## Control Flow and State
The builder requires equal rates and channel counts. If destination format is `SNDRV_PCM_FORMAT_MU_LAW`, it encodes from source linear format; if source is Mu-Law, it decodes to destination linear format. Transfer validates byte-aligned channel areas in debug builds, clamps frames to destination availability, and iterates channel/frame buffers. Decode maps each Mu-Law byte to signed 16-bit linear and writes it into the native destination format with endian and unsigned conversion. Encode reads native samples into signed 16-bit form and produces one Mu-Law byte per frame.

## Dependencies and Integration Points
It depends on PCM format helpers, OSS plugin infrastructure, and the reference Mu-Law companding algorithm. It is linked into OSS PCM emulation only when plugin support is configured.

## Risks and Test Signals
Risks include signedness flipping for unsigned native formats, endian offset mistakes for packed samples, and clipping/segment behavior around Mu-Law boundaries. Tests should round-trip known Mu-Law vectors, encode/decode all supported linear widths/endians, verify disabled-channel silence behavior, and compare against standard Mu-Law reference values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/mulaw.c -->
