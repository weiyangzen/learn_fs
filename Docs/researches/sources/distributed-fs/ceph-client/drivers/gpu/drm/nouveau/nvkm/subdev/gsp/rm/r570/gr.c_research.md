# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/gr.c

Purpose: implements R570 GR RM API callbacks for topology queries, context buffer/ZCULL information, and a TU10x-specific graphics scrubber workaround channel.

Important APIs: `r570_gr_tpc_mask()` and `r570_gr_gpc_mask()` query GPC/TPC masks through R570/RM controls. `r570_gr_get_ctxbufs_and_zcull_info()` reads static GR context-buffer info, passes entries to `r535_gr_get_ctxbuf_info()`, extracts ZCULL context size/alignment, then reads `NV2080_CTRL_CMD_GR_GET_ZCULL_INFO` and populates `gr->base.zcull_info`. `r570_gr_scrubber_init()` conditionally creates a scrubber channel on TU10x chipsets `0x162`, `0x164`, and `0x166`: it obtains a CHID, allocates instance memory, creates a VMM, creates an RM VAS with `r535_mmu_vaspace_new()`, allocates a FIFO channel, promotes GR context buffers, allocates a 3D object, and enables RM's bug-4208224 workaround. `r570_gr_scrubber_fini()` tears that state down and sends teardown control if enabled. `r570_gr` exports `.get_ctxbufs_and_zcull_info` and scrubber init/fini callbacks.

Control flow and state: scrubber state persists in `gr->scrubber`: CHID, instance memory, VMM, context buffers/VMAs, channel object, 3D object, and enabled flag. Initialization is all-or-nothing; any failure calls `r570_gr_scrubber_fini()`. Context buffer info persists in `r535_gr`/base GR structures and informs later context promotion.

Dependencies and integration: depends on RM GR helpers, MMU, FIFO/CHID, GR private structures, R570 GR/engine headers, and R535 helpers for VAS creation, context promotion, and context buffer interpretation. It integrates with FIFO channel allocation and RM API callbacks.

Risks: the scrubber path is chipset-gated and allocates several interdependent resources; teardown must tolerate partially initialized state. Context buffer and ZCULL control IDs differ between RM generations, so pairing with R570 headers matters. CHID allocation for the scrubber consumes a FIFO channel ID and must not conflict with user channels.

Test signals: query GPC/TPC masks and compare against static info, initialize GR contexts, verify ZCULL info is populated, boot TU10x devices through scrubber init/fini, run graphics workloads that require context switching, and inspect error logs for bug-4208224 or RC-triggered failures.
