# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.c

## Purpose

`soc21.c` implements the common AMDGPU IP block for SOC21/RDNA3-class devices. It installs ASIC callbacks, register access helpers, codec capability tables, reset policy, doorbell assignments, revision-dependent CG/PG flags, SR-IOV mailbox integration, RAS IRQ handling, and common lifecycle hooks for hardware initialization, suspend, resume, and gating.

## Important APIs, Types, And Functions

The exported object is `soc21_common_ip_block`; `soc21_grbm_select()` updates `GRBM_GFX_CNTL`. `soc21_query_video_codecs()` selects VCN 4.0.x and 5.3.0 codec capabilities, with mutable SR-IOV codec arrays that can be updated from the host. `soc21_didt_rreg()`/`soc21_didt_wreg()` protect indirect DIDT access with `adev->reg.didt.lock`. `soc21_read_register()` exposes a whitelist of GC and SDMA status registers. `soc21_asic_reset_method()` chooses Mode1, Mode2, BACO, or user override by MP1 IP version. `soc21_init_doorbell_index()` assigns KIQ, MEC, user queues, GFX, MES, SDMA, IH, VCN, VPE, and non-CP doorbell ranges.

## Control Flow

`soc21_common_early_init()` sets NBIO remapping, PCIe indirect/port accessors, DIDT accessors, ASIC functions, revision IDs, and GC-version-specific CG/PG flags; it also enables SR-IOV VF settings. Late init obtains VF mailbox IRQs and patches SR-IOV video codecs or enables NBIO ATHUB RAS error IRQs for PF. Hardware init programs ASPM, initializes NBIO registers, optionally remaps HDP, and enables the doorbell aperture. Fini disables apertures and releases mailbox/RAS IRQs. Resume can detect dGPU S3 abort by sampling the MP0 sign-of-life register and reset before reinitialization.

## State And Persistence Behavior

State is split between `adev` callback tables/flags and persistent hardware registers. The file updates doorbell mappings, mailbox IRQ ownership, RAS IRQ references, NBIO/HDP clock gating state, LSDMA memory power gating, and VCN codec capability data. SR-IOV codec arrays are intentionally non-const because host-provided capability updates persist in the guest driver's data.

## Dependencies And Integration Points

SOC21 depends on GC 11 register headers, MP 13 offsets, SOC15 common register macros, NBIO/HDP/LSDMA function tables, PSP/DPM reset services, SMU/VCN data, SR-IOV `mxgpu_nv`, and KFD-facing stable-pstate behavior through RLC safe mode and perfmon MCGC updates.

## Risks And Test Signals

Version tables are the main maintenance risk: wrong GC/MP/UVD matching changes reset behavior, codec exposure, or gating support. SR-IOV paths must coordinate mailbox IRQs and host codec overrides. Doorbell constants are shared with rings and KFD. Tests should cover probe on each GC 11.x/11.5.x variant, VF/PF boot, video capability queries with harvested VCNs and AV1 support changes, GPU reset modes, S3 abort recovery, NBIO/HDP clock gating, LSDMA memory PG, RAS ATHUB interrupt enable/disable, and ring/doorbell tests.
