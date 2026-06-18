# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_trace.h

## Purpose

`css_trace.h` defines the shared SP/ISP trace buffer ABI: trace item/header layouts, trace-buffer partitioning, trace command encodings, circular index helpers, and bit-packing macros for regular, quick, formatted, and 24-bit trace points.

## Important APIs, Types, And Data

Key includes: `type_support.h`, `sh_css_internal.h`. Important macros/constants include `__CSS_TRACE_H_`, `MAX_SCRATCH_DATA`, `MAX_CMD_DATA`, `HDR_HDR_OFFSET`, `HDR_COMMAND_OFFSET`, `HDR_DATA_OFFSET`, `HDR_DEBUG_SIGNATURE_OFFSET`, `HDR_DEBUG_POINTER_OFFSET`, `HDR_STATUS_OFFSET`, `HDR_STATUS_OFFSET_BYTE`. Important types include `DBG_commands`.

## Control Flow

The file is macro-only support code. Control flow appears at expansion sites in callers, so tests need to exercise both valid and invalid macro inputs in the surrounding CSS host code.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Dependencies are local to the AtomISP CSS host stack: `type_support.h` scalar types, `system_global.h`/`system_local.h` base addresses and IDs, block-specific public/private headers, `assert_support.h`, `device_access.h` or `ia_css_device_access.h`, and low-level HRT register/memory operations. Integration points are the higher-level CSS pipeline code that configures sensors, DMA, GDC, input formatting, IRQ delivery, SP/ISP execution, and diagnostics through these wrappers.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.
- `FIELD_FORMAT_MASK` is derived from `FIELD_MAJOR_W_FMT_WIDTH` rather than `FIELD_FORMAT_WIDTH`; because both are small constants this deserves review before changing trace format width.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
