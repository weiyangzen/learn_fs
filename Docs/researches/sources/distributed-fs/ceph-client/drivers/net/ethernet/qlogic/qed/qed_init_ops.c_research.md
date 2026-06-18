# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_init_ops.c

## Purpose
`qed_init_ops.c` interprets firmware initialization scripts and manages runtime initialization data. It loads firmware binary table pointers, stores runtime register values, writes array/zero/inline/runtime init commands, handles polling/read commands, executes callback ops, initializes global GTT windows, and installs the generated IRO array pointer.

## Important APIs, Types, and Functions
- `qed_init_iro_array()` points `cdev->iro_arr` at the E4 IRO triplet array.
- `qed_init_store_rt_reg()` and `qed_init_store_rt_agg()` stage runtime register values in `p_hwfn->rt_data`.
- `qed_init_alloc()` and `qed_init_free()` allocate/free runtime validity and value arrays for PFs.
- `qed_init_run()` is the top-level init-op interpreter.
- `qed_gtt_init()` writes the static PXP global windows.
- `qed_init_fw_data()` parses firmware binary buffer headers into `cdev->fw_data`.
- Internal helpers handle DMAE/PIO array writes, zero fills, zipped arrays, pattern arrays, runtime segments, polling comparisons, mode trees, phase conditionals, and DMAE-ready callbacks.

## Control Flow
The firmware data setup reads `bin_buffer_hdr` entries and records pointers to version info, init ops, array data, mode tree, and overlays. During `qed_init_run()`, the driver allocates an unzip buffer, walks every init op, and dispatches by opcode. Write commands select inline, zeros, array, or runtime data; array commands may unzip compressed payloads or repeat pattern payloads; runtime commands flush only valid staged segments and invalidate them after writing. Read commands can be simple reads or bounded polls with EQ/AND/OR comparison. IF_MODE and IF_PHASE commands skip forward by encoded command offsets when conditions do not match. The DMAE-ready callback runs `qed_dmae_sanity()` and enables DMAE for the rest of engine phase.

## State and Persistence
Runtime state is held in `p_hwfn->rt_data.init_val` and `p_hwfn->rt_data.b_valid`, plus the temporary `p_hwfn->unzip_buf`. Firmware table pointers are stored in `cdev->fw_data`. GTT global-window configuration persists in hardware registers. Runtime validity bits are cleared as each value is emitted.

## Dependencies and Integration Points
This file uses `qed_hw.c` for register and DMAE access, `qed_init_ops.h` macros for runtime storage, `qed_iro_hsi.h` for IRO offset selection, QED HSI init-op structures, and SR-IOV PF/VF checks. It is central to device bring-up and receives runtime values prepared by `qed_init_fw_funcs.c`, interrupt setup, context setup, and other init code.

## Risks
- Init scripts are firmware-defined; incorrect table offsets or corrupted binary data can drive invalid register writes.
- Zipped array expansion depends on `MAX_ZIPPED_SIZE` and `qed_unzip_data()` returning a nonzero output length.
- `qed_init_cmd_wr()` does not propagate the return from `qed_init_rt()` in the runtime case, so runtime DMAE errors could be lost in that path.
- Poll commands log timeouts but do not fail `qed_init_run()`, which may allow later init steps after a hardware readiness issue.
- Runtime arrays are skipped for VFs, so callers must avoid PF-only runtime staging assumptions in VF flows.

## Test Signals
Look for successful firmware-data parsing, clean init phase completion, no "Failed to unzip dmae data" messages, no poll timeout logs, successful DMAE-ready sanity callback, expected runtime values being invalidated after flush, and successful GTT window reads during later hardware access.
