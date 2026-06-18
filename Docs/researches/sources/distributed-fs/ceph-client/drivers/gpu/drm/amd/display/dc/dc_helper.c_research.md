# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_helper.c

## Purpose
`dc_helper.c` implements low-level register helper routines used by DC register macros. It supports direct MMIO read/modify/write, indirect register access, register polling, optional DMUB offload/gathering of register sequences, and small utility helpers for DCE/DCN version naming and VRR support.

## Important APIs, Types, And Functions
`generic_reg_update_ex` builds a mask/value set from variadic field triples, then either queues a DMUB read-modify-write sequence when offload gathering is active or performs direct `dm_read_reg`/`dm_write_reg`. `generic_reg_set_ex` applies fields to a caller-provided register value and either queues burst writes or writes directly.

`generic_reg_get` through `generic_reg_get8` read one register and extract up to eight fields. Separate fixed-arity helpers are intentionally used instead of a pointer-heavy variadic get form, which the file comments call out as stack-corruption-prone.

`generic_reg_wait` polls a field until it equals a condition value, sleeping or delaying between tries. When DMUB gathering is active, it packs a `DMUB_CMD__REG_REG_WAIT` request instead. It asserts that total timeout is at most 3 seconds, logs long waits, warns on timeout, and breaks to debugger.

Indirect helpers are `generic_write_indirect_reg`, `generic_read_indirect_reg`, `generic_indirect_reg_get`, `generic_indirect_reg_update_ex`, `generic_indirect_reg_update_ex_sync`, and `generic_indirect_reg_get_sync`. They use index/data register pairs or CGS PCIE index access.

DMUB offload helpers include `reg_sequence_start_gather`, `reg_sequence_start_execute`, and `reg_sequence_wait_done`. Internal helpers pack read-modify-write, burst-write, and reg-wait DMUB commands and flush when buffers fill or command type/address changes.

`dce_version_to_string` maps known DCE/DCN version enums to display strings. `dc_supports_vrr` returns true for DCE versions at or above `DCE_VERSION_8_0`.

## Control Flow And State
The main state is `ctx->dmub_srv->reg_helper_offload`. `reg_sequence_start_gather` marks gathering active when DMUB offload is available and enabled. Subsequent register set/update/wait helpers append command data instead of touching MMIO directly. `reg_sequence_start_execute` clears gathering and submits the pending command based on command type. `reg_sequence_wait_done` waits for DMUB idle unless emulation is active.

For non-offload paths, register helpers synchronously read/write MMIO. DMUB offload can switch to burst-write mode after repeated same-address read-modify-write patterns, using `same_addr_count` and `should_burst_write`.

## Dependencies And Integration Points
It includes Linux delay/stdarg, `dm_services.h`, `dc.h`, `dc_dmub_srv.h`, and `reg_helper.h`. It integrates with nearly all DC hardware programming blocks through `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and indirect register macros. It depends on DMUB command definitions and `dc_wake_and_execute_dmub_cmd`.

## Risks
The variadic field APIs rely on exact argument ordering and integer promotion; mismatches can corrupt updates. DMUB gather sequencing is global per context, so nested or mismatched gather/execute calls can leave stale commands; the code asserts but still requires caller discipline. `generic_reg_set_ex` returns a `bool`-like result from `dmub_reg_value_burst_set_pack` in offload mode despite the function returning `uint32_t`, which callers should not treat as a readback value. Register waits can block up to the requested timeout and break to debugger on failure. Offloaded read-modify-write returns packed values rather than hardware states, so callers must not depend on readback semantics during offload.

## Test Signals
Register helper unit tests should cover mask composition, multi-field set/update, DMUB buffer flushing, burst-write transition, gather/execute/wait ordering, indirect access, timeout behavior, and version string mapping. Hardware integration signals include clean display bring-up, no hangs in register waits, correct DMUB idle handling, and stable behavior with `dmub_offload_enabled` toggled.
