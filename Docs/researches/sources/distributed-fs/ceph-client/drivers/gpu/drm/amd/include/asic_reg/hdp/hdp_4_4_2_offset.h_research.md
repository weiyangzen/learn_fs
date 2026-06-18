# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_4_2_offset.h

## Purpose

`hdp_4_4_2_offset.h` is the generated register-offset map for HDP IP 4.4.2, address block `aid_hdp_hdpdec`, base address `0x3c80`. It uses the newer `regHDP_*` macro prefix rather than the older `mmHDP_*` prefix. The register map describes the AID-scoped HDP interface used for host-path coherency, non-surface access, surface read/write flags, MEMIO, XDP-to-HDP flush/mailbox operations, P2P BAR programming, GPU IOV violation logging, and MMHUB error status.

## Important APIs, types, and macros

No functions or types are declared. The exported macro families are:

- `regHDP_MMHUB_TLVL`, `regHDP_MMHUB_UNITID`: traffic and unit ID offsets.
- `regHDP_NONSURFACE_BASE`, `regHDP_NONSURFACE_INFO`, `regHDP_NONSURFACE_BASE_HI`: non-surface address configuration.
- `regHDP_SURFACE_WRITE_FLAGS`, `regHDP_SURFACE_READ_FLAGS`, and their `_CLR` registers: surface read/write flag tracking introduced relative to the 4.0 offset header.
- `regHDP_NONSURF_FLAGS`, `regHDP_NONSURF_FLAGS_CLR`, `regHDP_HOST_PATH_CNTL`, `regHDP_SW_SEMAPHORE`, `regHDP_DEBUG0`, `regHDP_LAST_SURFACE_HIT`, `regHDP_OUTSTANDING_REQ`, `regHDP_MISC_CNTL`, and `regHDP_MEM_POWER_CTRL`.
- `regHDP_MMHUB_CNTL`, `regHDP_EDC_CNT`, `regHDP_VERSION`, `regHDP_CLK_CNTL`, `regHDP_MEMIO_*`.
- `regHDP_XDP_*` offsets for direct-to-HDP reserved slots, flush, BAR update, mailbox configuration, P2P BARs, status/sticky registers, BAR high address bits, framebuffer location, `GPU_IOV_VIOLATION_LOG`, `GPU_IOV_VIOLATION_LOG2`, and `MMHUB_ERROR`.

All `_BASE_IDX` values are `0`.

## Control flow

The file has no executable logic. Consumers use the `regHDP_*` names with SOC15 register helpers. In this tree, `hdp_v4_0.c` special-cases HDP 4.4.x behavior while including the 4.0 headers, and no direct C include of this exact 4.4.2 header was found. That makes this file a generated hardware contract available for AID-specific or future platform code rather than an active direct include in the visible AMDGPU C sources.

## State and persistence behavior

The constants refer to persistent MMIO register state. Compared with the 4.0 offset header, this map moves the power register naming to `MEM_POWER_CTRL`, adds surface read/write flag registers, omits `READ_CACHE_INVALIDATE`, and splits GPU IOV initiator ID into `GPU_IOV_VIOLATION_LOG2`. Those deltas affect which hardware state a driver can safely poll or write on HDP 4.4.2 devices.

## Dependencies and integration points

The paired dependency is `hdp_4_4_2_sh_mask.h`. The `regHDP_*` prefix aligns with newer generated register headers and with AMDGPU code paths that use `reg`-prefixed offsets in later HDP generations. The address block name `aid_hdp_hdpdec` signals integration with multi-AID GPU register layouts where each AID may expose an HDP instance or address-space view.

## Risks

A major risk is mixing `mmHDP_*` and `regHDP_*` macro names across generations: the numeric offsets may look similar, but helper call sites and generated mask headers expect matching tokens. Another risk is assuming `READ_CACHE_INVALIDATE` exists because it does in 4.0 and 5.0; 4.4.2 omits it, and `hdp_v4_0_invalidate_hdp()` already skips HDP 4.4.2. Surface flag registers and `GPU_IOV_VIOLATION_LOG2` are version additions, so backporting field logic to 4.0 would reference undefined offsets.

## Test signals

Static validation should confirm that each `regHDP_*` offset has a matching field group in `hdp_4_4_2_sh_mask.h` where appropriate. Build validation should cover any platform code that includes this header. Runtime validation on HDP 4.4.2 hardware should exercise surface flag clear paths, MEM_POWER_CTRL power gating, MMHUB error reporting, and IOV violation logging with initiator ID read from `LOG2`.
