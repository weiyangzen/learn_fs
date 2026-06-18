# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/internals.h

Purpose: this header defines raw NAND core-internal declarations and helper wrappers. It is explicitly for core raw NAND files, not controller drivers.

Important APIs, types, and functions: it lists manufacturer IDs, `struct nand_manufacturer_ops`, `struct nand_manufacturer_desc`, external manufacturer operation tables, `nand_flash_ids[]`, the `dist3_pairing_scheme`, and raw NAND core functions for manufacturer lookup, bad-block management, erase, ONFI/Jedec detection, timing selection, feature access, raw-page unsupported stubs, parameter page reads, ID decoding, panic wait, and string sanitization. Inline helpers include `nand_has_exec_op()`, `nand_check_op()`, `nand_exec_op()`, and `nand_controller_can_setup_interface()`.

Control flow: core code includes this header to dispatch optional controller operations and to share non-public core entry points. `nand_check_op()` calls a controller's `exec_op(..., true)` when present. `nand_exec_op()` validates target index and calls `exec_op(..., false)`, returning `-ENOTSUPP` when no modern operation hook exists. `nand_controller_can_setup_interface()` gates interface setup on the controller op being present and `NAND_KEEP_TIMINGS` being absent.

State and persistence: the header does not allocate state, but it defines global raw NAND registries and core contracts. Manufacturer ops may initialize per-chip vendor state and later clean it up; BBT and pairing declarations point at persistent core behavior implemented elsewhere.

Dependencies and integration points: the only include is `<linux/mtd/rawnand.h>`. Integration points span the raw NAND manufacturer database, ONFI/JEDEC parsers, controller operation model, bad-block table implementation, and timing negotiation.

Risks: because this is internal ABI, changing function signatures or helper semantics can break many raw NAND core files at once. `nand_exec_op()` uses `WARN_ON()` for out-of-range chip select, so invalid callers produce noisy kernel warnings. Controller drivers should not include this header, and doing so would couple them to unstable core internals.

Test signals: relevant coverage is raw NAND core build coverage, manufacturer detection for listed vendors, ONFI/JEDEC detection, invalid chip-select warning behavior, fallback behavior for legacy controllers without `exec_op`, and setup-interface gating when `NAND_KEEP_TIMINGS` is set.
