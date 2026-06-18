# sources/distributed-fs/ceph-client/include/media/rc-core.h

## Purpose
Defines the remote-controller core device model, key reporting APIs, raw IR event APIs, LIRC per-file state, and helpers for scancode extraction/encoding.

## Important APIs, Types, and Functions
`enum rc_driver_type` distinguishes scancode, raw IR RX, and raw IR TX drivers. `rc_scancode_filter`, `rc_filter_type`, `lirc_fh`, and the large `rc_dev` model device identity, rc-map, locks, raw state, input device, users, protocols, filters, key state, timers, LIRC chardev state, and driver callbacks. APIs include allocate/register/unregister/free, managed variants, `rc_keydown()`, `rc_keydown_notimeout()`, `rc_keyup()`, `rc_repeat()`, keycode lookup, raw event storage/filtering/timeout/idle, raw encoding, overflow helper, `ir_extract_bits()`, and `ir_nec_bytes_to_scancode()`.

## Control Flow
Drivers allocate an `rc_dev`, fill identity/protocol/callback fields, register it, then report decoded scancodes or raw pulse/space events. The core manages input keydown/repeat/keyup timers, protocol changes, filters, LIRC queues, and optional transmit operations.

## State and Persistence Behavior
`rc_dev` persists per remote device and owns keypress state, protocol masks, filters, input child device, timers, user count, raw decoder state, and optional LIRC file handles. `keylock` protects key state; `lock` serializes protocol setup/show/store behavior.

## Dependencies and Integration Points
Depends on spinlocks, cdev, kfifo, timers, input, LIRC UAPI, and rc-map. Integrates IR receivers/transmitters, CEC RC, input events, sysfs protocol controls, and LIRC character devices.

## Risks
Timer/key state races can leave keys stuck or repeats wrong. Protocol bitmasks must match decoder availability. Raw event duration limits and timeout handling affect decoder correctness. NEC byte helper intentionally distinguishes NEC, NECX, and NEC32 based on complement checks.

## Test Signals
Register/unregister, keydown/repeat/keyup timing, protocol enable changes, wakeup filters, LIRC open/poll/read/write, raw event overflow/timeout, NEC scancode decoding variants, transmit carrier/duty/mask callbacks, and suspend wakeup filtering.
