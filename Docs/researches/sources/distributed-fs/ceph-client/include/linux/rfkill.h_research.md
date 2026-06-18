# sources/distributed-fs/ceph-client/include/linux/rfkill.h

Purpose: this header declares the in-kernel rfkill API used by radio/transmitter drivers to expose and control software and hardware block state.

Important APIs/types/functions: it remaps UAPI rfkill states to kernel-only `enum rfkill_user_states` and undefines direct UAPI state names to prevent kernel misuse. `struct rfkill_ops` provides `poll`, `query`, and mandatory `set_block` callbacks. APIs include `rfkill_alloc()`, `rfkill_register()`, polling pause/resume, unregister/destroy, hardware/software state setters, persistent software-state initialization, combined state setting, block-state queries, `rfkill_find_type()`, and optional LED trigger helpers.

Control flow: a driver allocates an rfkill object, initializes software/hardware state if needed, registers after it can service callbacks, then the core invokes `set_block()` for user or policy changes. Hardware events call `rfkill_set_hw_state()` or `_reason()`, soft-state events call `rfkill_set_sw_state()`, and polling/query callbacks synchronize state. Unregister waits until callbacks are no longer in flight, after which destroy releases the object.

State and persistence: the opaque rfkill object stores block state, persistent flag, polling, callbacks, userspace device state, and optional LED trigger. Persistent devices may preserve software block state across power transitions.

Dependencies and integration points: depends on UAPI rfkill definitions, device model, LEDs, mutex/list infrastructure, and network/wireless/Bluetooth/platform radio drivers.

Risks: drivers must ignore unblock requests when hard-blocked, handle callback reentry from state setters, and distinguish hard from soft state. Disabled-config stubs return `ERR_PTR(-ENODEV)` from alloc but register treats that sentinel as success. Test signals include soft/hard block transitions, rfkill userspace events, polling pause/resume, suspend/resume state retention, LED trigger behavior, and builds with rfkill disabled.
