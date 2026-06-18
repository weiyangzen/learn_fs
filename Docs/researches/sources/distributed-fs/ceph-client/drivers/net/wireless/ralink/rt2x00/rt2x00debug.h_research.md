# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00debug.h

## Purpose
Defines the debugfs register callback contract for rt2x00 chip drivers. It lets each hardware module describe readable/writable register spaces without hard-coding CSR, EEPROM, BBP, RF, or RFCSR access in generic debugfs code.

## Important APIs, Types, And Functions
`enum rt2x00debugfs_entry_flags` currently defines `RT2X00DEBUGFS_OFFSET`, meaning callbacks receive byte offsets rather than word indexes. `RT2X00DEBUGFS_REGISTER_ENTRY()` generates a per-register-class structure containing read/write callbacks, flags, base, word size, and word count. `struct rt2x00debug` groups owner module and register entries for CSR, EEPROM, BBP, RF, and RFCSR.

## Control Flow
Chip drivers populate a `struct rt2x00debug` and attach it to `rt2x00_ops.debugfs`. `rt2x00debug_register()` checks which read callbacks exist, creates offset/value debugfs files, and uses the callbacks to perform register access after validating requested word count.

## State And Persistence
This header declares metadata only. Runtime offset state and debugfs objects are owned by `rt2x00debug.c`; hardware register state is accessed through callbacks.

## Dependencies And Integration Points
Depends on `struct rt2x00_dev` and module ownership. Integrated with optional `CONFIG_RT2X00_LIB_DEBUGFS` support and chip-specific debug descriptors such as `rt2800_rt2x00debug`.

## Risks
Wrong word size/count/base exposes invalid hardware offsets. Missing module ownership can allow unload while debugfs files are open. Direct writes bypass normal driver locking unless callbacks implement it.

## Test Signals
Debugfs registration for each chip family, module get/put behavior while files are open, bounds checks for offsets, and safe CSR/EEPROM/BBP/RF/RFCSR read/write operations.
