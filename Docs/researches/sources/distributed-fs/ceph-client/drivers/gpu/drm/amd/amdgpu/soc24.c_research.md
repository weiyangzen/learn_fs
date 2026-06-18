# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc24.c

## Purpose

`soc24.c` implements AMDGPU's common IP block for SOC24/GC12.0 devices. It is a streamlined successor to `soc21.c`: it supplies VCN 5.0.0 codec capabilities, ASIC callbacks, whitelisted register reads, reset policy, doorbell assignments, GC12 CG/PG flags, SR-IOV mailbox hooks, RAS IRQ enablement, NBIO/HDP/LSDMA gating, and lifecycle methods.

## Important APIs, Types, And Functions

The exported object is `soc24_common_ip_block`; `soc24_grbm_select()` writes `regGRBM_GFX_CNTL`. `soc24_query_video_codecs()` returns VCN 5.0.0 encode/decode caps and rejects fully harvested VCN configurations. `soc24_read_register()` exposes selected GC and SDMA status registers, returning cached `gb_addr_config` when available. `soc24_asic_reset_method()` supports user Mode1/Mode2/BACO overrides and defaults MP1 14.0.2/14.0.3 to Mode1, otherwise BACO if supported. `soc24_init_doorbell_index()` reuses Navi10-style assignments for KIQ, MEC, user queues, GFX, MES, SDMA, IH, VCN, and non-CP ranges.

## Control Flow

`soc24_common_early_init()` installs PCIe indirect and port accessors, ASIC callbacks, revision IDs, GC12-specific CG/PG flags, and SR-IOV VF settings. Late init gets VF mailbox IRQs or enables NBIO ATHUB RAS error events. Hardware init programs ASPM only for non-APU devices, initializes NBIO, remaps HDP, runs DF hardware init when present, and enables the doorbell aperture. Hardware fini disables doorbells and releases mailbox/RAS IRQs. Suspend and resume are direct fini/init wrappers.

## State And Persistence Behavior

The common block writes `adev` function tables, revision IDs, CG/PG flags, doorbell ranges, mailbox IRQ state, and RAS IRQ references. Hardware persistence includes NBIO/HDP/DF initialization, doorbell apertures, clock-gating bits, and LSDMA memory power-gating state. `get_pcie_replay_count()` is a dummy implementation returning zero, so sysfs users should not treat it as real hardware telemetry for this generation.

## Dependencies And Integration Points

The file depends on GC 12.0 and MP 14.0.2 register headers, SOC15 register macros, NBIO v6.3.1-style functions, HDP, DF, LSDMA v7 power-gating callbacks, DPM reset/BACO services, SR-IOV `mxgpu_nv`, RLC safe-mode support, and DRM video capability reporting.

## Risks And Test Signals

Risks include incomplete telemetry (`pcie_replay_count`), assumptions inherited from Navi10 doorbells, GC12 CG/PG tables that differ between 12.0.0 and 12.0.1, and RAS IRQ behavior tied to NBIF v6.3.1 comments. Tests should cover boot on both GC12 variants, codec queries, reset modes, non-APU ASPM programming, DF init ordering, SR-IOV VF mailbox IRQs, RAS event IRQs, clock/power gating, and doorbell/ring operation.
