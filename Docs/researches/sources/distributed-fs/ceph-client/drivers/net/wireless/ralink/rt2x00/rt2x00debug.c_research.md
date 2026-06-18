# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00debug.c

## Purpose
Implements rt2x00 debugfs support. It creates per-device debugfs files for driver/chipset metadata, device and capability flags, hardware restart trigger, register read/write windows, queue statistics, crypto statistics, and a single-reader binary frame dump stream.

## Important APIs, Types, And Functions
Private state is held in `struct rt2x00debug_intf`, including debug callbacks, debugfs dentries, frame dump open flag, skb queue, waitqueue, crypto counters, metadata blobs, and register offsets. Exported functions are `rt2x00debug_update_crypto()`, `rt2x00debug_dump_frame()`, `rt2x00debug_register()`, and `rt2x00debug_deregister()`. Macro-generated file operations implement CSR/EEPROM/BBP/RF/RFCSR register access.

## Control Flow
Registration allocates `rt2x00debug_intf`, attaches it to `rt2x00dev`, creates a driver folder under the wiphy debugfs directory, writes static metadata blobs, exposes flags/restart files, creates register offset/value pairs for supported register classes, initializes frame dump queue/waitqueue, and exposes queue and crypto stats. Dumping frames checks whether the dump file is open, bounds the queue length to 20, copies a `rt2x00dump_hdr`, descriptor, and frame data into a new skb, queues it, and wakes readers. Reads block until a dump skb is available. Deregistration purges queues, removes debugfs recursively, frees blobs and state.

## State And Persistence
Debugfs state exists while registered and is not persistent across remove/suspend. Crypto counters accumulate by cipher while the debugfs interface lives. Frame dump has single-open state and queued copied skbs. Register offsets are mutable debugfs variables and persist until deregistration.

## Dependencies And Integration Points
Depends on `CONFIG_RT2X00_LIB_DEBUGFS`, Linux debugfs, poll/waitqueue/usercopy APIs, rt2x00 register access callbacks from `struct rt2x00debug`, `rt2x00dump.h` ABI, mac80211 wiphy debugfs root, and `ieee80211_restart_hw()` for restart injection.

## Risks
Debugfs register writes allow direct hardware mutation and can destabilize devices. `rt2x00debug_update_crypto()` assumes `debugfs_intf` exists when compiled in; call ordering must respect registration. Frame dump allocation is GFP_ATOMIC and may drop frames under pressure. Poll returns writable-style bits for readable data, which is unusual. Restart trigger is rate-limited globally by a static `last_reset`.

## Test Signals
Open/read queue dump with TX/RX traffic, verify binary `rt2x00dump_hdr` layout, read queue and crypto stats, read/write each supported register class, trigger restart with and without `CAPABILITY_RESTART_HW`, suspend/resume debugfs deregistration/registration, and run KASAN/usercopy checks.
