# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_debug.h

## Purpose

`qed_debug.h` is the narrow public interface for the QED driver's debug feature collection layer. It declares the feature identifiers and callable APIs used by the rest of the driver or debugfs plumbing to size, collect, and manage debug dumps implemented in `qed_debug.c`.

## Important APIs And Types

The header defines `enum qed_dbg_features`, which indexes the driver-supported debug features:

- `DBG_FEATURE_GRC`
- `DBG_FEATURE_IDLE_CHK`
- `DBG_FEATURE_MCP_TRACE`
- `DBG_FEATURE_REG_FIFO`
- `DBG_FEATURE_IGU_FIFO`
- `DBG_FEATURE_PROTECTION_OVERRIDE`
- `DBG_FEATURE_FW_ASSERTS`
- `DBG_FEATURE_ILT`
- `DBG_FEATURE_NUM`

It forward-declares `struct qed_dev` and `struct qed_hwfn`, then declares three API families:

- Per-feature dump and size APIs: `qed_dbg_grc()`, `qed_dbg_idle_chk()`, `qed_dbg_reg_fifo()`, `qed_dbg_igu_fifo()`, `qed_dbg_protection_override()`, `qed_dbg_fw_asserts()`, `qed_dbg_ilt()`, `qed_dbg_mcp_trace()`, plus matching `*_size()` functions. Dump calls take a `struct qed_dev *`, caller-provided buffer, and `u32 *num_dumped_bytes`.
- Generic dispatch APIs: `qed_dbg_feature()` and `qed_dbg_feature_size()` accept `enum qed_dbg_features` and route to the same implementation used by the feature-specific wrappers.
- Device-level debug management: `qed_dbg_all_data()`, `qed_dbg_all_data_size()`, `qed_dbg_phy_size()`, `qed_get_debug_engine()`, `qed_set_debug_engine()`, `qed_dbg_pf_init()`, and `qed_dbg_pf_exit()`.

## Control Flow And Integration

The header does not implement logic; it exposes the contract consumed by other QED modules. Typical use is:

1. Call `qed_dbg_pf_init()` during PF/device initialization after firmware data is available so the implementation can install debug binary arrays and set the tool version.
2. Query a feature's size with a `*_size()` function or `qed_dbg_feature_size()`.
3. Allocate/provide a buffer of that size and call the corresponding dump function.
4. Optionally use `qed_dbg_all_data_size()` and `qed_dbg_all_data()` to collect a bundled debug package across engines and NVRAM images.
5. Call `qed_dbg_pf_exit()` during teardown to release any allocated debug buffers.

`qed_get_debug_engine()` and `qed_set_debug_engine()` expose engine selection for multi-hwfn devices; all per-feature collection functions operate against `cdev->engine_for_debug` inside the implementation.

## State And Persistence Behavior

The header itself holds no state. Its APIs operate on state stored in `struct qed_dev` and `struct qed_hwfn`, including selected debug engine, feature buffers, loaded firmware debug arrays, and implementation-specific debug info. `qed_dbg_pf_init()` and `qed_dbg_pf_exit()` are the lifecycle boundaries for that state.

The public contract makes callers responsible for buffer ownership at the API boundary: callers supply the destination buffer, and dump functions report `num_dumped_bytes`. Internal implementation buffers are managed by `qed_debug.c`.

## Dependencies

The declarations assume kernel integer types such as `u32` and `u8` are already available through the including compilation unit's kernel headers. The header intentionally avoids including large implementation-specific headers and only forward-declares QED device types.

Its main integration points are debugfs/diagnostic call sites in the QED driver and the implementation in `qed_debug.c`. The `enum qed_dbg_features` values must remain aligned with `qed_features_lookup[]` in the implementation.

## Risks And Test Signals

- Enum/order drift is the main interface risk. `DBG_FEATURE_*` order is used as an index into implementation lookup tables and `cdev->dbg_features[]`; adding or reordering values requires synchronized implementation changes.
- Size/dump API pairing is part of the contract. Callers should test that every `*_size()` result is sufficient for the matching dump function and that short buffers are rejected by the implementation.
- Lifecycle ordering matters. Calling dump APIs before `qed_dbg_pf_init()` or after `qed_dbg_pf_exit()` risks missing debug arrays or freed buffers in the implementation.
- Multi-engine callers should test `qed_set_debug_engine()` bounds and behavior indirectly through feature collection, since the setter accepts an `int` and does not expose validation in the header.
- Build tests should ensure all prototypes stay consistent with `qed_debug.c`, especially when adding features or changing `enum qed_dbg_features`.
