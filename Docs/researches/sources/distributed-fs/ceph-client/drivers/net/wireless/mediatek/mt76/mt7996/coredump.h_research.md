# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/coredump.h

## Purpose
This header defines the MT7996 devcoredump wire format, memory-region descriptors, and CONFIG_DEV_COREDUMP-dependent function declarations/stubs.

## Important APIs, Types, And Functions
Types include `mt7996_coredump`, `mt7996_coredump_mem`, `mt7996_mem_hdr`, and `mt7996_mem_region`. It declares or stubs `mt7996_coredump_get_mem_layout()`, `mt7996_coredump_new()`, `mt7996_coredump_submit()`, `mt7996_coredump_register()`, and `mt7996_coredump_unregister()`.

## Control Flow
No executable logic exists except inline stubs when devcoredump is disabled. Those stubs return harmless defaults so core recovery code can compile without conditional call sites.

## State And Persistence
The packed coredump format persists in devcoredump output and includes magic, length, GUID, timestamp, kernel release, firmware version, device id, firmware state, PC/LR stacks, and optional memory data.

## Dependencies And Integration Points
It includes `mt7996.h` for device types and uses `ETHTOOL_FWVERS_LEN`, GUID types, and kernel packing conventions. It is consumed by coredump implementation and recovery paths.

## Risks
The packed format is userspace-visible. Changing fields can break dump parsers. Stubs must match real function signatures exactly. Optional memory headers must align with builder logic.

## Test Signals
Builds with `CONFIG_DEV_COREDUMP=y/n`, successful recovery code linkage, and parsable devcoredump blobs validate this header.
