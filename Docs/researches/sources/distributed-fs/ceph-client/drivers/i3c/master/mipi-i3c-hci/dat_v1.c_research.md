# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dat_v1.c

## Purpose

`dat_v1.c` implements the v1 HCI Device Address Table as cached 8-byte entries mirrored to MMIO. It provides slot allocation, dynamic/static address programming, flag mutation, address lookup, and runtime restore support.

## Important APIs, Types, and Functions

- DAT field macros describe auto-command fields, NACK retry, ring ID, dynamic address/parity, timestamp, master-request/SIR reject, IBI payload, and static address fields.
- `hci_dat_v1_init()` validates register-backed 8-byte DAT support, allocates the cache array and allocation bitmap, and clears hardware entries.
- `hci_dat_v1_alloc_entry()` finds a free bit, marks it, and initializes default reject flags (`SIR_REJECT | MR_REJECT`).
- `hci_dat_v1_free_entry()` clears cached/hardware words and releases the bitmap slot.
- `hci_dat_v1_set_dynamic_addr()` writes the dynamic address and parity bit.
- `hci_dat_v1_set_static_addr()`, `set_flags()`, `clear_flags()`, `get_index()`, and `restore()` provide the remaining vtable operations.

## Control Flow

Initialization occurs during bus init or lazily on first allocation. Allocation scans the bitmap with `find_first_zero_bit()`, writes default flags, and returns the DAT index to per-device data. Address setters read the cached word, update only the relevant fields, and write through to MMIO. `get_index()` scans allocated entries for a matching dynamic address. `restore()` iterates all cached entries and rewrites both words after controller reset.

## State and Persistence Behavior

`hci->DAT` is the persistent software mirror of hardware DAT words. `hci->DAT_data` is the allocation bitmap. Both are devm-managed and survive controller runtime resets, allowing `restore()` to repopulate hardware.

## Dependencies and Integration Points

The implementation uses Linux bitmap helpers, device-managed allocation, `parity8()`, and MMIO `writel()`. It is used by v1 command preparation, core attach/detach, IBI flag control, DAA, and runtime resume.

## Risks and Edge Cases

Only register-space DAT with 8-byte entries is supported; other HCI DAT storage formats return `-EOPNOTSUPP`. `get_index()` assumes `DAT_data` is initialized. The parity bit uses inverted parity semantics from the HCI format and must not be simplified without spec review. Concurrent DAT mutations rely on higher-level I3C core serialization; this file has no local lock.

## Test Signals

Test DAT init rejection for missing/non-8-byte DAT, bitmap exhaustion, default reject flags, dynamic parity encoding, static I2C entries, set/clear flag preservation, directed address lookup, and restore after simulated hardware reset.
