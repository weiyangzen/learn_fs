# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/pixelgen_private.h

Purpose: provides pixel generator register access plus state capture and dump helpers.

Important APIs/types/functions: DLI helpers are `pixelgen_ctrl_reg_load()` and `pixelgen_ctrl_reg_store()`. NCI helpers are `pixelgen_ctrl_get_state()` and `pixelgen_ctrl_dump_state()`.

Control flow: register helpers assert valid pixelgen ID/base and access word-indexed registers. `pixelgen_ctrl_get_state()` reads common, PRBS, sync generator, and TPG register indices from `PixelGen_SysBlock_defs.h`. The dump helper prints the captured values.

State and persistence: stores mutate pixel generator hardware; snapshots are transient.

Dependencies and integration: depends on pixelgen public/local definitions, HRT register indices, and CSS device access. Used for test-pattern/synthetic input diagnostics.

Risks and test signals: dump prints `tpg_hcnt_mask` twice and omits a distinct `tpg_vcnt_mask` line, reducing diagnostic quality. Tests should validate register read order, enable bits for PRBS/TPG/sync generator, and state dump correctness.
