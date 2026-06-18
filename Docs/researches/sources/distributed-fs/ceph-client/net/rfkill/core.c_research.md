# sources/distributed-fs/ceph-client/net/rfkill/core.c

## Purpose
Implements the rfkill core: driver-facing rfkill device allocation/registration/state APIs, global software-state and emergency power-off handling, sysfs attributes, uevents, optional LED triggers, polling, suspend/resume behavior, and the `/dev/rfkill` userspace ABI.

## Important APIs, Types, and Functions
Defines private `struct rfkill`, event wrapper `struct rfkill_int_event`, and per-file-descriptor `struct rfkill_data`. Exported APIs include `rfkill_alloc()`, `rfkill_register()`, `rfkill_unregister()`, `rfkill_destroy()`, `rfkill_set_hw_state_reason()`, `rfkill_set_sw_state()`, `rfkill_init_sw_state()`, `rfkill_set_states()`, `rfkill_blocked()`, `rfkill_soft_blocked()`, `rfkill_find_type()`, `rfkill_pause_polling()`, and `rfkill_resume_polling()`. Under input support it also provides `rfkill_switch_all()`, `rfkill_epo()`, `rfkill_restore_states()`, `rfkill_remove_epo_lock()`, `rfkill_is_epo_lock_active()`, and `rfkill_get_global_sw_state()`.

## Control Flow
Drivers allocate an object with `rfkill_alloc()`, optionally initialize persistent software state, then call `rfkill_register()`, which assigns an index, adds the device, registers LED triggers, starts polling, syncs global state, and emits add events. State changes flow through `rfkill_set_block()` for user/global requested software changes, `rfkill_set_hw_state_reason()` for hardware blocks, or direct setters for driver state. Changes update LED triggers, global triggers, sysfs/uevent state, and `/dev/rfkill` event queues. Userspace opens `/dev/rfkill` to receive initial add events and later changes; writes with `RFKILL_OP_CHANGE` or `RFKILL_OP_CHANGE_ALL` apply software blocks. Module init registers the rfkill class, misc device, LED triggers, and optional input handler; exit reverses that order.

## State and Persistence
Global runtime state includes `rfkill_list`, `rfkill_fds`, `rfkill_global_states[]`, `rfkill_epo_lock_active`, default state module parameter, and optional input-disable count. Each rfkill tracks software/hardware block bits, previous software bit during set calls, hard block reason mask, index, registration/persistence/poll/suspend flags, ops, device, works, and name. Each open file owns a capped event list and ABI max-size setting. No durable persistence is written, but devices may be marked persistent so global sync does not override their initialized software state.

## Dependencies and Integration
Depends on the device model/class core, sysfs, miscdevice, wait queues, poll/read/write/ioctl file operations, capabilities (`CAP_NET_ADMIN` for sysfs writes), LED triggers when configured, PM sleep callbacks, workqueues, input bridge through `rfkill.h`, and driver `struct rfkill_ops` callbacks.

## Risks and Test Signals
Risks include the documented global mutex versus driver lock ABBA potential, event queue overflow per fd, userspace ABI size compatibility, state races around `RFKILL_BLOCK_SW_SETCALL`, polling during suspend/unregister, and EPO lock semantics. Test signals are sysfs `soft`/`state` permission and value checks, `/dev/rfkill` initial and change event ordering, max event cap behavior, ioctl max-size negotiation and input disable, LED trigger updates, poll pause/resume, register/unregister with active readers, and EPO restore/unlock flows.
