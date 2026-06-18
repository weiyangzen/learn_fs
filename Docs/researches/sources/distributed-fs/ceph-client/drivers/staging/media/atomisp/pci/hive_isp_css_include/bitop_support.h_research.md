# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/bitop_support.h

## Purpose

`bitop_support.h` provides low-level CSS support macros used throughout the AtomISP CSS host code.

## Important APIs, Types, And Data

Important macros/constants include `__BITOP_SUPPORT_H_INCLUDED__`, `bitop_setbit`, `bitop_getbit`, `bitop_clearbit`.

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

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
