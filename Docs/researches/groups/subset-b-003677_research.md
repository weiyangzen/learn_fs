# subset-b-003677 Research

Grouped research report for the requested Nouveau FIFO and GR source files. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gf100.c

Purpose: implements the Fermi GF100 FIFO backend and provides the baseline used by many newer FIFO variants. It defines channel binding, RAMFC and USERD setup, engine context binding, PBDMA/runlist helpers, non-stall event gating, interrupt dispatch, MMU fault decoding/recovery, and the `gf100_fifo_new()` constructor.

Important APIs and data: `gf100_chan_preempt()`, `gf100_chan_userd_clear()`, `gf100_fifo_chid_ctor()`, `gf100_fifo_runq_nr()`, `gf100_fifo_intr_pbdma()`, `gf100_fifo_intr_mmu_fault()`, `gf100_fifo_intr_ctxsw_timeout()`, `gf100_fifo_mmu_fault_recover()`, `gf100_runq_init()`, `gf100_runq_intr()`, `gf100_runl_preempt_pending()`, `gf100_engn_mmu_fault_trigger*()`, and the function tables `gf100_chan`, `gf100_runq`, `gf100_runl`, `gf100_engn`, `gf100_fifo_mmu_fault`, and `gf100_fifo`.

Control flow: channel creation through the generic FIFO core calls the function table, writes RAMFC fields into the channel instance object, binds instance pointers into PFIFO channel tables, starts/stops channel enable bits, and updates runlists through NV50-style RAMRL helpers. Interrupt flow reads PFIFO status at `0x002100 & 0x002140`, dispatches scheduler, MMU fault, PBDMA, runlist, and engine interrupts, acknowledges handled bits, and masks unknown bits to avoid interrupt storms. Context-switch timeout recovery scans engines reporting busy channel state, triggers synthetic MMU faults for matching engines, and lets normal fault recovery schedule runlist recovery.

State and persistence: state lives in GPU registers, channel instance memory, USERD memory, runlist membership, atomic recovery counters, and `nvkm_chid` allocations. There is no durable persistence; all state is hardware/runtime state rebuilt at driver init and channel creation.

Dependencies and integration: depends on FIFO private types, channel groups, runlists, runqueues, BAR reset helpers, MMU fault delivery, MC, software engine method handling, and NVIF Fermi channel class registration. It integrates with `nvkm_fifo_new_()`, `nvkm_fifo_fault()`, `nvkm_runl_rc_cgrp()`, `nvkm_chan_error()`, and the non-stall event framework.

Risks: heavy use of magic register offsets and bitfields; fault recovery can reset engines and kill channel groups; `WARN_ON` paths indicate unknown engine mappings; interrupt handlers mask unrecognized status, which prevents storms but may hide unsupported hardware conditions; PBDMA exception clearing is marked TODO.

Test signals: useful signals are successful module build, channel creation for `FERMI_CHANNEL_GPFIFO`, PBDMA error logging with channel names, MMU fault reports with decoded engine/client/reason/access, non-stall event delivery, runlist update completion, and recovery from forced context-switch timeout without hanging PFIFO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk104.c

Purpose: implements Kepler GK104 FIFO support and is the main Kepler baseline for later GK/GM/GP variants. It changes channel table registers, supports topology-discovered runlists/engines, adds Kepler PBDMA HCE interrupt handling, expands MMU fault decode tables, and exports many helpers reused by later chips.

Important APIs and data: exported helpers include `gk104_chan_bind()`, `gk104_chan_bind_inst()`, `gk104_chan_start()`, `gk104_chan_stop()`, `gk104_runl_commit()`, `gk104_runl_insert_chan()`, `gk104_runl_pending()`, `gk104_runq_init()`, `gk104_runq_intr()`, `gk104_runq_idle()`, `gk104_engn_cxid()`, `gk104_engn_chsw()`, `gk104_ectx_ctor()`, `gk104_fifo_intr()`, `gk104_fifo_runl_ctor()`, and `gk104_fifo_new()`. Key tables are `gk104_chan`, `gk104_engn`, `gk104_engn_ce`, `gk104_runq`, `gk104_runl`, and `gk104_fifo_mmu_fault`.

Control flow: channel RAMFC programming resembles GF100 but stores privilege and CHID fields. Engine context binding selects per-engine instance-pointer slots, including SEC, VIC, MSENC, NVDEC, and NVENC aliases. `gk104_fifo_runl_ctor()` walks `device->top->device`, creates runlists by hardware runlist id, associates runqueues based on PBDMA runlist masks, and adds each engine with GR inserting the software engine too. Interrupt handling decodes bind, PIO, scheduler, channel-switch, dropped MMU fault, MMU fault, PBDMA, runlist, and non-stall events.

State and persistence: runlist and channel state remain runtime only. Hardware topology controls which engines and runlists exist. Channel identifiers expand to 4096, and channel groups are optionally supported by later consumers.

Dependencies and integration: depends on `subdev/top` discovery, GF100 interrupt/recovery helpers, NV50 runlist update/wait, software-engine method dispatch, and NVIF Kepler channel class `KEPLER_CHANNEL_GPFIFO_A`.

Risks: topology-driven construction can fail if runqueue mapping exceeds the fixed two-entry `runl->runq[]`; HCE `CTXNOTVALID` defaults to logging unless a later runqueue function supplies a recovery callback; many fault client names are decode-only and do not imply recovery; engine status selection around simultaneous load/save relies on `nvkm_engine_chsw_load()`.

Test signals: look for correct runlist count from TOP, PBDMA interrupt decode for both INTR0 and HCE INTR1, successful channel bind/start at `0x800000/0x800004`, runqueue idle reporting during recovery, and Kepler channel class exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk110.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk110.c

Purpose: adds GK110 channel-group support on top of GK104 FIFO. It introduces hardware channel groups, group preemption, CGID allocation, and runlist entries that describe a group plus its member channels.

Important APIs and data: `gk110_chan_preempt()` chooses channel-group preemption when the channel belongs to a hardware group; `gk110_cgrp_preempt()` writes `0x01000000 | cgrp->id` to the preempt register; `gk110_runl_insert_cgrp()` emits the group runlist descriptor; `gk110_fifo_chid_ctor()` allocates both `fifo->cgid` and `fifo->chid`; `gk110_fifo_new()` registers the `KEPLER_CHANNEL_GROUP_A` and `KEPLER_CHANNEL_GPFIFO_B` classes.

Control flow: regular channel operations reuse GK104 bind/start/stop/RAMFC. When preempting a channel, the code checks `cgrp->hw`; hardware groups use the group preempt function, while non-grouped channels fall back to GF100 CHID preemption. Runlist generation calls `insert_cgrp` before member channels when `cgrp->hw` is set.

State and persistence: persistent runtime state is the CGID allocator and the `cgrp->hw`, `cgrp->id`, and `cgrp->chan_nr` values that feed runlist descriptors. There is no storage across driver lifetime.

Dependencies and integration: relies on GK104 runlist construction, runqueue handling, and interrupt handling, plus `nvkm_cgrp` membership and `nvkm_chid_new()` events. The exported `gk110_runl`, `gk110_cgrp`, and `gk110_chan` tables are reused by GK208, GK20A, and Maxwell/Pascal derivatives.

Risks: group descriptor bit packing is hardware-specific; missing or misallocated CGIDs break group preemption and recovery; fallback preemption behavior must remain correct for non-hardware groups.

Test signals: create channel groups through the NVIF class, verify returned CGIDs, create member channels, trigger channel-group preemption, and confirm runlist update contains one group descriptor plus channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk208.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk208.c

Purpose: provides GK208 FIFO specialization. It mostly reuses GK110/GK104 behavior but changes PBDMA initialization and reduces channel count.

Important APIs and data: `gk208_runq_init()` calls `gk104_runq_init()` and then writes `0x000f4240` to `0x04012c + pbid * 0x2000`; `gk208_runq` inherits GK104 interrupt handling and idle checks; `gk208_fifo_chid_nr()` returns 1024; `gk208_fifo_new()` registers `KEPLER_CHANNEL_GROUP_A` and `KEPLER_CHANNEL_GPFIFO_A`.

Control flow: construction uses GK110 CGID/CHID allocation, GK104 TOP-driven runlist construction, GK104 init/interrupt paths, and GK110 runlist group descriptors. Runtime deltas are limited to runqueue init and channel-count limits.

State and persistence: channel and group state follow GK110. The extra runqueue register appears to configure a timeout or scheduling parameter per PBDMA and is rewritten at init.

Dependencies and integration: depends on helpers exported by GF100, GK104, and GK110. It is a compact function-table variant consumed by device probing for GK208-class GPUs.

Risks: because most logic is inherited, regressions may come from mismatched class selection or channel count assumptions; the magic `0x04012c` value lacks local explanation.

Test signals: build coverage, creation of up to 1024 channels, successful GK208 PBDMA init register write, GK104 PBDMA interrupt decode, and group preemption behavior inherited from GK110.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk208.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk20a.c

Purpose: defines the GK20A FIFO function table, largely reusing GK208/GK110/GK104 code for the Tegra Kepler variant.

Important APIs and data: `gk20a_fifo` selects `nv50_fifo_chid_nr`, GK110 CHID/CGID construction, GF100 runqueue counting, GK104 runlist construction/init/interrupt handling, GK110 runlist/group/channel functions, GK208 runqueue behavior, and `KEPLER_CHANNEL_GPFIFO_A`. `gk20a_fifo_new()` passes this table to `nvkm_fifo_new_()`.

Control flow: no local runtime logic exists beyond function-table selection. All channel lifecycle, runlist updates, interrupts, and recovery are delegated to inherited helpers.

State and persistence: all state is inherited runtime FIFO state. The table does not enable a user-visible channel-group class, but uses `gk110_cgrp` internally.

Dependencies and integration: depends on the Kepler helper stack and NVIF Kepler channel class. It integrates through the common FIFO constructor.

Risks: being purely declarative makes correctness dependent on selecting helpers that match GK20A hardware; using `nv50_fifo_chid_nr` limits channels to 128, which must match the target integration; absent local comments make hardware rationale external.

Test signals: probe GK20A, create GPFIFO channels, verify inherited interrupts do not report unsupported bits, and confirm runlist/channel allocation limits match hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gm107.c

Purpose: implements Maxwell GM107 FIFO deltas over Kepler: channel binding uses only instance binding, runlist entries include channel instance addresses, MMU fault client decoding changes, and MMU fault unit parsing supports wider client fields.

Important APIs and data: `gm107_chan`, `gm107_runl_insert_chan()`, `gm107_runl`, `gm107_fifo_mmu_fault`, `gm107_fifo_intr_mmu_fault_unit()`, `gm107_fifo_chid_nr()`, and `gm107_fifo_new()`. Exported `gm107_runl`, `gm107_chan`, and `gm107_fifo_mmu_fault` are reused by GM200.

Control flow: channel operations reuse GK104 start/stop/unbind and GK110 preemption, but `bind` is `gk104_chan_bind_inst()` instead of runlist-tagging bind. Runlist insertion writes CHID plus instance pointer. Interrupt handling remains GK104, but MMU fault unit extraction uses a 6-bit client field and GM107-specific engine table.

State and persistence: runtime state includes 2048 channel IDs, CGID state from GK110 construction, channel instance addresses in RAMRL, and decoded MMU fault records.

Dependencies and integration: depends on GF100 fault recovery, GK104 interrupts and runlist commit, GK110 groups, GK208 PBDMA init, and NVIF `KEPLER_CHANNEL_GPFIFO_B`.

Risks: runlist descriptor format differs from Kepler; wrong descriptor layout can make channels unrunnable. Fault engine table omits graphics/copy engine mappings and relies on TOP lookup where available.

Test signals: GM107 channel creation, runlist dump/trace showing instance-address entries, MMU fault logging with client values above 31, and recovery of faulted channel groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gm200.c

Purpose: provides GM200 FIFO specialization, primarily reading runqueue and channel counts from hardware registers and selecting the Maxwell channel class.

Important APIs and data: `gm200_fifo_runq_nr()` reads `0x002004 & 0xff`, `gm200_fifo_chid_nr()` reads `0x002008`, and `gm200_fifo_new()` registers `MAXWELL_CHANNEL_GPFIFO_A`. The `gm200_fifo` table reuses GM107 runlist/channel/MMU-fault behavior and GK104 interrupt/init behavior.

Control flow: constructor delegates to `nvkm_fifo_new_()`. At FIFO setup, common code asks the table for channel and runqueue counts, allowing hardware-reported sizing instead of fixed constants.

State and persistence: no local state beyond hardware-reported counts. Runtime channel/group/runlist state follows GM107/GK110 behavior.

Dependencies and integration: depends on GM107, GK208, GK104, GK110, and GF100 helpers. Integrates with device-specific probing for second-generation Maxwell.

Risks: invalid or unexpected register values at `0x002004/0x002008` directly affect allocation sizes; class selection must match userspace expectations for Maxwell channels.

Test signals: boot/probe logs with sane runqueue/channel counts, successful channel allocation across reported range, PBDMA interrupts through inherited GK208/GK104 handlers, and `MAXWELL_CHANNEL_GPFIFO_A` exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gp100.c

Purpose: implements Pascal GP100 FIFO differences. It adds two-runqueue runlist descriptors, Pascal MMU fault decode layout, and forced channel-group support for the Pascal GPFIFO class.

Important APIs and data: `gp100_runl_insert_chan()` encodes `chan->id | chan->runq << 14` plus instance pointer; `gp100_runl` sets `.runqs = 2`; `gp100_fifo_intr_mmu_fault_unit()` decodes hub/access/client/reason with Pascal bit positions; `gp100_fifo_mmu_fault` and `gp100_fifo_new()` define decode tables and construction.

Control flow: inherited GK104 runlist construction associates runqueues; NV50 runlist update uses the GP100 insertion function. Fault handling uses GK104 interrupt dispatch and GF100 recovery, but the fault parser emits Pascal-style `nvkm_fault_data` before calling `nvkm_fifo_fault()`.

State and persistence: runtime state includes per-channel `runq`, forced hardware channel groups, channel instance pointers in RAMRL, and MMU fault data with wider access/reason fields.

Dependencies and integration: depends on GM200 dynamic counts, GK110 CGID constructor/group preemption, GK104 init/commit/interrupt, GK208 runqueue init, and `PASCAL_CHANNEL_GPFIFO_A`.

Risks: runqueue bit placement in runlist entries is hardware-specific; wrong `chan->runq` assignment can route channels to the wrong PBDMA/LCE. Fault parsing differs from GM107 and may misdecode if applied to the wrong chip.

Test signals: Pascal channel/group creation, two-runqueue operation, copy-engine channel visibility tied to runqueue selection, decoded MMU faults with Pascal access values, and recovery from faulted channel groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gv100.c

Purpose: implements Volta GV100 FIFO behavior: new RAMFC layout, doorbell token support, CE context binding through BAR2, runlist entries with USERD and instance pointers, Volta MMU fault decode tables, and simplified context-switch timeout recovery.

Important APIs and data: `gv100_chan_doorbell_handle()`, `gv100_chan_ramfc`, `gv100_chan_userd`, `gv100_ectx_bind()`, `gv100_ectx_ce_ctor()`, `gv100_ectx_ce_bind()`, `gv100_runq`, `gv100_runl_preempt()`, `gv100_runl_insert_chan()`, `gv100_runl_insert_cgrp()`, `gv100_fifo_mmu_fault_*` tables, `gv100_fifo_intr_ctxsw_timeout()`, and `gv100_fifo_new()`.

Control flow: channel creation writes Volta RAMFC fields and returns CHID as doorbell handle. GR engine context binding writes context VMA to channel instance offsets `0x210/0x214`; CE binding writes BAR2 addresses to `0x220/0x224`. Runlist update emits 16-byte entries: channel entries carry USERD address, runqueue bit, instance address, and CHID; group entries carry group metadata. Runqueue HCE `CTXNOTVALID` logs, marks the channel errored, updates PBDMA state, and acknowledges the HCE bit.

State and persistence: runtime state includes 16-byte RAMRL entries, USERD memory addresses, BAR2-backed CE context references, forced channel groups, and Volta fault tables. CE constructor fails if BAR2 mapping is unavailable.

Dependencies and integration: builds on GK104 interrupts/init, GK208 runqueue init, GK110 groups, GM200 dynamic sizing, GF100 recovery, and NVIF `VOLTA_CHANNEL_GPFIFO_A`.

Risks: CE context binding depends on valid BAR2; doorbell handle semantics differ from TU102; `gv100_fifo_intr_ctxsw_timeout()` directly schedules runlist engine recovery rather than synthetic MMU faults; fault decode tables are large and chip-specific.

Test signals: channel creation returning doorbell token, runlist entries containing USERD and instance addresses, `CTXNOTVALID` channel kill handling, CE object init with BAR2 present, Volta MMU fault decode, and runlist preemption via `0x002638`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv04.c

Purpose: implements the earliest NV04 PFIFO backend. It uses legacy RAMHT/RAMRO/RAMFC instance-memory tables, direct cache puller/pusher registers, DMA channel RAMFC layouts, RAMHT object insertion, pause/start helpers, cache-error/DMA-pusher/semaphore interrupt handling, and the `NV03_CHANNEL_DMA` class.

Important APIs and data: `nv04_chan_start()`, `nv04_chan_stop()`, `nv04_chan_ramfc_clear()`, `nv04_eobj_ramht_del()`, `nv04_fifo_pause()`, `nv04_fifo_start()`, `nv04_fifo_intr()`, `nv04_fifo_init()`, `nv04_fifo_runl_ctor()`, `nv04_fifo_chid_ctor()`, `nv04_fifo_new()`, plus `nv04_chan_ramfc`, `nv04_chan_userd`, `nv04_chan_inst`, `nv04_engn`, `nv04_runl`, and `nv04_fifo`.

Control flow: channel RAMFC setup writes DMA put/get and push instance state into global RAMFC. Stopping a channel disables cache switching, saves live PFIFO cache registers back into RAMFC if the channel is active, clears hardware cache registers, installs an invalid channel marker, disables DMA mode for the channel, and restarts caches. Interrupt handling disables caches, handles cache errors by optionally dispatching software methods, advances GET past bad methods, handles DMA pusher errors by moving GET to PUT, processes semaphore interrupts, masks unknown bits, and restores previous cache assignment.

State and persistence: state is runtime-only but stored across channel switches in instance-memory RAMFC and RAMHT objects. The last CHID is reserved as an invalid marker.

Dependencies and integration: depends on `regsnv04.h`, instmem RAMHT/RAMRO/RAMFC, timer polling, software engine method dispatch, and generic FIFO/runlist/channel-group core.

Risks: direct register save/restore is fragile; cache puller hash busy/failed handling is timing-sensitive; interrupt recovery advances GET and may drop bad commands; hardware-era differences are encoded through RAMFC layouts and masks.

Test signals: NV04/NV03 class channel creation, RAMHT insertion/removal, cache-error logs with method/data decode, DMA-pusher recovery, semaphore advancement, and no PFIFO hang after channel stop/start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv10.c

Purpose: provides NV10 FIFO specialization by extending the NV04 RAMFC layout and channel count for `NV10_CHANNEL_DMA`.

Important APIs and data: `nv10_chan_ramfc_write()` writes the NV10 RAMFC offsets, `nv10_chan_ramfc` includes reference-count state in the context layout, `nv10_chan` reuses NV04 USERD/instance/start/stop helpers, `nv10_fifo_chid_nr()` returns 32, and `nv10_fifo_new()` constructs the FIFO.

Control flow: runtime behavior is inherited from NV04. Channel creation writes DMA PUT/GET, DMA instance at offset `0x0c`, and fetch configuration at `0x14`; suspend/resume of live PFIFO state uses the declared RAMFC layout. Interrupt/init/pause/start/runlist behavior comes from NV04.

State and persistence: RAMFC entry size remains 32 bytes but includes `NV10_PFIFO_CACHE1_REF_CNT`. CHID allocation reserves the invalid marker through `nv04_fifo_chid_ctor()`.

Dependencies and integration: depends on NV04 register definitions, instmem RAMFC/RAMHT, and the generic FIFO constructor. It integrates as the NV10-era DMA channel class.

Risks: wrong RAMFC offsets corrupt cache state save/restore; using NV04 interrupt handling assumes compatible PFIFO status bits; big-endian fetch configuration remains compile-time conditional.

Test signals: creation of 32-channel-capable NV10 FIFO, correct RAMFC offsets in instance memory, cache-error/DMA-pusher handling through inherited NV04 path, and `NV10_CHANNEL_DMA` class exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv17.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv17.c

Purpose: provides NV17 FIFO support, extending NV10 RAMFC with acquire, semaphore, and subroutine state and a modified RAMFC base register encoding.

Important APIs and data: `nv17_chan_ramfc_write()`, `nv17_chan_ramfc`, `nv17_chan`, `nv17_fifo_init()`, `nv17_fifo`, and `nv17_fifo_new()`. The class is `NV17_CHANNEL_DMA`.

Control flow: channel creation writes a 64-byte RAMFC entry, with base `chan->id * 64`. The layout adds acquire value/timestamp/timeout, semaphore, and DMA subroutine fields. FIFO initialization follows NV04 but writes `NV03_PFIFO_RAMFC` with `nvkm_memory_addr(ramfc) >> 8 | 0x00010000`, selecting the NV17 RAMFC format.

State and persistence: runtime PFIFO state is saved in larger RAMFC records. Semaphore/acquire state can survive context switches through the declared layout.

Dependencies and integration: depends on NV04 interrupt, pause/start, runlist, RAMHT, and CHID helpers plus NV04 register definitions.

Risks: context record size and RAMFC format bit must match hardware; inherited interrupt handling must handle semaphore state correctly; a wrong layout causes stale acquire/semaphore state after switches.

Test signals: NV17 channel creation, semaphore interrupt recovery, RAMFC format register value, successful context switches with acquire/semaphore commands, and build coverage for `NV17_CHANNEL_DMA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv17.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv40.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv40.c

Purpose: implements NV40 FIFO support. It expands the RAMFC to 128 bytes, adds graphics/MPEG engine context pointer binding, uses an NV40 RAMHT context format, and performs chipset-specific RAMFC placement setup.

Important APIs and data: `nv40_chan_ramfc_write()`, `nv40_chan_ramfc`, `nv40_chan_userd`, `nv40_eobj_ramht_add()`, `nv40_ectx_bind()`, `nv40_fifo_init()`, `nv40_fifo`, and `nv40_fifo_new()`.

Control flow: channel creation writes put/get, push instance, fetch config, and timeslice fields into per-channel RAMFC. Engine object creation inserts RAMHT entries with `chan->id << 23 | engn->id << 20`. Engine context binding pauses PFIFO cache switching, updates the active engine register if the channel is current, writes the RAMFC context slot, and resumes PFIFO. Initialization programs RAMHT/RAMRO and chooses RAMFC addressing differently for selected NV40 chipsets versus later ones.

State and persistence: RAMFC stores DMA, acquire/semaphore, GR context, MPEG context, and assorted PFIFO state. USERD maps through BAR0 PRI at `0xc00000`. Runtime engine context bindings are mirrored in both hardware registers and RAMFC.

Dependencies and integration: depends on NV04 interrupt/pause/start/runlist code, instmem RAMHT/RAMRO/RAMFC, FB memory size for RAMFC placement, and `NV40_CHANNEL_DMA`.

Risks: chipset-specific RAMFC placement is fragile; binding engine context while PFIFO is active requires correct locking and cache disable; MPEG binding is only valid on chipset >= 0x44.

Test signals: NV40 channel creation, graphics context switch correctness, MPEG object binding where present, RAMHT lookups, PFIFO init register values per chipset, and inherited cache-error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv50.c

Purpose: implements NV50 FIFO, bridging legacy PFIFO interrupt handling with RAMRL runlist updates and per-channel GPU objects. It introduces per-channel RAMFC/engine/PGD/RAMHT allocations, runlist memory allocation/update, context binding, and NV50 channel class support.

Important APIs and data: `nv50_eobj_ramht_add/del()`, `nv50_chan_start/stop/unbind()`, `nv50_chan_ramfc_write()`, `nv50_ectx_bind()`, `nv50_runl_wait()`, `nv50_runl_update()`, `nv50_fifo_init()`, `nv50_fifo_chid_ctor()`, `nv50_fifo_chid_nr()`, and `nv50_fifo_new()`. The key tables are `nv50_chan`, `nv50_engn`, `nv50_engn_sw`, `nv50_runl`, and `nv50_fifo`.

Control flow: channel creation allocates RAMFC, engine context object, PGD, and RAMHT under the channel instance object, then initializes RAMFC fields for pushbuffer limits and RAMHT search. Runlist update allocates or reuses runlist memory, writes hardware channel groups and channels through `insert_*`, rotates groups for fairness, and commits count/address to PFIFO. Engine context binding writes start/limit/flags into the channel engine object; unbinding may force engine context save as a hardware bug workaround.

State and persistence: state is runtime GPU object memory under each channel, per-channel RAMHT, runlist memory (`runl->mem`), `runl->offset` ring allocation, and channel ID allocation from 1 to 126.

Dependencies and integration: uses NV04 interrupt/pause/start for compatible PFIFO bits, generic runlist/channel-group core, RAMHT helpers, timer polling, and `NV50_CHANNEL_GPFIFO`.

Risks: `nv50_runl_alloc()` must avoid overwriting in-flight runlists and can time out; context unbind workaround polls engine state; CHID 0 and 127 are reserved; runlist update has TODOs for priority/interleaving/forward progress.

Test signals: runlist update traces, no timeout from `nv50_runl_wait()`, channel RAMHT object insertion, valid `NV50_CHANNEL_GPFIFO` creation, interrupt handling for non-stall events, and channel ID reservation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/priv.h

Purpose: private FIFO interface header tying chip-specific FIFO implementations to the common FIFO engine. It defines `struct nvkm_fifo_func`, nested MMU fault, channel-group, and channel descriptors, and exports cross-generation helper declarations.

Important APIs and data: `struct nvkm_fifo_func` contains callbacks for destruction, CHID/runqueue/runlist creation, init, PBDMA init, interrupt handling, MMU fault parsing/recovery, pause/start, non-stall events, and selected runlist/runqueue/engine/channel/group function tables. It declares constructors including `nvkm_fifo_new_()` and `r535_fifo_new()`, plus exported helpers from NV04, NV50, GF100, GK104, GK110, GK208, GM107, GM200, GV100, TU102, GA100, and GB202 paths.

Control flow: chip files fill an `nvkm_fifo_func` table, then pass it to the common constructor. The common FIFO layer invokes callbacks to size allocators, create runqueues/runlists, initialize hardware, route interrupts, expose NVIF channel/group classes, and bind engine/channel behavior.

State and persistence: the header defines no storage itself. It specifies the callback contract that controls runtime state in `struct nvkm_fifo`, `nvkm_runl`, `nvkm_runq`, `nvkm_cgrp`, and `nvkm_chan`.

Dependencies and integration: includes public FIFO engine and enum definitions, and references fault, event, object, memory, runlist, runqueue, channel, group, and engine structures. It is the integration point for both nouveau-managed and R535/GSP-managed FIFO construction.

Risks: callback tables must be internally consistent; missing callbacks can be valid for old hardware but fatal for newer helpers expecting them; declarations couple many generations, so signature changes have broad blast radius.

Test signals: full driver build is the main signal. Runtime signals include each chip constructor resolving all symbols, correct NVIF class exposure from `.cgrp` and `.chan`, and expected interrupt/fault callbacks invoked for each device generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/regsnv04.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/regsnv04.h

Purpose: defines legacy PFIFO register offsets and bitfields used by NV03/NV04 through NV50-era FIFO code. It centralizes interrupt, RAMHT/RAMFC/RAMRO, cache, DMA fetch, semaphore, acquire, method/data, and CHID mask constants.

Important APIs and data: macros include `NV03_PFIFO_INTR_0`, `NV03_PFIFO_INTR_EN_0`, `NV_PFIFO_INTR_*` bits, `NV03_PFIFO_RAMHT/RAMFC/RAMRO`, `NV03_PFIFO_CACHES`, `NV04_PFIFO_MODE`, `NV50_PFIFO_CTX_TABLE()`, cache push/pull registers, DMA fetch trigger/size/max request encodings, endian bits, acquire/semaphore registers, and method/data address macros for NV04 and NV40 layouts.

Control flow: no executable flow exists. Consumers use these constants to initialize PFIFO, save/restore RAMFC layouts, decode and acknowledge interrupts, advance cache GET/PUT pointers, and recover from DMA/cache errors.

State and persistence: macros describe hardware state locations. Runtime state is in PFIFO registers and instance memory managed by the C files.

Dependencies and integration: included by NV04/NV10/NV17/NV40 legacy FIFO implementations. The constants must match hardware manuals/reverse-engineered behavior.

Risks: bad offsets or masks cause hardware hangs or silent corruption. Some symbolic names alias different generation semantics, so consumers must choose generation-correct macros. Large DMA fetch encoding tables are easy to misuse.

Test signals: successful compile, correct legacy PFIFO init values, cache-error recovery using the expected method/data address space, and no regressions in NV04/NV10/NV17/NV40/NV50 interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/regsnv04.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runl.c

Purpose: implements generic FIFO runlist lifecycle, lookup, update gating, block/allow, and recovery-control logic shared by NV50+ and modern FIFO backends.

Important APIs and data: `nvkm_runl_new()`, `nvkm_runl_get()`, `nvkm_runl_add()`, `nvkm_runl_del()`, `nvkm_runl_fini()`, `nvkm_runl_block()`, `nvkm_runl_allow()`, `nvkm_runl_update_locked()`, `nvkm_runl_update_pending()`, `nvkm_runl_preempt_wait()`, `nvkm_runl_rc_engn()`, `nvkm_runl_rc_cgrp()`, `nvkm_runl_chan_get_chid()`, `nvkm_runl_chan_get_inst()`, and `nvkm_runl_cgrp_get_cgid()`.

Control flow: recovery starts when a channel group or engine schedules RC. The runlist is blocked, optionally preempted, `rc_pending` is incremented, and work is queued. The worker locks the runlist, marks pending channel groups as running recovery, errors and removes their channels, waits for runqueues to idle on preempt-capable hardware, resets engines still pointing at recovering groups, commits a runlist update, clears fault state, unblocks the runlist as many times as it was blocked for RC, and waits for the update.

State and persistence: state is runtime-only: runlist lists, engine list, cgrp/chan counts, `changed`, `blocked`, `rc_triggered`, `rc_pending`, runlist memory pointer/offset, work item, mutex, and shared `nvkm_chid` references. Lookup helpers return objects with locks held and irq flags handed back to callers.

Dependencies and integration: depends on channel/group/chid/runqueue structures, TOP fault-id lookup, engine reset, timers, and chip-specific `nvkm_runl_func` callbacks for update, wait, pending, block, allow, fault clear, and preempt.

Risks: recovery can reset engines and kill all channels in a group; lock ordering between CHID locks and group locks is critical; missing `cxid`/`idle` callbacks reduce recovery precision; block counters must remain balanced.

Test signals: runlist update after channel insert/remove, RC scheduling logs, errored-channel events, successful preempt wait, no deadlocks under concurrent channel destruction and interrupt recovery, and clean unload after `flush_work()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runl.h

Purpose: declares generic runlist and host-engine structures and callback contracts used by FIFO implementations.

Important APIs and data: `struct nvkm_engn_func` defines non-stall, channel-switch status, current channel/group ID, synthetic MMU fault, engine context construction/binding, RAMHT add/delete, and secondary constructor hooks. `struct nvkm_runl_func` defines init/fini, runqueue count, descriptor size, runlist update/insert/commit/wait/pending, block/allow, fault clear, preempt, and preempt-pending callbacks. `struct nvkm_runl` stores IDs, doorbell, CHID/CGID allocators, engine and group lists, runqueue pointers, interrupt hooks, memory, locks, and RC atomics.

Control flow: the header establishes how chip-specific FIFO code plugs into generic runlist management. Macros iterate runlists, engines, and channel groups and provide logging prefixes.

State and persistence: describes runtime-only in-memory state. No durable persistence exists.

Dependencies and integration: included by FIFO chip files, user channel code, and runlist implementation. It references `nvkm_engine`, `nvkm_fifo`, `nvkm_chid`, `nvkm_memory`, `nvkm_inth`, and Linux work/mutex/list primitives.

Risks: the fixed `runq[2]` array constrains current multi-runqueue support; callback nullability differs by generation; callers must respect lock/put protocols for lookup helpers.

Test signals: successful compilation of all FIFO variants, correct runlist logging prefixes, runqueue assignment not exceeding two entries, and runtime recovery paths invoking the intended callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runq.c

Purpose: implements minimal allocation and destruction for FIFO runqueues/PBDMAs.

Important APIs and data: `nvkm_runq_new()` allocates a zeroed `struct nvkm_runq`, assigns `fifo->func->runq`, stores FIFO pointer and PBDMA id, and appends it to `fifo->runqs`. `nvkm_runq_del()` removes the list entry and frees it.

Control flow: common FIFO construction creates one runqueue per hardware PBDMA using this helper. Chip-specific runqueue callbacks then initialize registers, handle interrupts, and report idle state.

State and persistence: state is an in-memory list node, callback pointer, FIFO pointer, and PBDMA id. No hardware programming is done here and no state persists across driver lifetime.

Dependencies and integration: depends on `runq.h` and `priv.h`, and is consumed by the common FIFO constructor and chip-specific runlist constructors that associate runqueues with runlists.

Risks: allocation failure returns NULL rather than encoded error; callers must handle it. Deleting a runqueue assumes it is linked and no longer referenced by a runlist.

Test signals: runqueue count equals chip-specific `runq_nr`, PBDMA ids match interrupt/register offsets, clean teardown removes all list entries, and build coverage for FIFO construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runq.h

Purpose: declares the FIFO runqueue/PBDMA abstraction and its callback contract.

Important APIs and data: `struct nvkm_runq_func` has callbacks for init, interrupt handling, PBDMA INTR0 names, HCE CTXNOTVALID handling, and idle checks. `struct nvkm_runq` stores the callback table, owning FIFO, PBDMA id, and list node. Macros provide runqueue iteration and prefixed logging.

Control flow: chip-specific FIFO tables point `.runq` at a `nvkm_runq_func`; common construction creates runqueues; interrupt handlers iterate matching runqueues and call `runq->func->intr()`.

State and persistence: runtime in-memory only. Hardware state is owned by chip-specific callbacks.

Dependencies and integration: included by GF100/GK104/GK208/GV100 FIFO paths and generic runqueue construction.

Risks: optional callbacks require guards; missing idle callback limits recovery on preempt-capable runlists; logging macro assumes valid FIFO/subdev pointers.

Test signals: compile-time callback consistency, PBDMA interrupt logs with correct id, idle polling during recovery, and no NULL callback dereferences on older hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/tu102.c

Purpose: implements Turing TU102 FIFO support. It extends Volta with runlist-id-qualified doorbell handles, VFN doorbell writes on channel start, Turing runlist commit registers, new context-switch timeout decoding, Turing MMU fault engine table, and optional GSP/R535 FIFO construction.

Important APIs and data: `tu102_chan_doorbell_handle()`, `tu102_chan_start()`, `tu102_runl_pending()`, `tu102_runl_commit()`, `tu102_fifo_intr_ctxsw_timeout_info()`, `tu102_fifo_intr()`, `tu102_fifo_init_pbdmas()`, `tu102_fifo_mmu_fault`, and `tu102_fifo_new()`.

Control flow: channel start first enables the inherited GK104 channel bit, then writes the doorbell token to `device->vfn->addr.user + 0x0090`. Runlist commit writes low/high address and count to `0x002b00 + runl * 0x10`. Context-switch timeout handling reads an engine mask from `0x002a30`, fetches per-engine info from `0x003200 + engine * 4`, determines whether load/save/switch state identifies next or previous CGID, and schedules channel-group recovery. Interrupt handling is Turing-specific and omits the older explicit MMU fault interrupt branch.

State and persistence: state is runtime hardware state, especially VFN doorbell address, runlist id, channel id, and channel-group recovery state. GSP-managed devices route construction through `r535_fifo_new()`.

Dependencies and integration: depends on GSP detection, VFN subdevice, GV100 runlist descriptors and engine functions, GK104 bind/CHSW/runlist interrupt helpers, GF100 PBDMA/nonstall helpers, and `TURING_CHANNEL_GPFIFO_A`.

Risks: doorbell write requires valid VFN mapping; the runlist commit has an unresolved target comment; context-switch timeout info decoding is bit-sensitive; GSP path changes ownership of FIFO operations.

Test signals: TU102 channel creation returning `(runlist << 16) | chid`, doorbell write on start, runlist commits to `0x002b00` block, context-switch timeout recovery for load/save/switch states, and both native and GSP-managed constructor paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/ucgrp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/ucgrp.c

Purpose: implements the user-visible FIFO channel-group object. It parses NVIF channel-group creation arguments, resolves runlist and VMM handles, creates a hardware/software channel group, exposes channel child classes, and returns the CGID to userspace.

Important APIs and data: `struct nvkm_ucgrp`, `nvkm_ucgrp_new()`, `nvkm_ucgrp_chan_new()`, `nvkm_ucgrp_sclass()`, and `nvkm_ucgrp_dtor()`. It uses `union nvif_cgrp_args` version 0 and stores a referenced `struct nvkm_cgrp`.

Control flow: constructor validates ABI version and name length, looks up the requested runlist by id, resolves the VMM handle from the client, allocates the user object, calls `nvkm_cgrp_new(runl, name, vmm, true, &cgrp)`, and writes `args->v0.cgid`. The class enumerator exposes the FIFO channel class as a child whose constructor creates a channel inside this group.

State and persistence: holds a reference to `nvkm_cgrp` until object destruction. Runtime group state lives in the channel-group object and runlist; no durable persistence exists.

Dependencies and integration: depends on `nvkm_runl_get()`, `nvkm_uvmm_search()`, `nvkm_cgrp_new()`, `nvkm_uchan_new()`, MMU/VMM handles, and the FIFO function table's channel class.

Risks: ABI validation is strict; missing runlist/VMM returns errors; exposing only one child channel class means class table correctness depends on `fifo->func->chan.user`; failure after object construction relies on object cleanup.

Test signals: NVIF channel-group creation with valid/invalid runlist and VMM handles, returned CGID, child channel class enumeration, group destruction releasing references, and channel creation within the group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/ucgrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/uchan.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/uchan.c

Purpose: implements the user-visible FIFO channel object and channel child engine-object proxying. It creates channels from NVIF args, maps USERD, exposes engine object classes, handles channel init/fini, binds/unbinds engine contexts on object lifecycle, supports non-stall/killed events, and returns channel tokens/instance information to userspace.

Important APIs and data: `struct nvkm_uchan`, `struct nvkm_uobj`, `nvkm_uchan_new()`, `nvkm_uchan_chan()`, `nvkm_uchan_init()`, `nvkm_uchan_fini()`, `nvkm_uchan_map()`, `nvkm_uchan_sclass()`, `nvkm_uchan_object_new()`, and proxy callbacks `nvkm_uchan_object_init_0()`, `nvkm_uchan_object_fini_1()`, and `nvkm_uchan_object_dtor()`.

Control flow: constructor validates NVIF channel args, resolves runlist, VMM, DMA object, and optional USERD memory, allocates a user object, calls `nvkm_chan_new_()`, returns doorbell token or `~0`, CHID, instance aperture, and instance address. Init binds the channel, allows it, and inserts it into the runlist unless already errored. Fini blocks/removes the channel and unbinds hardware. Child object creation finds the host engine, obtains a channel context, constructs the engine object under the context object when present, and inserts RAMHT entries when required.

State and persistence: maintains channel references, channel context references, refcounts for engine/channel context use, RAMHT hash values, and runtime events. No durable persistence.

Dependencies and integration: depends on channel/group/runlist/chid helpers, VMM and DMA object handle lookup, GPU memory mapping, engine FIFO class enumeration, object proxy lifecycle, and FIFO channel function tables.

Risks: complex lifetime/refcount sequencing around `cctx->uses` and `ectx->uses`; partial failures after object/proxy allocation must unwind through object destruction; runqueue-specific CE class filtering assumes `chan->runq` matches runlist runqueue layout; mapping requires channel USERD BAR support.

Test signals: NVIF channel creation with VMM/ctxdma/userd variants, USERD mmap address/size, init/fini channel insertion/removal, killed and non-stall uevents, engine object creation/destruction with RAMHT cleanup, and errored-channel init behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/uchan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/Kbuild

Purpose: declares the Nouveau graphics engine object files that build into `nvkm-y`. It includes the base GR engine, generation-specific GR engines from NV04 through GA102, and context-generation files from NV40 through GA102.

Important APIs and data: entries append `nvkm/engine/gr/*.o` files to `nvkm-y`. The first block lists engine implementations such as `base.o`, `gf100.o`, `gk104.o`, `gm200.o`, `gv100.o`, `tu102.o`, and `ga102.o`; the second block lists context generators such as `ctxgf100.o`, `ctxgf104.o`, `ctxgk104.o`, `ctxgm200.o`, `ctxgv100.o`, `ctxtu102.o`, and `ctxga102.o`.

Control flow: no runtime control flow. Kbuild uses these entries to compile and link the GR implementation into the kernel module/built-in driver.

State and persistence: no runtime state. Build configuration state is the ordered object list.

Dependencies and integration: integrates the GR subtree into the larger Nouveau NVKM build. FIFO engine-object enumeration and context binding depend on these GR objects being linked.

Risks: missing an object file causes unresolved symbols or unsupported GPU generations; stale entries can break builds if files are removed; build order can matter when archives resolve symbols.

Test signals: kernel/module build success, no unresolved GR context symbols, and probe coverage for listed generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/base.c

Purpose: implements the generic GR engine wrapper. It adapts `struct nvkm_gr_func` chip callbacks to `struct nvkm_engine_func`, exposes context-switch helpers, tile/TLB/unit helpers, FIFO class hooks, and the GR constructor.

Important APIs and data: `nvkm_gr_ctxsw_inst()`, `nvkm_gr_ctxsw_resume()`, `nvkm_gr_ctxsw_pause()`, `nvkm_gr_units()`, `nvkm_gr_tlb_flush()`, `nvkm_gr_ctor()`, and internal engine callbacks for object class lookup, channel class construction, interrupt, non-stall, oneinit, reset, init, fini, and dtor. The static `nvkm_gr` engine function table wires these callbacks into NVKM.

Control flow: public helpers check for `device->gr` and optional chip callbacks before invoking them. FIFO object enumeration calls `nvkm_gr_oclass_get()` to fetch graphics object classes, and channel object creation calls `nvkm_gr_cclass_new()` for per-channel class setup. Engine lifecycle calls forward to chip-specific GR functions if present.

State and persistence: `struct nvkm_gr` stores the selected function table and is embedded in an `nvkm_engine`. The file manages no durable state; lifecycle callbacks may create hardware state in chip files.

Dependencies and integration: depends on `priv.h`, FIFO channel objects, and the NVKM engine core. It is the bridge between FIFO-created channel objects and GR-specific object/context handling.

Risks: optional callback handling returns neutral values in many cases, so missing chip callbacks can silently disable features; object class index accounting must remain correct for FIFO enumeration; reset returns `-ENOSYS` if not implemented.

Test signals: GR engine construction, object class enumeration through FIFO channels, context-switch pause/resume helpers, interrupt forwarding, non-stall forwarding, and chip-specific init/fini/reset callbacks firing during device lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxga102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxga102.c

Purpose: defines GA102/Ampere graphics context-generation parameters and a few GA102-specific patch functions on top of the GF100/GV100/TU102 context framework.

Important APIs and data: `ga102_grctx_generate_sm_id()` maps logical TPC through `gv100_gr_nonpes_aware_tpc()` and writes SM id at `TPC_UNIT(..., 0x608)`. `ga102_grctx_generate_unkn()` sets bits in `0x41980c` and `0x41be08`. `ga102_grctx_generate_r419ea8()` writes `0x419ea8` from `0x504728 | 0x08000000`. The exported `ga102_grctx` table selects buffer sizes, counts, and inherited generation hooks.

Control flow: the generic `gf100_grctx_generate_main()` calls the function-table hooks for bundle/pagepool/attribute buffers, unknown buffer, floorsweeping, ROP mapping, and late register patches. GA102 custom hooks run during those phases.

State and persistence: context data is generated into runtime graphics context images and patch buffers. The table defines bundle size `0x3000`, pagepool `0x20000`, attrib/alpha counts, unknown buffer size `0x80000`, and GFXP count `0xd28`.

Dependencies and integration: depends on `ctxgf100.h` declarations, inherited GM107/GP100/GP102/GV100/TU102/GM200 helpers, and GA102 GR engine code selecting this table.

Risks: register constants and count values are tightly hardware-specific; non-PES-aware TPC mapping would produce wrong SM ids; missing hub/GPC/TPC pack pointers means this table relies on inherited firmware or alternate paths in the broader GA102 GR code.

Test signals: GA102 context generation success, no FECS/golden context timeout, correct SM id programming on floorswept GPUs, valid attribute/bundle/pagepool sizes, and graphics workloads surviving context switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf100.c

Purpose: implements the GF100/Fermi graphics context generator and the baseline register-init packs used by many later GR context variants. It contains large MMIO/init lists, patch helpers, buffer setup, floorsweeping, ROP/alpha/beta mapping, FECS/golden context generation, and the exported `gf100_grctx` table.

Important APIs and data: exported symbols include `gf100_grctx_patch_wr32()`, `gf100_grctx_generate_main()`, `gf100_grctx_generate()`, `gf100_grctx_generate_bundle()`, `gf100_grctx_generate_pagepool()`, `gf100_grctx_generate_attrib_cb_size()`, `gf100_grctx_generate_attrib_cb()`, `gf100_grctx_generate_attrib()`, `gf100_grctx_generate_floorsweep()`, `gf100_grctx_generate_sm_id()`, `gf100_grctx_generate_tpc_nr()`, `gf100_grctx_generate_rop_mapping()`, `gf100_grctx_generate_alpha_beta_tables()`, and many `gf100_grctx_pack_*` / `gf100_grctx_init_*` lists.

Control flow: `gf100_grctx_generate()` forces FE power, resets FECS, allocates temporary context memory with a reserved prefix, maps it into the channel VMM, points the channel instance at it, makes the channel current either through firmware FECS bind or direct registers, runs `grctx->main()`, unloads/saves the golden context, copies generated context data into `gr->data`, and clears the instance pointer. `gf100_grctx_generate_main()` loads MMIO packs, waits idle, patches pagepool/bundle/attribute buffers, performs floorsweeping, loads indirect command and method bundles, restores timeouts, and applies late hooks.

State and persistence: generated context data is cached in `gr->data` for runtime use. Temporary `nvkm_memory` and VMA allocations are freed. Hardware state is programmed during generation and synchronized through idle waits.

Dependencies and integration: depends on GF100 GR private structures, FB/MC/timer helpers, FIFO context helpers, FECS firmware paths, and later variant tables declared in `ctxgf100.h`.

Risks: massive register tables are difficult to audit; missing alpha/beta maps fall back with warnings; FECS/golden-save timeouts can fail context generation; floorsweeping depends on accurate `gpc/tpc/sm/tile` topology; patch-buffer path changes behavior when `chan->mmio` is present.

Test signals: successful golden context generation, FECS bind/save completion, no idle wait timeouts, stable `gr->data` size, graphics context switch tests, warnings for missing alpha/beta mapping, and workloads on floorswept GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf100.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf100.h

Purpose: declares the GF100-family graphics context generation interface, function table, generation hooks, variant tables, and shared init-pack symbols.

Important APIs and data: `struct gf100_grctx_func` defines hooks for main generation, unknown setup, MMIO packs, indirect command/method packs, bundle/pagepool/attribute buffers, patch buffers, floorsweeping, SM/TPC/ROP/alpha/beta mapping, and many late register hooks. It declares `gf100_grctx_generate()`, shared GF100 helpers, and variant tables from GF108/GF104/GF110 through GA102.

Control flow: chip GR files select one `gf100_grctx_func` table. The generic generator calls callbacks in defined phases: MMIO pack load, buffer patching, floorsweeping, indirect bundle/method emission, and late register fixes.

State and persistence: no storage itself. It defines parameters and hooks that control generated graphics context images, patch buffers, and hardware register state.

Dependencies and integration: includes `gf100.h` and is used by all GF100-derived context generator C files. FIFO engine context binding ultimately consumes generated GR context objects through channel contexts.

Risks: broad declaration surface means incompatible signature or field changes affect many generations; optional hooks require careful null checks; table parameter mistakes can create invalid context images without compile-time detection.

Test signals: full build across all GR context files, variant table linkage, successful context generation on multiple generations, and no unresolved shared init-pack symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf104.c

Purpose: defines GF104 graphics context differences from GF100, focused on TPC/TEX/L1C/SM init lists and a context function table that otherwise reuses the GF100 generator.

Important APIs and data: `gf104_grctx_init_tex_0`, `gf104_grctx_init_l1c_0`, `gf104_grctx_init_sm_0`, private `gf104_grctx_pack_tpc`, and exported `gf104_grctx`.

Control flow: `gf104_grctx` selects `gf100_grctx_generate_main()` and the standard GF100 hub/GPC/ZCULL/ICMD/MTHD packs, but swaps the TPC pack to use GF104 TEX/L1C/SM register values. Buffer generation, floorsweeping, ROP mapping, alpha/beta tables, and late hooks are inherited.

State and persistence: generated graphics context images include GF104-specific TPC register defaults. No independent runtime state exists in this file.

Dependencies and integration: depends on `ctxgf100.h`, GF100 shared init packs and helper functions, and the GF104 GR engine selecting this table.

Risks: only selected TPC blocks differ; if GF104 hardware requires other deviations they would be missed. Register-list mistakes can show up as graphics faults or context-switch failures rather than compile errors.

Test signals: GF104 context generation, TPC init list application, stable graphics workloads, context switch success, and absence of FECS/golden context timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf104.c -->
