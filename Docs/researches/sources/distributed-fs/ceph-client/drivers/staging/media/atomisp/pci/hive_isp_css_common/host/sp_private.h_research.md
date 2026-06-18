# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/sp_private.h

## Purpose

`sp_private.h` is the private include layer for the `sp` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `sp_public.h`, `device_access.h`, `assert_support.h`. Important macros/constants include `__SP_PRIVATE_H_INCLUDED__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

## State And Persistence Behavior

The persistent state is hardware or firmware-visible state, not normal kernel heap state. Register writes persist in the ISP CSS device until overwritten or reset; shared structs and memory windows persist in SP/ISP DMEM, VMEM/BAMEM, HMEM, DDR, input-buffer SRAM, or GP-device registers depending on the subsystem.

## Dependencies And Integration Points

Dependencies are local to the AtomISP CSS host stack: `type_support.h` scalar types, `system_global.h`/`system_local.h` base addresses and IDs, block-specific public/private headers, `assert_support.h`, `device_access.h` or `ia_css_device_access.h`, and low-level HRT register/memory operations. Integration points are the higher-level CSS pipeline code that configures sensors, DMA, GDC, input formatting, IRQ delivery, SP/ISP execution, and diagnostics through these wrappers.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
