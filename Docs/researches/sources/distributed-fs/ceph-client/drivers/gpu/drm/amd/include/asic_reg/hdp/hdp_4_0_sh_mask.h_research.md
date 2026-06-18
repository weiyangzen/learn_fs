# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_0_sh_mask.h

## Purpose

`hdp_4_0_sh_mask.h` is the field-description companion for the HDP 4.0 offset header. It defines `__SHIFT` and `_MASK` macros for fields inside the HDP 4.0 registers, allowing AMDGPU helpers such as `REG_SET_FIELD()` and `WREG32_FIELD15()` to update individual hardware fields without hard-coded bit arithmetic at call sites.

## Important APIs, types, and macros

This file defines only macros. Important field groups include:

- MMHUB routing fields: `HDP_MMHUB_TLVL__*` and `HDP_MMHUB_UNITID__*` describe HDP, XDP, and XDP mailbox traffic levels/unit IDs.
- Non-surface aperture fields: `HDP_NONSURFACE_BASE__NONSURF_BASE_39_8`, `HDP_NONSURFACE_BASE_HI__NONSURF_BASE_47_40`, `HDP_NONSURFACE_INFO__NONSURF_SWAP`, and `HDP_NONSURFACE_INFO__NONSURF_VMID`.
- Host path fields: `HDP_HOST_PATH_CNTL__WR_STALL_TIMER`, `RD_STALL_TIMER`, write-combine controls, `ALL_SURFACES_DIS`, `WRITE_THROUGH_CACHE_DIS`, and `LIN_RD_CACHE_DIS`.
- Cache and request fields: `HDP_READ_CACHE_INVALIDATE__READ_CACHE_INVALIDATE`, `HDP_OUTSTANDING_REQ__WRITE_REQ/READ_REQ`, and `HDP_MISC_CNTL__FLUSH_INVALIDATE_CACHE`, `READ_BUFFER_WATERMARK`, cacheline-size, pending-write-tag, and burst fields.
- Power/clock fields: `HDP_MEM_POWER_LS__LS_ENABLE/LS_HOLD` and `HDP_CLK_CNTL__*SOFT_OVERRIDE`.
- MEMIO fields: `HDP_MEMIO_CNTL__MEMIO_SEND`, operation, byte enables, strobes, address upper bits, error-clear bits, VF/VFID, plus status/data fields.
- XDP direct-to-HDP and P2P fields: flush number, mailbox encoded data and address select, BAR update address/flush/BAR number, P2P mailbox addresses, P2P BAR address/flush/valid, and BAR high address bits.
- Diagnostic/security fields: `HDP_XDP_BUSY_STS__BUSY_BITS`, `HDP_XDP_STICKY__STICKY_STS/W1C`, `HDP_XDP_GPU_IOV_VIOLATION_LOG__*`, and `HDP_XDP_MMHUB_ERROR__*`.

## Control flow

There is no runtime control flow. The macros are consumed by preprocessor-expansion in AMDGPU register helpers. For example, `WREG32_FIELD15(HDP, 0, HDP_MISC_CNTL, FLUSH_INVALIDATE_CACHE, 1)` relies on `HDP_MISC_CNTL__FLUSH_INVALIDATE_CACHE__SHIFT` and `HDP_MISC_CNTL__FLUSH_INVALIDATE_CACHE_MASK`. `REG_SET_FIELD()` similarly uses the field macros to construct read-modify-write values.

## State and persistence behavior

The file has no state, but it describes stateful hardware fields. Several fields are sticky or write-one-to-clear by convention (`HDP_XDP_STICKY__STICKY_W1C`, `*_FLAGS_CLR`). Others gate power or clocks, trigger cache invalidation, hold RAS/error counters, or encode SR-IOV violation details. Field values persist in the GPU register file according to hardware reset and power-domain behavior; the header must therefore match silicon bit layout exactly.

## Dependencies and integration points

This header is directly paired with `hdp_4_0_offset.h` and is included by `hdp_v4_0.c`. It depends on AMDGPU naming conventions: register field macros must be named `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` so helper macros can derive them from register and field tokens. The constants integrate with `amdgpu_ip_version()` branches in `hdp_v4_0.c`, which select behavior for HDP 4.0/4.1, 4.2.1, and 4.4.x devices.

## Risks

Because these are untyped bit constants, mask/shift drift can compile cleanly while corrupting hardware behavior. Notable version-sensitive fields include `HDP_MMHUB_TLVL`, where the 4.0 masks are 3-bit wide while 4.4.2 widens them to 4 bits, and `HDP_MEM_POWER_LS`, which is superseded by `HDP_MEM_POWER_CTRL` in later naming. Cache-control fields such as `FLUSH_INVALIDATE_CACHE` and read/write cache disable bits can cause coherency bugs if wrong. Security/virtualization fields in GPU IOV logging and MMHUB error registers can hide or misattribute faults if masks are wrong.

## Test signals

Compilation of field-based register writes in `hdp_v4_0.c` is the first signal. Runtime signals include successful HDP invalidate operations, stable display/compute memory coherency, correct clock-gating state reporting for HDP light sleep, expected RAS EDC counter behavior, and absence of MMHUB/XDP error logs during normal DMA and P2P workloads. A useful static check is comparing every `HDP_*__FIELD` macro here against the official generated register database for HDP 4.0 silicon.
