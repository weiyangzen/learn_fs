# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_catalog.h

## Purpose
Defines the typed data model for DPU hardware catalogs. Hardware discovery and resource allocation use these structures to describe capabilities, block offsets, feature bits, interrupts, format tables, QoS/performance limits, and SoC configuration instances.

## Important APIs, Types, and Functions
Important constants include `MAX_BLOCKS`, `DPU_MAX_IMG_WIDTH`, `DPU_MAX_IMG_HEIGHT`, `CRTC_DUAL_MIXERS`, and `MAX_XIN_COUNT`. Feature enums describe SSPP, mixer, DSPP, CTL, WB, VBIF, and DSC capabilities. Key structs are `dpu_caps`, `dpu_sspp_sub_blks`, `dpu_lm_sub_blks`, `dpu_dspp_sub_blks`, `dpu_pingpong_sub_blks`, `dpu_dsc_sub_blks`, `dpu_mdp_cfg`, `dpu_ctl_cfg`, `dpu_sspp_cfg`, `dpu_lm_cfg`, `dpu_pingpong_cfg`, `dpu_dsc_cfg`, `dpu_intf_cfg`, `dpu_wb_cfg`, `dpu_cwb_cfg`, `dpu_vbif_cfg`, `dpu_cdm_cfg`, `dpu_perf_cfg`, and the root `dpu_mdss_cfg`. The header also declares extern catalog instances for supported SoCs.

## Control Flow and State
No runtime state is held here; all structures are immutable descriptions. Runtime initializers copy pointers from `dpu_mdss_cfg` into hardware wrapper objects, and ops availability is frequently gated by `mdss_ver->core_major_ver` or feature bits.

## Dependencies and Integration Points
The header is a dependency for nearly every DPU block: CTL, INTF, CDM, CWB, DSC, DSPP, interrupts, VBIF/perf, resource manager, encoder setup, and format validation. Interrupt indexes stored in catalog entries are later passed into the core IRQ layer.

## Risks and Test Signals
The contract risk is semantic drift: a feature bit can mean a required register path, a max dimension constrains framebuffer validation, and incorrect block lengths/bases lead to invalid MMIO. Tests should include catalog compile coverage, probe-time sanity checks, resource manager topology validation, format-list validation, IRQ index mapping, version-gated ops coverage, and per-SoC display/writeback smoke tests.
