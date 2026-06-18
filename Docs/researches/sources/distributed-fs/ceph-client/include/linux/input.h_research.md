<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input.h -->
# sources/distributed-fs/ceph-client/include/linux/input.h

Purpose: Main in-kernel input subsystem interface for devices, handlers, handles, events, absolute axes, polling, grabs, timestamps, and force feedback.

Important APIs/types/functions: `struct input_value`, `enum input_clock_type`, `struct input_dev`, `input_handler`, `input_handle`, and `ff_device` define device capabilities/state, event routing, open/close, keymaps, polling, multi-touch, autorepeat, locking, and force-feedback effects. APIs allocate/register/unregister devices and handlers, open/close handles, grab/release, inject/report events, configure abs axes, keycodes, softrepeat, timestamps, polling intervals, minors, force feedback, and memless FF.

Control flow: Drivers allocate/register `input_dev`; handlers connect and open handles; drivers call `input_event()` or report helpers; core batches events to handlers until `input_sync()`. Open/close transitions start or stop hardware.

State/persistence: `input_dev` persists across registration and holds capability bitmaps, current key/LED/switch state, abs info, queued values, timestamps, users, locks, and device-model object.

Dependencies/integration: Depends on UAPI input ids/events, device model, fs, timers, lists, mod_devicetable, multitouch, and force feedback.

Risks: Event callbacks run under spinlock and cannot sleep; capability/keymap bitmaps must match UAPI/mod_devicetable limits; unregister/open races require mutex and going-away handling.

Test signals: Device registration, evdev event delivery, grabs, inhibit/uninhibit, keymap ioctls, polling, abs configuration, force-feedback upload/play/erase, and lockdep for callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input.h -->
