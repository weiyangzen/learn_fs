# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_hw_error_regs.h

## Purpose

`xe_hw_error_regs.h` defines MMIO addresses and bit fields for Xe hardware error reporting, including GT correctable/nonfatal/fatal status, device-level error status, PVC GT error vectors, and PVC SoC global/local error registers.

## Important APIs, Types, and Definitions

- HEC firmware error registers: `HEC_UNCORR_ERR_STATUS(base)`, `UNCORR_FW_REPORTED_ERR`, and `HEC_UNCORR_FW_ERR_DW0(base)`.
- GT error status: `ERR_STAT_GT_COR`, `ERR_STAT_GT_NONFATAL`, `ERR_STAT_GT_FATAL`, `ERR_STAT_GT_REG(x)`, and bit masks for EU, SLM, GuC, and FPU errors.
- Device status: `DEV_ERR_STAT_REG(x)` and bit positions `XE_CSC_ERROR`, `XE_SOC_ERROR`, `XE_GT_ERROR`.
- Vector registers: `ERR_STAT_GT_FATAL_VECTOR_REG(x)`, `ERR_STAT_GT_COR_VECTOR_REG(x)`, and `ERR_STAT_GT_VECTOR_REG(hw_err, x)`.
- SoC error helpers: PVC master/slave bases, global event control, global status, local correctable/uncorrectable status, and IEH bits.

## Control Flow

There is no local execution. Consumers select a register with `_PICK_EVEN()`-based helpers for correctable versus nonfatal/fatal lanes, then read, decode, clear, or log error state according to the hardware error class being handled.

## State and Persistence Behavior

The represented state is hardware-latched error status. Bits may persist until explicitly cleared or until reset, depending on the underlying register semantics. Vector registers expose per-unit causes that downstream error code can map to GT or SoC subcomponents.

## Dependencies and Integration Points

The file expects `XE_REG`, `_PICK_EVEN`, and `REG_BIT`/`REG_GENMASK` helpers from adjacent Xe register infrastructure and DRM Intel bit helpers. It integrates with hardware error detection, error interrupt handlers, PVC-specific RAS handling, and diagnostics that classify correctable versus fatal events.

## Risks and Edge Cases

- `ERR_STAT_GT_VECTOR_REG()` depends on the `HARDWARE_ERROR_CORRECTABLE` enum value being visible and stable at use sites.
- `_PICK_EVEN()` helpers assume `x` is a 0/1-like selector; unexpected values can select unintended offsets.
- Error-status registers are high-impact diagnostics; incorrect masks can hide fatal hardware events or report false positives.

## Test Signals

Build tests should cover all hardware-error users. Unit tests can validate selector macros produce the expected addresses. Integration signals are correct interrupt classification, accurate logs for injected or firmware-reported errors, and no regressions on PVC RAS flows.
