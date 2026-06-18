# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dbg_hsi.h

## Purpose

`qed_dbg_hsi.h` defines the QED debug tools hardware/software interface. It is mostly an ABI/schema header for firmware-generated debug arrays, GRC dumps, idle checks, attention parsing, MCP traces, debug bus capture, register FIFOs, IGU FIFOs, protection override dumps, and firmware assert dumps.

## Important APIs, Types, and Functions

- Hardware block and buffer identity enums: `enum block_id`, `enum bin_dbg_buffer_type`, `enum dbg_attn_type`, `enum dbg_bus_clients`, `enum dbg_bus_constraint_ops`, `enum dbg_bus_states`, `enum dbg_bus_storm_modes`, `enum dbg_bus_targets`, `enum dbg_grc_params`, `enum dbg_status`, `enum dbg_storms`, and `enum ilt_clients`.
- Packed/bitfield schemas: attention mappings/results, mode headers, dump register/memory descriptors, idle-check rules/results, reset registers, debug bus line/block/storm data, GRC parameter data, MCP trace metadata, and per-hardware-function `struct dbg_tools_data`.
- Debug dump APIs: `qed_dbg_grc_get_dump_buf_size()`, `qed_dbg_grc_dump()`, idle-check, MCP trace, register FIFO, IGU FIFO, protection override, firmware assert, and attention read/print functions.
- User/parser APIs: `qed_dbg_user_set_bin_ptr()`, `qed_dbg_alloc_user_data()`, `qed_dbg_get_status_str()`, result buffer size calculators, result printers, MCP trace metadata setters/free functions, and attention parsing.
- Utility hardware access declarations: `qed_read_regs()` and `qed_read_fw_info()`.

## Control Flow

This file does not implement algorithms; it declares the data contract used by debug implementation files. Typical control flow is: set debug binary pointers, configure optional GRC parameters, ask for a dump buffer size, allocate a caller buffer, collect a raw dump through a `qed_dbg_*_dump()` routine using a PTT window, and optionally parse/print the raw dump through a corresponding `qed_print_*_results()` function.

## State and Persistence Behavior

State is represented by caller-owned buffers and by `struct dbg_tools_data` attached to each hardware function by implementation code. It tracks configured GRC params, debug bus state, idle-check buffer sizing, mode enable arrays, block reset state, chip/hardware topology, DMAE usage, pretend/split parameters, and register read counts. MCP trace parsing also owns optional allocated metadata through `struct mcp_trace_meta`.

## Dependencies and Integration Points

The header depends on Linux primitive types, I/O helpers, bitops, delay, kernel, list, and slab headers. It also references QED core objects (`struct qed_hwfn`, `struct qed_ptt`, `struct fw_info`) that are defined elsewhere. It is shared by debug collection code, ethtool/devlink-style diagnostic paths, firmware dump consumers, and context code via `enum ilt_clients`.

## Risks and Edge Cases

- Many structures encode bitfields with explicit masks/shifts; firmware tooling, hardware register definitions, and parser code must agree exactly.
- The enum ordering is part of the implicit ABI for firmware-generated debug arrays. Reordering breaks binary buffer interpretation.
- Public dump functions return `enum dbg_status`, not Linux `errno`, so callers need correct status translation.
- Buffer sizing is two-phase; callers must honor returned dword or byte sizes to avoid `DBG_STATUS_DUMP_BUF_TOO_SMALL` or parse failures.
- Some debug functions may halt/resume MCP, access wide-bus registers, or rely on block reset state; diagnostic paths should be careful during error recovery.

## Test Signals

Validation includes compiling all debug implementations against this header, collecting GRC/idle/MCP/FIFO/assert dumps on supported chips, parsing dumps with expected status strings, exercising invalid buffer sizes and invalid parameters, and confirming firmware debug bundle version compatibility through `qed_dbg_set_bin_ptr()`/`qed_dbg_user_set_bin_ptr()`.
