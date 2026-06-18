# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/utils.h

## Purpose
This header declares PCIe diagnostic dumping and provides small register bitfield helpers for iwlwifi PCIe code.

## Important APIs, Types, and Functions
- `iwl_trans_pcie_dump_regs()` is declared for error diagnostics.
- `_iwl_trans_set_bits_mask()` reads a CSR/MMIO register, clears a mask, applies a masked value, and writes the result.
- `iwl_trans_clear_bit()` and `iwl_trans_set_bit()` are convenience wrappers for clearing or setting all bits in a mask.

## Control Flow
The inline helper performs read-modify-write through `iwl_read32()` and `iwl_write32()`. With `CONFIG_IWLWIFI_DEBUG`, it warns if the requested value contains bits outside the mask.

## State and Persistence Behavior
The helpers mutate device register state directly. They do not lock internally, so callers must satisfy any register-access serialization requirements before calling them.

## Dependencies and Integration Points
The header includes `iwl-io.h` for `struct iwl_trans` and register accessors. It is used by PCIe transport code, including command wake/clear paths in `gen1_2/tx.c`.

## Risks and Edge Cases
These helpers are generic and do not enforce hardware access preconditions. Read-modify-write on registers with write-one-to-clear or volatile bits would be unsafe unless the caller selects appropriate registers. Debug masking catches value mistakes only in debug builds.

## Test Signals
Build coverage validates inline users. Runtime evidence is correct manipulation of CSR bits such as MAC access request/clear paths and absence of debug WARNs for masked values.
