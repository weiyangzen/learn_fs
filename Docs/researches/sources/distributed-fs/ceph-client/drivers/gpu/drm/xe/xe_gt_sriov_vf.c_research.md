# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf.c

Purpose: implements VF-side GT SR-IOV bootstrap, GuC ABI negotiation, VF config/resource query, PF relay handshake/runtime query, inaccessible register emulation, and post-migration recovery.

Important APIs and functions: exports `xe_gt_sriov_vf_reset`, `bootstrap`, `guc_versions`, `query_config`, `connect`, `query_runtime`, migration event/init/recovery checks, `gmdid`, `guc_ids`, scheduler group status, `read32`/`write32`, debug printers, `wait_valid_ggtt`, and fixup count. Internal helpers send VF2GUC reset/version/KLV/resfix messages and VF2PF relay handshake/runtime requests.

Control flow: bootstrap resets GuC VF state and negotiates a stable GuC interface version. Config query reads GGTT start/size, LMEM size, submission CTX/doorbell quotas, scheduler group availability, and GMDID through GuC KLVs; GGTT base changes shift existing GGTT nodes. PF connection negotiates relay ABI, then runtime query fetches PF-owned register snapshots in chunks. `read32` serves inaccessible registers from cached runtime data or GMDID.

State and persistence: state lives in `gt->sriov.vf`: wanted/found GuC versions, self_config, runtime register cache, scheduler group flag, GMDID, and migration recovery state. Runtime regs are DRM-managed and resized as PF reports different counts. Migration state has a scratch buffer, worker, waitqueue, spinlock, queued/inprogress/teardown flags, `ggtt_need_fixes`, marker, debug stoppers, and atomic fixup count.

Migration recovery: on migrated event, the VF marks recovery pending, wakes CT waiters, queues ordered work, flushes/stops CT, pauses GuC submit, resets TLB invalidation, sends RESFIX_START, requeries config, rebases CCS/default LRC HWSP/GuC contexts, marks GGTT fixups done, resumes IRQ/CT/submission, sends RESFIX_DONE, then kickstarts jobs. Failures abort submission pause and wedge the device; shared-GT ordering can requeue media recovery behind primary GT recovery.

Dependencies and integration: depends on GuC MMIO communication, GuC relay, KLV ABI, GGTT/tile VF storage, LMEM, IRQ, memirq, GuC CT/submit, LRC, CCS rebase, TLB invalidation, WOPCM, runtime PF service, and debugfs.

Risks: version changes after prior handshake return `-EREMCHG`. Resource reassignment checks reject changed GGTT/LMEM/CTX/doorbell sizes except GGTT base shifting. Migration recovery assumes memirq for immediate pending detection and can wedge on failed fixups. Runtime register cache must be sorted as supplied by PF for `bsearch`. `xe_gt_sriov_vf_lmem` is declared in the header but not implemented in this file, so consumers rely on another definition or risk link failure.

Test signals: VF bootstrap across platform version baselines, GuC KLV query failures, GGTT base migration, PF ABI/runtime chunk query, inaccessible register read/write debug warnings, migration recovery success/failure/requeue with debug `resfix_stoppers`, and waiters using `xe_gt_sriov_vf_wait_valid_ggtt`.
