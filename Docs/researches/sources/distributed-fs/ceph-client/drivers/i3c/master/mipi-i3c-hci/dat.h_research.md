# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dat.h

## Purpose

`dat.h` defines the shared Device Address Table interface for the HCI driver. It names common DAT flags and declares a vtable for allocation, address programming, flag mutation, lookup, and restore operations.

## Important APIs, Types, and Functions

- `DAT_0_I2C_DEVICE`, `DAT_0_SIR_REJECT`, and `DAT_0_IBI_PAYLOAD` are global DAT word-0 flags used by core attach and IBI control.
- `struct hci_dat_ops` provides `init`, `alloc_entry`, `free_entry`, `set_dynamic_addr`, `set_static_addr`, `set_flags`, `clear_flags`, `get_index`, and `restore`.
- `mipi_i3c_hci_dat_v1` is the concrete v1 DAT implementation.

## Control Flow

Core code calls the v1 operations when HCI v1 descriptors require device indexes rather than direct addresses. Attach paths allocate and program entries; CCC preparation can look up a directed address; IBI enable/disable and request paths mutate flags; runtime resume restores cached entries.

## State and Persistence Behavior

The header describes operations over `hci->DAT`, `hci->DAT_data`, and MMIO `hci->DAT_regs`; actual storage is owned by `struct i3c_hci` and implemented in `dat_v1.c`.

## Dependencies and Integration Points

It depends on `struct i3c_hci` and `struct dat_words` from `hci.h`. It is used by `core.c`, `cmd_v1.c`, and `dat_v1.c`.

## Risks and Edge Cases

The API is index-based and assumes the implementation has initialized DAT metadata before callers allocate or look up entries. v2 direct-address command flow reduces DAT usage, so call sites must avoid assuming DAT exists in all HCI modes.

## Test Signals

Attach/detach tests should confirm entry allocation and freeing. IBI tests should verify SIR reject and payload flags. Resume tests should confirm cached DAT words are written back to hardware.
