# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_reg.c

Purpose: provides a small hardware register-range validator for RVU AF code. In this file the implemented map is for NIX transmit scheduler queue register access, ensuring mailbox or debug paths only expose aligned offsets in approved scheduler-level ranges.

Important APIs and types: `struct reg_range` stores inclusive start and exclusive end offsets. `struct hw_reg_map` describes one register block selector with a register block id, range count, mask, and up to `MAX_REG_RANGES` valid ranges. `txsch_reg_map[]` defines allowed offsets for `NIX_TXSCH_LVL_SMQ`, `TL4`, `TL3`, `TL2`, and `TL1`. `rvu_check_valid_reg()` is the exported validator, taking a register map id, register block id, and register offset.

Control flow: `rvu_check_valid_reg()` first rejects offsets that are not 64-bit aligned. It then selects the map only for `TXSCHQ_HWREGMAP`; any other map id is rejected. It validates the scheduler level index, checks that the table entry's `regblk` matches the requested block, masks the register offset through the map's mask, and scans configured ranges. The function returns true only if the masked offset is greater than or equal to a range start and strictly less than that range end.

State and persistence: the only persistent state is the static read-only range table. No hardware registers are read or written here; this file is a validation gate for other code that performs register access.

Dependencies and integration: depends on Linux module/PCI includes and RVU/NIX constants from `rvu_struct.h`, `common.h`, `mbox.h`, and `rvu.h`. It integrates with mailbox/debug register access paths that need to validate transmit scheduler register offsets before servicing a request.

Risks: the table is a hardware ABI allowlist. Missing a valid range blocks legitimate diagnostics or configuration; adding too broad a range can expose unsafe registers. The mask is currently `0xFFFF` for all levels, so callers must understand that high address bits are ignored during validation. The range end is exclusive, which must match the intended register definitions. Only TX scheduler maps are supported; future register maps need explicit additions.

Test signals: unit-style tests or mailbox tests should verify rejection of unaligned offsets, unknown map ids, invalid scheduler levels, out-of-range offsets, and acceptance of each listed range boundary start with rejection at each exclusive end. Integration tests should confirm callers using this validator cannot access non-allowlisted TX scheduler registers.
