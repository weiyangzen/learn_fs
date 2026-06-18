# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/rm.c

Purpose: assembles the R535 RM implementation descriptor and API table for Turing/Ampere-style GSP-RM operation.

Important definitions: `r535_wpr_libos2` and `r535_wpr_libos3` define WPR heap sizing policy from `GSP_FW_HEAP_*` constants. `r535_api` wires together the R535 module implementations: GSP, RPC, control, allocation, client, device, FBSR, display, FIFO, CE, GR, NVDEC, NVENC, NVJPG, and OFA. `r535_rm_tu102` uses the libos2 WPR sizing; `r535_rm_ga102` uses the libos3 sizing.

Control flow and state: no runtime flow is implemented here. The table determines which callbacks downstream Nouveau code invokes for the selected GPU/RM firmware generation. WPR sizing feeds firmware carveout allocation and boot metadata construction.

Dependencies and integration: includes `rm/rm.h` for API/implementation structures and `nvrm/gsp.h` for heap constants. It is a central integration point across all R535 implementation files.

Risks and tests: an incorrect API pointer mixes incompatible payload versions and can break boot, display, FIFO, or resume. Wrong WPR sizing can prevent firmware heap setup or under-allocate resume state. Test signals are successful RM implementation selection for TU102/GA102-family devices and coverage of each callback family.
