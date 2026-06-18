# Research: subset-b-003689

Grouped source research for subset B work item `subset-b-003689`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/nv04.c

## Purpose
Implements NV04-generation instance memory backed by the PRAMIN aperture at `0x700000`. It allocates small GPU instance objects from a fixed 512 KiB heap and reserves early regions for VBIOS, RAMHT, RAMFC, and RAMRO.

## Important APIs, Types, and Functions
Key types are `struct nv04_instmem` and `struct nv04_instobj`. Main entry points are `nv04_instmem_new`, `nv04_instobj_new`, `nv04_instmem_oneinit`, `nv04_instmem_suspend`, and `nv04_instmem_resume`. Object memory operations provide `rd32`, `wr32`, `acquire`, `size`, `addr`, `target`, and destructor callbacks through `nvkm_memory_func`.

## Control Flow, State, and Persistence
Object creation constructs an `nvkm_instobj`, allocates a `nvkm_mm_node` under the instmem mutex, and exposes PRAMIN-relative offsets as `NVKM_MEM_TARGET_INST`. One-time initialization reserves known legacy layout ranges by calling `nvkm_memory_new` and `nvkm_ramht_new`. Suspend saves preservable objects, shuts down BAR2, then saves boot objects; resume reloads boot objects, initializes BAR2, and reloads normal objects.

## Dependencies and Integration Points
It depends on `nvkm_mm`, `nvkm_memory`, `nvkm_ramht`, BAR2 helpers, PRAMIN MMIO access, and the common instmem object lifecycle in `priv.h`. Channel/context code consumes the reserved RAMHT/RAMFC/RAMRO objects.

## Risks and Test Signals
Risks are fixed layout assumptions, off-by-one PRAMIN heap allocation, missing suspend preservation, and unsafe direct MMIO offsets. Test signals include boot on NV04/NV1x/NV3x hardware, channel creation, suspend/resume context restore, BAR2 reinitialization, and debug reads of reserved RAMHT/RAMFC regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/nv40.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/nv40.c

## Purpose
Provides NV40-generation instance memory using a write-combined CPU mapping of the PRAMIN BAR. It extends the NV04 fixed-reservation model with larger context-storage sizing based on chipset and graphics partition counts.

## Important APIs, Types, and Functions
Important symbols are `nv40_instmem_new`, `nv40_instmem_oneinit`, `nv40_instobj_new`, `nv40_instmem_rd32`, `nv40_instmem_wr32`, and `nv40_instmem_dtor`. The `nv40_instobj` memory callbacks use `ioread32_native` and `iowrite32_native` against `imem->iomem`.

## Control Flow, State, and Persistence
Constructor initializes the common instmem subdevice and maps `NVKM_BAR2_INST` with `ioremap_wc`. Oneinit computes `base.reserved` from vertex shader/graphics class information, adds space for GART and object storage, initializes the heap, and reserves VBIOS/RAMHT/RAMRO/RAMFC ranges. Object allocation and destruction mirror NV04 but address the WC mapping. Release issues `wmb()` to order host writes.

## Dependencies and Integration Points
It integrates with device BAR resource callbacks, `nv44_gr_class`, `hweight8` shader counting, `nvkm_mm`, `nvkm_ramht`, and common instmem consumers. The mapped BAR is destroyed with `iounmap`.

## Risks and Test Signals
Risks include incorrect generation-specific reserved-size formulas, failed PRAMIN BAR mapping, missing write barriers, and heap overlap with hardware context storage. Test with NV40/NV44 variants, many-channel allocation, BAR resource failures, RAMHT setup, and suspend/resume or module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/nv40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/nv50.c

## Purpose
Implements NV50+ instance memory objects backed by real VRAM/instance memory and mapped for CPU access through BAR2 when possible, with a BAR0 PRAMIN window fallback. It supports wrapping existing `nvkm_memory` for BAR2-visible instmem objects.

## Important APIs, Types, and Functions
Key entry points are `nv50_instmem_new`, `nv50_instmem_new_`, `nv50_instobj_new`, `nv50_instobj_wrap`, `nv50_instobj_acquire`, `nv50_instobj_release`, `nv50_instobj_kmap`, `nv50_instobj_boot`, `nv50_instobj_bar2`, and `nv50_instmem_fini`. `nv50_instobj_fast` and `nv50_instobj_slow` select direct BAR2 or windowed access.

## Control Flow, State, and Persistence
Allocation uses `nvkm_ram_get` with page alignment, wraps it in an instobj, and lazily maps it into BAR2 VMM on first acquire. If BAR2 space is exhausted, unused mappings are evicted from `imem->lru`; active mappings are protected by a refcount. Release flushes BAR writes and returns inactive mappings to the LRU. Bootstrapped BAR page-table objects are removed from eviction and call `nvkm_instmem_boot`. Fini invalidates the cached BAR0 window base.

## Dependencies and Integration Points
This file depends on BAR1/BAR2 VMM helpers, VRAM allocation, `nvkm_memory_map`, MMIO window register `0x001700`, GSP detection, and R535 instmem delegation. It reuses NV04 suspend/resume save/restore.

## Risks and Test Signals
Risks include BAR2 LRU races, stale `memory.ptrs` during refcount transitions, missing BAR flushes, windowed access contention, and GSP/non-GSP path divergence. Test signals include BAR2 exhaustion, concurrent acquire/release, bootstrapped page-table mappings, R535 delegation, suspend/resume restore, and MMIO read/write verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/priv.h

## Purpose
Defines the private instmem hardware interface and common instance-object structure used by NV04, NV40, NV50, and firmware-backed implementations.

## Important APIs, Types, and Functions
`struct nvkm_instmem_func` declares lifecycle hooks, direct register accessors, memory allocation/wrapping hooks, zeroing policy, and BAR0 window programming. `struct nvkm_instobj` embeds `nvkm_memory` plus list/preserve/suspend state. The header declares common constructors/destructors and save/load helpers.

## Control Flow, State, and Persistence
The header has no executable control flow. It defines persistent object state used by suspend/resume: `preserve` selects objects to save, while `suspend` stores saved dwords.

## Dependencies and Integration Points
It includes public `subdev/instmem.h` and `core/memory.h`, and is consumed by all instmem backends plus R535 glue.

## Risks and Test Signals
Signature drift breaks chip-specific backends. Save/load state must remain compatible with every `nvkm_memory_func`. Build coverage across NV04/NV40/NV50/GSP configurations and suspend/resume tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/Kbuild

## Purpose
Adds the LTC subdevice objects to the Nouveau NVKM build for Fermi through Ampere/Tegra variants.

## Important APIs, Types, and Functions
The build list includes `base.o`, `gf100.o`, `gk104.o`, `gm107.o`, `gm200.o`, `gp100.o`, `gp102.o`, `gp10b.o`, and `ga102.o`.

## Control Flow, State, and Persistence
There is no runtime control flow. Build order makes the shared base and exported generation helpers available before chip-specific constructors are linked.

## Dependencies and Integration Points
This Kbuild fragment is included by the Nouveau NVKM kernel build. It must stay aligned with chip constructors referenced by device tables.

## Risks and Test Signals
Omitting an object causes unresolved constructor or helper symbols for that GPU family. Signals are kernel build coverage for all enabled Nouveau configurations and module load on supported chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/base.c

## Purpose
Provides the common LTC subdevice wrapper for cache tag clearing, zero-bandwidth clear programming, cache invalidation/flush, interrupt dispatch, and subdevice lifetime.

## Important APIs, Types, and Functions
Public helpers are `nvkm_ltc_tags_clear`, `nvkm_ltc_zbc_color_get`, `nvkm_ltc_zbc_depth_get`, `nvkm_ltc_zbc_stencil_get`, `nvkm_ltc_invalidate`, `nvkm_ltc_flush`, and `nvkm_ltc_new_`. Internal subdev hooks are `nvkm_ltc_oneinit`, `nvkm_ltc_init`, `nvkm_ltc_intr`, and `nvkm_ltc_dtor`.

## Control Flow, State, and Persistence
Construction stores the chip `nvkm_ltc_func`, initializes the mutex, and calculates valid ZBC color/depth index ranges while reserving index 0. Init replays all stored ZBC color/depth/stencil entries before invoking the chip init hook. Tag clearing validates the tag range, serializes through `ltc->mutex`, calls hardware clear, and waits.

## Dependencies and Integration Points
It depends on chip callbacks in `priv.h`, `nvkm_memory_unref` for `tag_ram`, public `subdev/ltc.h`, and framebuffer tag allocation users.

## Risks and Test Signals
Risks include invalid tag range BUGs, missing optional stencil callbacks, stale ZBC replay after reset, and cache flush hooks being absent on a chip. Test with ZBC allocation/replay, compression tag allocation, interrupt dispatch, cache invalidation/flush, and subdevice teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/ga102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/ga102.c

## Purpose
Defines the Ampere GA102 LTC backend for non-GSP-RM operation, mainly extending GP100-family behavior with a wider ZBC color selector.

## Important APIs, Types, and Functions
`ga102_ltc_zbc_clear_color` writes ZBC color entries using a 5-bit index field. `ga102_ltc_new` rejects GSP-RM devices with `-ENODEV` and otherwise registers `ga102_ltc`.

## Control Flow, State, and Persistence
The function table reuses GP100 oneinit/init/interrupt, GM107 CBC and depth clear routines, GP102 stencil clear, and GF100 cache invalidate/flush. Stored ZBC entries from base.c persist and are replayed through the GA102 color path.

## Dependencies and Integration Points
It depends on `subdev/gsp.h`, GP100/GM107/GF100/GP102 shared helpers, and device-family constructor routing.

## Risks and Test Signals
Risks are incorrect ZBC index width, using this backend under firmware-owned GSP RM, and mismatched reused register offsets. Test non-GSP GA102 initialization, ZBC color slots above 15, stencil/depth clear replay, and GSP-RM fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/ga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gf100.c

## Purpose
Implements Fermi LTC hardware operations: CBC tag clearing, tag RAM allocation, ZBC programming, interrupt decoding, and cache flush/invalidate.

## Important APIs, Types, and Functions
Important exports are `gf100_ltc_cbc_clear`, `gf100_ltc_cbc_wait`, `gf100_ltc_zbc_clear_color`, `gf100_ltc_zbc_clear_depth`, `gf100_ltc_intr`, `gf100_ltc_invalidate`, `gf100_ltc_flush`, `gf100_ltc_oneinit_tag_ram`, `gf100_ltc_oneinit`, and `gf100_ltc_new`. `gf100_ltc_lts_intr_name` names LTS interrupt bits.

## Control Flow, State, and Persistence
Oneinit counts enabled LTC partitions and slices from hardware masks, allocates conservative tag RAM from VRAM when present, aligns `tag_base`, and initializes the framebuffer tag allocator. Init programs LTC count, tag base, and large-page mode. CBC clear writes start/limit/command registers and waits every LTC/LTS status register. Interrupt handling scans the master mask and acknowledges per-slice status.

## Dependencies and Integration Points
It integrates with `nvkm_fb`, `nvkm_ram_get`, `fb->tags.mm`, timer wait helpers, compression tag users, and base.c ZBC replay.

## Risks and Test Signals
Risks include over/under-allocating tag RAM, wait timeouts, wrong partition mask interpretation, and missed ECC/error interrupts. Test compressed render targets, tag clear ranges, cache flush/invalidate timing, LTS interrupt injection, no-VRAM behavior, and multi-partition GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gk104.c

## Purpose
Provides the Kepler GK104 LTC function table and init differences while reusing the GF100 core implementation.

## Important APIs, Types, and Functions
`gk104_ltc_init` programs LTC count into both `0x17e8d8` and `0x17e000`, writes `tag_base`, and sets large-page mode. `gk104_ltc_new` registers the `gk104_ltc` table.

## Control Flow, State, and Persistence
Oneinit, interrupts, CBC, ZBC, flush, and invalidate use GF100 routines. Init consumes `ltc_nr` and `tag_base` calculated by GF100 oneinit and persists hardware tag/CBC configuration until reset.

## Dependencies and Integration Points
Depends on GF100 helpers and the common LTC base. It integrates with framebuffer compression tag setup.

## Risks and Test Signals
Risks are missed Kepler-specific count register programming and large-page mode mismatch. Test GK104 initialization, compressed surfaces, ZBC replay, cache flush, and comparing `ltc_nr` visibility in both programmed registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gm107.c

## Purpose
Implements Maxwell GM107 LTC register layout for CBC clear/wait, ZBC color/depth, interrupt handling, partition discovery, and init.

## Important APIs, Types, and Functions
Exports include `gm107_ltc_cbc_clear`, `gm107_ltc_cbc_wait`, `gm107_ltc_zbc_clear_color`, `gm107_ltc_zbc_clear_depth`, `gm107_ltc_intr_lts`, `gm107_ltc_intr`, and `gm107_ltc_new`.

## Control Flow, State, and Persistence
CBC operations use `0x17e26c/270/274` and per-slice wait registers under `0x14046c`. Interrupt handling reads master mask `0x00017c`, decodes each LTC/LTS status with the GF100 bitfield table, and acknowledges it. Oneinit counts partitions from `0x022438` minus mask `0x021c14`, gets slice count from `0x17e280`, and delegates tag RAM allocation to GF100. Init writes LTC count, tag base, and large-page mode.

## Dependencies and Integration Points
Integrates with GF100 tag RAM allocation, timer wait helpers, base.c ZBC replay, and Maxwell-family chip tables.

## Risks and Test Signals
Risks include incorrect mask register use, CBC waits that silently time out, and reused interrupt names missing Maxwell-specific meanings. Test GM107 compressed surfaces, partition-fused chips, ZBC replay, interrupt logs, and cache flush/invalidate reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gm200.c

## Purpose
Defines the GM200 LTC backend with direct LTC count discovery and minimal tag-base initialization.

## Important APIs, Types, and Functions
`gm200_ltc_oneinit` reads `ltc_nr` from `0x12006c`, `lts_nr` from `0x17e280`, then calls GF100 tag RAM setup. `gm200_ltc_init` writes `tag_base` to `0x17e278`. `gm200_ltc_new` registers the function table.

## Control Flow, State, and Persistence
GM200 reuses GM107 CBC/ZBC/interrupt paths and GF100 cache flush/invalidate. The only persistent local state is partition/slice counts and allocated tag RAM from oneinit.

## Dependencies and Integration Points
Depends on GF100 tag memory management and GM107 register helpers. It integrates with framebuffer compression and ZBC users.

## Risks and Test Signals
Risks include reading an incorrect LTC count register and relying on reused GM107 offsets. Test GM200 init, compression tag allocation, CBC clear/wait, ZBC replay, interrupt reporting, and tag base programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gp100.c

## Purpose
Provides Pascal GP100 LTC glue, using GP100 interrupt routing and leaving tag RAM setup to unresolved firmware/PMU paths.

## Important APIs, Types, and Functions
Exports are `gp100_ltc_intr`, `gp100_ltc_oneinit`, `gp100_ltc_init`, and `gp100_ltc_new`.

## Control Flow, State, and Persistence
Interrupt handling reads mask register `0x0001c0` and dispatches each set LTC to `gm107_ltc_intr_lts`. Oneinit reads `ltc_nr` and `lts_nr` but does not allocate tag RAM. Init is a stub with a TODO for a PMU low-security call to set tag RAM address.

## Dependencies and Integration Points
It reuses GM107 CBC/ZBC helpers and GF100 cache operations. It integrates with base.c but may have reduced compression-tag functionality because tag allocation is not implemented here.

## Risks and Test Signals
Risks are missing tag RAM configuration, no compression tags, and incorrect interrupt mask assumptions. Test GP100 init on real hardware, compressed-surface behavior, interrupt dispatch, and fallback behavior when compression is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gp102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gp102.c

## Purpose
Adds GP102 LTC support and stencil ZBC programming for non-GSP-RM Pascal devices.

## Important APIs, Types, and Functions
`gp102_ltc_zbc_clear_stencil` writes stencil clear values at selected ZBC index. `gp102_ltc_new` rejects GSP-RM devices and registers a GP100-derived function table with stencil support.

## Control Flow, State, and Persistence
The backend reuses GP100 oneinit/init/intr, GM107 CBC/color/depth, and GF100 flush/invalidate. Base.c persists stencil values in `ltc->zbc_stencil` and replays them through this callback on init.

## Dependencies and Integration Points
Depends on `subdev/gsp.h`, GP100 and GM107 helpers, and ZBC consumers.

## Risks and Test Signals
Risks include running under firmware-owned GSP RM, stencil register index mismatches, and inherited GP100 tag-RAM limitations. Test GP102 non-GSP initialization, stencil ZBC replay, depth/color compatibility, interrupt dispatch, and GSP-RM rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gp102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gp10b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gp10b.c

## Purpose
Implements Tegra GP10B LTC init differences, including LTC count programming and optional IOMMU stream ID setup.

## Important APIs, Types, and Functions
`gp10b_ltc_init` programs LTC count registers and writes `sid << 2` to `0x160000` when `tegra_dev_iommu_get_stream_id` succeeds. `gp10b_ltc_new` registers the backend.

## Control Flow, State, and Persistence
The table reuses GP100 oneinit/interrupt, GM107 CBC/color/depth, GP102 stencil, and GF100 cache operations. Init persists the Tegra stream ID and LTC count into hardware after base.c replays ZBC state.

## Dependencies and Integration Points
Depends on Tegra IOMMU helpers, GP100/GM107/GP102/GF100 common functions, and the public LTC base.

## Risks and Test Signals
Risks are stream-ID programming failure, SoC-specific register mismatch, and inherited missing tag RAM setup. Test Tegra GP10B boot, IOMMU DMA faults, ZBC replay, cache flush/invalidate, and interrupt dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/gp10b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/priv.h

## Purpose
Defines the private LTC backend contract and shared helper declarations for chip-specific cache/tag/ZBC implementations.

## Important APIs, Types, and Functions
`struct nvkm_ltc_func` declares oneinit/init/intr, CBC clear/wait, ZBC color/depth/stencil capacities and writers, and cache invalidate/flush hooks. The header declares GF100, GM107, GP100, and GP102 shared helpers used by later chip files.

## Control Flow, State, and Persistence
No executable flow is present. The function table determines which hardware paths base.c calls and controls persistent ZBC replay and tag clearing behavior.

## Dependencies and Integration Points
Includes public `subdev/ltc.h` and `core/enum.h`; consumed by all LTC implementation files.

## Risks and Test Signals
Risks are missing optional callbacks, incorrect capacity values, and helper signature drift. Build all chip variants and run ZBC/tag/interrupt paths to validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/Kbuild

## Purpose
Builds the Nouveau NVKM master-control subdevice and chip-specific MC backends.

## Important APIs, Types, and Functions
The fragment links `base.o` plus MC variants from NV04 through GA100, including G84/G98/GT215, Fermi/Kepler, Tegra, Pascal, and Ampere.

## Control Flow, State, and Persistence
No runtime flow exists. Object inclusion determines which constructors and shared reset/interrupt maps are available to device tables.

## Dependencies and Integration Points
Integrated by the parent NVKM Kbuild. It must match all MC constructors referenced by chipset discovery.

## Risks and Test Signals
Missing object entries cause unresolved symbols or absent hardware support. Kernel build matrices and module-load smoke tests on each generation are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/base.c

## Purpose
Provides common MC services for subdevice interrupt masking, reset/enable/disable, unknown register programming, and MC subdevice construction.

## Important APIs, Types, and Functions
Public helpers are `nvkm_mc_unk260`, `nvkm_mc_intr_mask`, `nvkm_mc_reset`, `nvkm_mc_disable`, `nvkm_mc_enable`, `nvkm_mc_enabled`, and `nvkm_mc_new_`. `nvkm_mc_reset_mask` selects reset bits from TOP metadata or static maps.

## Control Flow, State, and Persistence
Reset/enable paths look up the target subdevice, prefer `nvkm_top_reset`, and fall back to `mc->func->reset` entries while respecting `noauto`. Constructors install interrupt leaves through `nvkm_intr_add`, using one or two leaves depending on `intr_nonstall`. Init delegates to the chip hook.

## Dependencies and Integration Points
Depends on `core/option.h`, `subdev/top.h`, `nvkm_intr`, `nvkm_device_subdev`, and chip-specific `nvkm_mc_func` tables.

## Risks and Test Signals
Risks include stale reset masks, ignoring `noauto`, interrupt leaf misconfiguration, and null MC during early calls. Test subdevice reset/enable cycles, TOP-derived reset paths, interrupt block/allow through `nvkm_mc_intr_mask`, and all chip constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/g84.c

## Purpose
Defines G84 MC reset and interrupt routing for early Tesla GPUs with VP/BSP/CIPHER/MPEG engines.

## Important APIs, Types, and Functions
`g84_mc_reset`, `g84_mc_intrs`, `g84_mc`, and `g84_mc_new` are the key symbols.

## Control Flow, State, and Persistence
The static maps associate PMC enable bits with engines and interrupt bits with engine/subdev handlers. Runtime flow is handled by `base.c`, `nv50_mc_init`, and `nv04_mc_device`.

## Dependencies and Integration Points
Uses shared NV04 interrupt pending/rearm behavior and NV50-style init. It integrates with video, graphics, FIFO, display, FB, GPIO/I2C, timer, and bus subdevices.

## Risks and Test Signals
Risks are wrong bit assignments for legacy video engines and shared GPIO/I2C masks. Test interrupt dispatch for each engine, reset cycles, FIFO/GR recovery, and display/timer interrupts on G84 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/g98.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/g98.c

## Purpose
Defines G98 MC routing for renamed video/security engines: MSVLD, SEC, MSPDEC, and MSPPP.

## Important APIs, Types, and Functions
Key symbols are `g98_mc_reset`, `g98_mc_intrs`, the `g98_mc` function table, and `g98_mc_new`.

## Control Flow, State, and Persistence
The file is declarative. Base MC code consumes reset and interrupt tables; `nv50_mc_init` enables devices through register `0x000200`.

## Dependencies and Integration Points
It uses NV04 device enable functions and interrupt handling. The maps connect display, video engines, FB, bus, GPIO/I2C, and timer subdevices to MC bits.

## Risks and Test Signals
Risks are engine rename/bit mismatches and interrupt fanout collisions. Test video decode/SEC interrupts, reset of all engines, display/FIFO/GR interrupt delivery, and module init on G98-class boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/g98.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/ga100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/ga100.c

## Purpose
Implements a minimal GA100 MC backend for non-GSP-RM operation with newer device enable register handling.

## Important APIs, Types, and Functions
Important functions are `ga100_mc_device_disable`, `ga100_mc_device_enable`, `ga100_mc_device_enabled`, `ga100_mc_init`, and `ga100_mc_new`.

## Control Flow, State, and Persistence
Enable/disable mask register `0x000600` and read it twice for posting/order. Init writes all ones to both `0x000200` and `0x000600`. The function table does not install interrupt routing in this file. Constructor returns `-ENODEV` when GSP RM owns the device.

## Dependencies and Integration Points
Depends on `subdev/gsp.h`, common MC construction, and device reset/enable calls from other subdevices.

## Risks and Test Signals
Risks include missing interrupt table coverage, incorrect use under GSP RM, and ordering requirements around `0x000600`. Test non-GSP GA100 bring-up, enable/disable status checks, reset callers, and GSP-RM constructor rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/ga100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gf100.c

## Purpose
Defines Fermi MC reset, interrupt routing, non-stall interrupt support, and a helper for writing register `0x000260`.

## Important APIs, Types, and Functions
Key symbols are `gf100_mc_reset`, `gf100_mc_intrs`, `gf100_mc_unk260`, `gf100_mc`, and `gf100_mc_new`.

## Control Flow, State, and Persistence
Runtime behavior is table-driven through base.c. The function table uses `gt215_mc_intr` for allow/block support, marks interrupts as non-stall-capable, reuses `nv50_mc_init`, and maps engine/subdev interrupt bits including PRIVRING, LTC, PMU, FB, THERM, and copy engines.

## Dependencies and Integration Points
Depends on GT215 interrupt helpers, NV04 device enable operations, and MC reset users. `unk260` is exposed through `nvkm_mc_unk260`.

## Risks and Test Signals
Risks include wrong CE instance bits, PMU `noauto` reset misuse, and missing non-stall interrupt setup. Test GR/FIFO/CE/video resets, interrupt block/allow, LTC/FB/PMU interrupt delivery, and users of `nvkm_mc_unk260`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gk104.c

## Purpose
Provides Kepler GK104 MC routing with TOP interrupt aggregation and reduced reset map.

## Important APIs, Types, and Functions
Exports `gk104_mc_reset`, `gk104_mc_intrs`, and `gk104_mc_new`; the function table also uses `gf100_mc_unk260`.

## Control Flow, State, and Persistence
The reset map covers FIFO and PMU `noauto`. Interrupt data routes normal fixed bits and reserves TOP handling through a specific `0x00001000` entry plus a catch-all non-stall TOP mask. Base.c and `gt215_mc_intr` manage runtime flow.

## Dependencies and Integration Points
Depends on NV50 init, GT215 interrupt masks, NV04 device enable, TOP subdevice, and GF100 `unk260`.

## Risks and Test Signals
Risks are masking TOP catch-all interrupts incorrectly and too-narrow reset coverage. Test TOP-enumerated engine interrupts, FIFO reset, PMU handling, GPIO/I2C shared bits, and non-stall interrupt leaf behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gk20a.c

## Purpose
Defines the Tegra GK20A MC backend by reusing GK104 interrupt/reset maps with NV50 init.

## Important APIs, Types, and Functions
The key symbols are `gk20a_mc` and `gk20a_mc_new`.

## Control Flow, State, and Persistence
All runtime behavior is delegated: init to `nv50_mc_init`, interrupts to `gt215_mc_intr` and `gk104_mc_intrs`, device control to `nv04_mc_device`, and reset mapping to `gk104_mc_reset`.

## Dependencies and Integration Points
Depends on GK104 shared tables and Tegra device routing.

## Risks and Test Signals
Risks are assuming GK104 desktop masks match GK20A SoC routing and lacking `unk260`. Test Tegra GPU interrupts, FIFO reset, PMU/top interactions, suspend/resume, and SoC boot logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gp100.c

## Purpose
Defines Pascal GP100 MC interrupt routing and write-only allow/block interrupt mask operations for non-GSP-RM devices.

## Important APIs, Types, and Functions
Exports `gp100_mc_intrs` and `gp100_mc_intr`. Internal helpers are `gp100_mc_intr_allow`, `gp100_mc_intr_block`, `gp100_mc_intr_rearm`, and `gp100_mc_intr_unarm`; `gp100_mc_new` registers the backend.

## Control Flow, State, and Persistence
Allow writes masks to `0x000160 + leaf*4`; block writes to `0x000180 + leaf*4`. Rearm reapplies saved masks for every leaf, and unarm blocks all bits. The function table reuses NV50 init, NV04 device enable, and GK104 reset.

## Dependencies and Integration Points
Depends on GSP detection, shared NV04 pending reads, and GP100 fault/TOP/LTC/PMU/FB interrupt users.

## Risks and Test Signals
Risks include write-only mask sequencing, GSP-RM ownership conflicts, and incorrect fault-subdev routing. Test page-fault interrupts, TOP fanout, mask block/allow, FIFO/GR interrupt delivery, and GSP-RM constructor rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gp10b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gp10b.c

## Purpose
Implements the Tegra GP10B MC backend with SoC-specific init to bring units out of ELPG.

## Important APIs, Types, and Functions
`gp10b_mc_init` writes `0xffffffff` to `0x000200` and `0x00020c`. `gp10b_mc_new` registers a GP100-style interrupt table.

## Control Flow, State, and Persistence
The backend uses GP100 interrupt allow/block, GP100 interrupt data, NV04 device control, and GK104 reset map. Init persists all-device enable and ELPG-exit state in MC registers.

## Dependencies and Integration Points
Depends on Tegra power-management expectations, GP100 MC interrupt code, and common MC reset helpers.

## Risks and Test Signals
Risks are ELPG state mismatches, desktop reset maps on Tegra, and interrupt mask differences. Test GP10B boot/resume, ELPG transitions, GPU faults, FIFO interrupts, and reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gp10b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gt215.c

## Purpose
Defines GT215 MC reset/interrupt tables and adds per-leaf interrupt allow/block callbacks via mask registers.

## Important APIs, Types, and Functions
Key symbols are `gt215_mc_reset`, `gt215_mc_intrs`, exported `gt215_mc_intr`, and `gt215_mc_new`. Helpers `gt215_mc_intr_allow` and `gt215_mc_intr_block` update `0x000640 + leaf*4`.

## Control Flow, State, and Persistence
The exported interrupt function reuses NV04 pending/unarm/rearm and adds dynamic block/allow. The chip function table uses NV50 init, NV04 device control, and GT215-specific reset/interrupt maps.

## Dependencies and Integration Points
Connects display, CE, video engines, FB, GPIO/I2C, timer, thermal, PMU, and bus interrupts to NVKM handlers.

## Risks and Test Signals
Risks include the local function table referencing `nv04_mc_intr` instead of exported `gt215_mc_intr`, shared interrupt masks, and engine-bit mismatches. Test interrupt block/allow, CE/video reset, PMU/THERM delivery, and regression against GF100 users of `gt215_mc_intr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv04.c

## Purpose
Implements the baseline legacy MC backend for NV04: simple device enable bits, interrupt pending/arm handling, reset masks, and init.

## Important APIs, Types, and Functions
Exports include `nv04_mc_reset`, `nv04_mc_device`, `nv04_mc_intr_rearm`, `nv04_mc_intr_unarm`, `nv04_mc_intr_pending`, `nv04_mc_intr`, `nv04_mc_init`, and `nv04_mc_new`.

## Control Flow, State, and Persistence
Device enable/disable masks register `0x000200`, with a readback after enable. Interrupt pending reads leaf status from `0x000100 + leaf*4`; arm/unarm writes `0x000140 + leaf*4`. Init enables all devices and disables ROM access through `0x001850`.

## Dependencies and Integration Points
Provides shared device and interrupt helpers reused by many later MC generations. Routes display, GR, FIFO, BUS, and TIMER.

## Risks and Test Signals
Risks are broad all-device enables, ROM access side effects, and leaf-count assumptions. Test legacy boot, FIFO/GR interrupts, display/timer interrupts, reset of GR/FIFO, and helper reuse on later generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv11.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv11.c

## Purpose
Defines NV11 interrupt routing while reusing NV04 init, reset, and device control.

## Important APIs, Types, and Functions
Key symbols are `nv11_mc_intrs`, the `nv11_mc` function table, and `nv11_mc_new`.

## Control Flow, State, and Persistence
The file is declarative. Runtime init uses `nv04_mc_init`; interrupts use `nv04_mc_intr`; reset uses `nv04_mc_reset`.

## Dependencies and Integration Points
Routes display with `0x03010000`, GR, FIFO, BUS, and TIMER interrupts to NVKM subdevices.

## Risks and Test Signals
Risks are display interrupt mask differences from NV04 and inherited broad init behavior. Test NV11 display events, GR/FIFO interrupts, reset paths, and module initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv17.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv17.c

## Purpose
Adds NV17 MC routing with MPEG engine reset and interrupt support.

## Important APIs, Types, and Functions
Exports `nv17_mc_reset`, `nv17_mc_intrs`, and `nv17_mc_new`.

## Control Flow, State, and Persistence
Static maps add MPEG bit `0x00000002` for reset and `0x00000001` for interrupt dispatch. Runtime behavior is handled by NV04 init/device/interrupt helpers.

## Dependencies and Integration Points
Integrates with display, GR, FIFO, MPEG, BUS, and TIMER subdevices. Later NV44/NV50 variants reuse these maps.

## Risks and Test Signals
Risks include MPEG bit mismatch and reuse on later chips. Test MPEG engine reset/interrupt, display mask behavior, FIFO/GR interrupts, and NV44/NV50 consumers of exported maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv17.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv44.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv44.c

## Purpose
Implements NV44-specific MC init for PRAMIN/instance aperture setup while using NV17 routing.

## Important APIs, Types, and Functions
`nv44_mc_init` reads `0x10020c`, enables all devices, and programs `0x001700..0x00170c`. `nv44_mc_new` registers the backend.

## Control Flow, State, and Persistence
Init writes a four-register window setup derived from `tmp`, likely PRAMIN BAR window state. Interrupt and reset behavior reuse NV04/NV17 helpers.

## Dependencies and Integration Points
Depends on NV17 interrupt/reset maps and NV04 device control. It interacts with legacy instmem/MMU aperture assumptions.

## Risks and Test Signals
Risks are incorrect aperture values from `0x10020c`, broad all-device enable, and legacy window assumptions. Test NV44 boot, instmem access, display/GR/FIFO interrupts, MPEG reset, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv44.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv50.c

## Purpose
Defines the baseline NV50 MC init and interrupt routing for display, GR, FIFO, MPEG, FB, bus, GPIO/I2C, and timer.

## Important APIs, Types, and Functions
Important symbols are `nv50_mc_intrs`, `nv50_mc_init`, `nv50_mc`, and `nv50_mc_new`.

## Control Flow, State, and Persistence
Init writes all ones to `0x000200` to enable devices. Interrupt and reset handling use NV04/NV17 shared helpers and tables.

## Dependencies and Integration Points
Used directly by NV50 and reused by G84/G98/GT215/GF100-family MC tables as the common enable init.

## Risks and Test Signals
Risks include overbroad enabling, FB interrupt mask mismatch, and shared GPIO/I2C mask collisions. Test NV50 boot, FB and display interrupts, FIFO/GR recovery, MPEG reset, and later-generation reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/priv.h

## Purpose
Defines the private MC backend contract and shared declarations for reset maps, interrupt data, and device enable methods.

## Important APIs, Types, and Functions
`struct nvkm_mc_map` maps PMC bits to subdevice type/instance and optional `noauto`. `struct nvkm_mc_func` contains init, interrupt, device control, reset map, and `unk260` hooks. Shared exports cover NV04, NV17, GT215, GF100, GK104, and GP100 helpers.

## Control Flow, State, and Persistence
No executable flow. The function tables drive base.c reset, enable, interrupt registration, and special register programming.

## Dependencies and Integration Points
Includes public `subdev/mc.h` and is consumed by all MC backends. It links MC to the generic `nvkm_intr` framework.

## Risks and Test Signals
Risks are signature drift, incorrectly marked `noauto`, and function tables missing mandatory device callbacks. Build every chip backend and test reset/interrupt paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/Kbuild

## Purpose
Builds the Nouveau NVKM MMU core, chip-specific MMU descriptors, memory object implementations, VMM backends, and user object wrappers.

## Important APIs, Types, and Functions
The build list covers `base.o`, chip MMU files from NV04 through GH100, memory implementations `mem*.o`, VMM implementations `vmm*.o`, and user ABI wrappers `umem.o`, `ummu.o`, `uvmm.o`.

## Control Flow, State, and Persistence
No runtime flow exists. The object list determines available MMU constructors, VMM page-table layouts, and user-space NVIF classes.

## Dependencies and Integration Points
Integrated by parent NVKM Kbuild and must match constructor references in device tables and symbols declared in `mem.h`, `vmm.h`, and `priv.h`.

## Risks and Test Signals
Missing entries cause unresolved symbols or disabled GPU families. Signals include full Nouveau kernel builds, module load, user memory allocation, and VMM creation on each generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/base.c

## Purpose
Implements common MMU subdevice construction, memory-type enumeration, global VMM creation, and page-table allocation caching/suballocation.

## Important APIs, Types, and Functions
Important symbols are `nvkm_mmu_ctor`, `nvkm_mmu_new_`, `nvkm_mmu_ptc_get`, `nvkm_mmu_ptc_put`, `nvkm_mmu_ptc_dump`, `nvkm_mmu_oneinit`, `nvkm_mmu_init`, and helpers for host/VRAM heap/type enumeration. Internal `nvkm_mmu_ptc` caches whole page tables; `nvkm_mmu_ptp` suballocates small page tables from a parent allocation.

## Control Flow, State, and Persistence
PT allocation first handles sub-page-table requests when alignment is below 4 KiB, otherwise reuses cached tables by size or allocates `NVKM_MEM_TARGET_INST` memory. Put either returns tables to a small cache or frees them, and recursively destroys empty PTP parents. Oneinit builds `mmu->heap[]` and `mmu->type[]` from FB VRAM heaps, BAR mapping properties, coherency, and kind support, then optionally creates a global GART VMM.

## Dependencies and Integration Points
Depends on instmem memory allocation, BAR, FB RAM heaps, `nvkm_vmm_new`, public NVIF MMU classes, and user MMU object construction.

## Risks and Test Signals
Risks include PT cache leaks, suballocation mask overflow, stale non-zero PTE reuse, incorrect memory type ordering, and BAR/coherency misclassification. Test VMM creation/destruction stress, raw/managed VMMs, VRAM absent systems, BAR1 uncached systems, suspend teardown, and page-table cache debug dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/g84.c

## Purpose
Defines the G84 MMU descriptor using NV50 memory/VMM classes with a smaller PD offset than base NV50.

## Important APIs, Types, and Functions
`g84_mmu` selects 40-bit DMA, NV50 user MMU/MEM/VMM classes, `nv50_mem_new`, `nv50_mem_map`, `nv50_vmm_new`, `nv50_mmu_kind`, and `kind_sys=true`. `g84_mmu_new` registers it.

## Control Flow, State, and Persistence
This is table-driven; base.c consumes the descriptor to expose types and construct VMMs. The VMM PD offset is `0x0200`.

## Dependencies and Integration Points
Depends on NV50 memory and VMM implementations and NVIF class IDs.

## Risks and Test Signals
Risks are wrong PD offset and system-memory kind handling. Test G84 VMM creation, BAR1 mapping, system/VRAM allocations, and user NVIF class probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gf100.c

## Purpose
Defines Fermi MMU capabilities and the GF100 compression-kind translation table.

## Important APIs, Types, and Functions
`gf100_mmu_kind` returns a 256-entry storage-kind map and invalid marker `0xff`. `gf100_mmu` selects 40-bit DMA, GF100 NVIF classes, `gf100_mem_new`, `gf100_mem_map`, `gf100_vmm_new`, and `kind_sys=true`.

## Control Flow, State, and Persistence
No dynamic flow beyond constructor registration. The kind table persists as static data and is exposed through user MMU kind queries and memory type construction.

## Dependencies and Integration Points
Depends on GF100 memory and VMM backends and NVIF class definitions. Used by GK104/GK20A derivatives.

## Risks and Test Signals
Risks include incorrect compressed-to-uncompressed kind mapping and invalid marker mismatches. Test kind queries, compressed VRAM allocations, GF100 VMM mapping, BAR1 user mapping, and user-space class negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gh100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gh100.c

## Purpose
Defines the GH100 MMU descriptor for R535/GSP-managed Hopper hardware with 52-bit DMA and GH100 VMM layout.

## Important APIs, Types, and Functions
`gh100_mmu` selects GF100 memory/user classes, `gf100_mem_new`, `gf100_mem_map`, `gh100_vmm_new`, `tu102_mmu_kind`, and `kind_sys=true`. `gh100_mmu_new` always delegates to `r535_mmu_new`.

## Control Flow, State, and Persistence
The file is descriptor-only; firmware integration owns construction through R535 glue.

## Dependencies and Integration Points
Depends on R535 MMU support, GH100 VMM implementation, TU102 kind table, and GF100 memory mapping ABI.

## Risks and Test Signals
Risks are 52-bit address handling, kind-table reuse, and firmware/user class mismatch. Test GSP/R535 MMU creation, high-address mappings, user memory allocation, and VMM operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gh100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gk104.c

## Purpose
Defines Kepler GK104 MMU capabilities using GF100 memory classes with a GK104 VMM backend.

## Important APIs, Types, and Functions
`gk104_mmu` selects 40-bit DMA, GF100 NVIF MMU/MEM/VMM classes, `gf100_mem_new`, `gf100_mem_map`, `gk104_vmm_new`, `gf100_mmu_kind`, and `kind_sys=true`. `gk104_mmu_new` registers it.

## Control Flow, State, and Persistence
Descriptor-only; base.c creates memory types and VMMs from the table.

## Dependencies and Integration Points
Depends on GF100 memory code, GK104 VMM implementation, and GF100 kind table.

## Risks and Test Signals
Risks include VMM class/layout mismatch and inherited kind table incompatibility. Test GK104 VMM creation, compressed mappings, BAR1 user maps, and system-memory mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gk20a.c

## Purpose
Defines Tegra GK20A MMU capabilities, using GF100 VMM semantics but no VRAM allocation constructor.

## Important APIs, Types, and Functions
`gk20a_mmu` selects 40-bit DMA, GF100 classes, `.mem.umap = gf100_mem_map`, `gk20a_vmm_new`, `gf100_mmu_kind`, and `kind_sys=true`. `gk20a_mmu_new` registers it.

## Control Flow, State, and Persistence
Descriptor-only. Host/SoC memory allocation is expected outside the VRAM path; user mapping uses the GF100 mapping hook.

## Dependencies and Integration Points
Depends on GK20A VMM, GF100 map validation, and Tegra memory integration.

## Risks and Test Signals
Risks include absent `mem.vram` path, SoC aperture differences, and kind-table assumptions. Test Tegra memory handles, VMM mappings, IOMMU interaction, and user BAR mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gm200.c

## Purpose
Defines Maxwell GM200 MMU support, including an updated 256-entry kind table and a fixed-layout VMM fallback when the framebuffer advertises a fixed page mode.

## Important APIs, Types, and Functions
`gm200_mmu_kind` returns the kind map with invalid `0xff`. `gm200_mmu` uses `gm200_vmm_new`; `gm200_mmu_fixed` uses `gm200_vmm_new_fixed`; `gm200_mmu_new` selects based on `device->fb->page`.

## Control Flow, State, and Persistence
Construction is conditional: fixed page mode forces the fixed VMM class version. The kind table persists as static data for user kind queries and memory type setup.

## Dependencies and Integration Points
Depends on FB page-mode state, GF100 memory code, GM200 VMM implementations, and NVIF classes.

## Risks and Test Signals
Risks include selecting the wrong fixed/non-fixed VMM, kind-table incompatibility, and compression behavior changes. Test GM200 normal and fixed-page boards, kind queries, compressed allocations, VMM map/unmap, and BAR1 mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gm20b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gm20b.c

## Purpose
Defines Tegra GM20B MMU descriptors with GM200-style VMMs and external/host memory mapping.

## Important APIs, Types, and Functions
`gm20b_mmu` uses `gm20b_vmm_new`; `gm20b_mmu_fixed` uses `gm20b_vmm_new_fixed`; both expose only `.mem.umap = gf100_mem_map`, use `gm200_mmu_kind`, and set 40-bit DMA. `gm20b_mmu_new` selects fixed mode from `device->fb->page`.

## Control Flow, State, and Persistence
Descriptor selection mirrors GM200 but omits a VRAM allocator constructor. Base.c handles user type enumeration and VMM construction.

## Dependencies and Integration Points
Depends on Tegra memory, GF100 map code, GM20B VMM backends, and FB page-mode state.

## Risks and Test Signals
Risks include wrong fixed-mode selection, missing VRAM allocation path, and SoC aperture differences. Test GM20B user memory handles, VMM maps, IOMMU faults, fixed-page mode, and kind queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gm20b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gp100.c

## Purpose
Defines GP100 MMU support with 47-bit DMA and optional fallback to GM200 layout via a configuration option.

## Important APIs, Types, and Functions
`gp100_mmu` selects GF100 memory classes, `gp100_vmm_new`, `gm200_mmu_kind`, and `kind_sys=true`. `gp100_mmu_new` checks `GP100MmuLayout`; when false it calls `gm200_mmu_new`.

## Control Flow, State, and Persistence
Construction is configuration-dependent. The VMM layout choice persists for the lifetime of the MMU and controls all user VMMs.

## Dependencies and Integration Points
Depends on `core/option.h`, GF100 memory code, GP100 VMM implementation, and GM200 fallback.

## Risks and Test Signals
Risks include incompatible layout option use, address-width mistakes, and kind-table reuse. Test both option settings, 47-bit mappings, compressed allocations, user VMM creation, and fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gp10b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gp10b.c

## Purpose
Defines Tegra GP10B MMU support with GP100-style 47-bit VMM layout or GM20B fallback.

## Important APIs, Types, and Functions
`gp10b_mmu` uses `.mem.umap = gf100_mem_map`, `gp10b_vmm_new`, and `gm200_mmu_kind`. `gp10b_mmu_new` checks `GP100MmuLayout`; false selects `gm20b_mmu_new`.

## Control Flow, State, and Persistence
Descriptor selection is config-driven and persists for all VMMs created under this MMU. VRAM allocation is not exposed through `.mem.vram`.

## Dependencies and Integration Points
Depends on core options, Tegra memory, GP10B VMM implementation, GM20B fallback, and GF100 mapping validation.

## Risks and Test Signals
Risks include wrong layout on SoC firmware, absent VRAM allocation path, and high address-width issues. Test both layout options, Tegra mappings, IOMMU behavior, raw VMM operations, and user class negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gp10b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gv100.c

## Purpose
Defines Volta GV100 MMU capabilities with 47-bit DMA and GV100 VMM backend.

## Important APIs, Types, and Functions
`gv100_mmu` selects GF100 memory classes, `gf100_mem_new`, `gf100_mem_map`, `gv100_vmm_new`, `gm200_mmu_kind`, and `kind_sys=true`. `gv100_mmu_new` registers it.

## Control Flow, State, and Persistence
Descriptor-only; base.c provides memory types and constructs VMMs from the table.

## Dependencies and Integration Points
Depends on GF100 memory code, GV100 VMM implementation, GM200 kind table, and NVIF classes.

## Risks and Test Signals
Risks are kind-table reuse and 47-bit address handling. Test GV100 user VMM creation, high-address maps, compression kinds, BAR1 mapping, and user MMU kind queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/mcp77.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/mcp77.c

## Purpose
Defines MCP77 integrated-chipset MMU capabilities using NV50 memory classes with a dedicated VMM constructor and NV50-style PD offset.

## Important APIs, Types, and Functions
`mcp77_mmu` selects 40-bit DMA, NV50 NVIF classes, `nv50_mem_new`, `nv50_mem_map`, `mcp77_vmm_new`, `nv50_mmu_kind`, and `kind_sys=true`. `mcp77_mmu_new` registers it.

## Control Flow, State, and Persistence
Descriptor-only. Base.c turns this into memory types and VMM construction.

## Dependencies and Integration Points
Depends on NV50 memory/kind code and MCP77 VMM layout.

## Risks and Test Signals
Risks include integrated-chipset aperture differences and PD offset mismatch. Test MCP77 user VMM creation, host memory mappings, BAR1 behavior, and kind queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/mcp77.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/mem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/mem.c

## Purpose
Implements common host/system memory objects for the MMU and dispatches memory allocation requests to either VRAM backends or host-page allocation.

## Important APIs, Types, and Functions
Key symbols are `nvkm_mem_new_type`, `nvkm_mem_map_host`, `nvkm_mem_new_host`, `nvkm_mem_map_dma`, `nvkm_mem_map_sgl`, and the `nvkm_mem_dma`/`nvkm_mem_sgl` memory function tables. `struct nvkm_mem` stores target, MMU pointer, page count, pages, and DMA or SGL backing.

## Control Flow, State, and Persistence
Host memory creation either wraps caller-provided DMA/SGL arrays from NVIF arguments or allocates zeroed pages, maps them for DMA, and records per-page DMA addresses. Target is coherent HOST only when the selected type is coherent and not uncached; otherwise NCOH. Destruction unmaps DMA and frees pages. `nvkm_mem_new_type` delegates VRAM requests to `mmu->func->mem.vram`.

## Dependencies and Integration Points
Depends on DMA mapping API, `vmap`, NVIF memory argument unpacking, `nvkm_vmm_map`, and chip-specific VRAM allocation functions.

## Risks and Test Signals
Risks include partial allocation leaks on mid-loop failures, DMA mask/GFP mismatch, incorrect coherent/NCOH target selection, and unsafe user-provided arrays. Test host allocation/free under fault injection, DMA mapping errors, host `vmap`, SGL wrapping, VMM mapping, and 32-bit DMA devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/mem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/mem.h

## Purpose
Declares MMU memory allocation and BAR/user mapping helpers shared by generic, NV04, NV50, and GF100 memory implementations.

## Important APIs, Types, and Functions
Declarations include `nvkm_mem_new_type`, `nvkm_mem_map_host`, `nv04_mem_new/map`, `nv50_mem_new/map`, and `gf100_mem_new/map`.

## Control Flow, State, and Persistence
No executable flow. The prototypes define the contract used by `nvkm_mmu_func.mem` descriptors and user memory objects.

## Dependencies and Integration Points
Includes `priv.h` and is consumed by MMU chip descriptors, `umem.c`, and VMM mapping paths.

## Risks and Test Signals
Risks are signature drift and inconsistent argument ABI handling across generations. Build all MMU variants and test user memory allocation/map classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/memgf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/memgf100.c

## Purpose
Implements GF100+ VRAM memory allocation and BAR1 user mapping with GF100 VMM map arguments.

## Important APIs, Types, and Functions
`gf100_mem_new` parses `gf100_mem_v0/vn`, selects contiguous allocation, chooses NORMAL VRAM for display/compression types or MIXED otherwise, and calls `nvkm_ram_get`. `gf100_mem_map` creates a BAR1 VMA, maps memory with `gf100_vmm_map_v0`, and returns IO handle/size.

## Control Flow, State, and Persistence
Mapping validates map args, allocates BAR1 space using the memory page size, maps through `nvkm_memory_map`, then returns BAR1 physical resource plus VMA offset. Allocations persist as `nvkm_memory` returned by the framebuffer RAM allocator.

## Dependencies and Integration Points
Depends on BAR1 VMM, FB RAM allocator, GF100 VMM mapping validation, and NVIF memory/map ABI.

## Risks and Test Signals
Risks include BAR1 VMA leaks on map failure, incorrect MIXED/NORMAL heap selection, kind/RO validation errors, and page-size mismatch. Test VRAM allocation flags, BAR1 mapping/unmapping, compressed/display allocations, contiguous allocation failure, and map argument validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/memgf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/memnv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/memnv04.c

## Purpose
Implements legacy NV04 VRAM allocation and direct BAR1 mapping.

## Important APIs, Types, and Functions
`nv04_mem_new` parses legacy NVIF args, chooses NORMAL or NOMAP VRAM heap based on mappability, and calls `nvkm_ram_get`. `nv04_mem_map` returns BAR1 framebuffer resource address plus `nvkm_memory_addr`.

## Control Flow, State, and Persistence
Mapping does not allocate a VMA; it returns `ERR_PTR(-ENODEV)` for `pvma`, indicating direct fixed BAR1 access. Allocation persists as framebuffer RAM memory.

## Dependencies and Integration Points
Depends on device BAR1 resource callbacks, FB RAM allocator, and NV04 memory/VMM classes.

## Risks and Test Signals
Risks include direct BAR1 address assumptions, NOMAP heap mistakes, and no VMA cleanup path. Test legacy VRAM allocation, user mapping, BAR1 resource size/offset, AGP/PCI variants, and unmappable memory rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/memnv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/memnv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/memnv50.c

## Purpose
Implements NV50 VRAM allocation and BAR1 mapping with NV50-specific bank-swizzle, contiguity, kind, and compression arguments.

## Important APIs, Types, and Functions
`nv50_mem_new` parses `nv50_mem_v0/vn`, selects storage type `0x01` or `0x02`, and calls `nvkm_ram_get`. `nv50_mem_map` parses `nv50_mem_map_v0/vn`, allocates BAR1 space, maps memory with `nv50_vmm_map_v0`, and returns IO address/size.

## Control Flow, State, and Persistence
Mapping gets a 4 KiB-aligned BAR1 VMA sized to memory, returns BAR1 resource base plus VMA address, then calls `nvkm_memory_map`. Allocation persists as RAM allocator memory.

## Dependencies and Integration Points
Depends on BAR1 VMM, FB RAM allocator, NV50 VMM map validation, bank-swizzle-aware VRAM kinds, and NVIF ABI.

## Risks and Test Signals
Risks include BAR1 VMA leaks on `nvkm_memory_map` failure, bank-swizzle misallocation, compression argument mismatch, and contiguous allocation failure. Test bank-swizzled allocations, BAR1 maps/unmaps, compressed mappings, and map error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/memnv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/nv04.c

## Purpose
Defines the baseline NV04 MMU descriptor with 32-bit DMA, legacy memory class, and global VMM support.

## Important APIs, Types, and Functions
Exports `nv04_mmu` and `nv04_mmu_new`. The descriptor uses `nv04_mem_new`, `nv04_mem_map`, `nv04_vmm_new`, and NV04 NVIF classes.

## Control Flow, State, and Persistence
Descriptor-only. `vmm.global=true` causes base.c to create a global GART VMM during oneinit.

## Dependencies and Integration Points
Depends on NV04 memory and VMM implementations and public NVIF classes.

## Risks and Test Signals
Risks include 32-bit DMA limitations and global VMM assumptions. Test NV04 memory allocation, global GART VMM creation, BAR1 mapping, and legacy user class probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/nv41.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/nv41.c

## Purpose
Adds NV41 PCIe MMU support with 39-bit DMA and initialization of the global page directory, while falling back to NV04 for AGP or disabled PCIe.

## Important APIs, Types, and Functions
`nv41_mmu_init` writes the global VMM page directory address to `0x100800`, enables `0x10008c`, and clears `0x100820`. `nv41_mmu_new` selects NV04 fallback or the NV41 descriptor.

## Control Flow, State, and Persistence
Constructor checks device type and `NvPCIE` option. Init persists MMU root pointer and enable bits in hardware after global VMM creation.

## Dependencies and Integration Points
Depends on core options, NV04 memory class, NV41 VMM layout, and `mmu->vmm->pd`.

## Risks and Test Signals
Risks include wrong AGP/PCIe fallback, page-directory address truncation, and init ordering before VMM exists. Test NV41 PCIe and AGP paths, global GART mappings, option override, and suspend/resume reinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/nv41.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/nv44.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/nv44.c

## Purpose
Implements NV44 PCIe MMU initialization, including PRAMIN-relative page-table address programming and null PTE setup.

## Important APIs, Types, and Functions
`nv44_mmu_init` computes a page-table base from `0x10020c` and the VMM PD memory address, then writes `0x100850`, `0x100818`, `0x100804`, `0x10008c`, `0x100820`, `0x10082c`, and `0x100800`. `nv44_mmu_new` selects NV04 fallback for AGP or disabled PCIe.

## Control Flow, State, and Persistence
Init assumes the PD object is 512 KiB aligned and fits inside a 512 KiB PRAMIN block. It persists null page and page-table sizing registers for the global VMM.

## Dependencies and Integration Points
Depends on NV04 memory class, NV44 VMM layout, device config option `NvPCIE`, and instmem/PRAMIN layout.

## Risks and Test Signals
Risks include PRAMIN address calculation errors, alignment assumptions, and fallback misselection. Test NV44 PCIe boot, AGP fallback, global GART mappings, null page faults, and resume reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/nv44.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/nv50.c

## Purpose
Defines NV50 MMU capabilities and the NV50 storage-kind table used to distinguish bank-swizzled and non-swizzled VRAM kinds.

## Important APIs, Types, and Functions
`nv50_mmu_kind` returns a 128-entry kind table with invalid marker `0x7f`. `nv50_mmu` selects 40-bit DMA, NV50 memory/VMM classes, `nv50_mem_new`, `nv50_mem_map`, `nv50_vmm_new`, and PD offset `0x1400`. `nv50_mmu_new` registers it.

## Control Flow, State, and Persistence
Descriptor-only. The kind table is static and exposed through user MMU queries and memory type setup.

## Dependencies and Integration Points
Depends on NV50 memory and VMM backends and NVIF classes.

## Risks and Test Signals
Risks include bank-swizzle kind errors, invalid marker mismatch, and PD offset mismatch. Test kind queries, VRAM allocations with bank swizzle, BAR1 mappings, and NV50 VMM creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/priv.h

## Purpose
Defines the private MMU backend contract, constructors, kind-table exports, and page-table allocation structures.

## Important APIs, Types, and Functions
`struct nvkm_mmu_func` groups lifecycle hooks, DMA width, user classes, memory allocation/mapping hooks, VMM constructor/global settings, kind table callback, system-kind support, and optional VMM promotion. `struct nvkm_mmu_pt` tracks cached/suballocated page-table memory. The header declares R535, base constructors, kind callbacks, and PTC helpers.

## Control Flow, State, and Persistence
No executable flow. The descriptor selected by a chip file determines MMU behavior for all memory and VMM objects. `nvkm_mmu_pt` state persists while VMMs reference page tables.

## Dependencies and Integration Points
Includes public `subdev/mmu.h`; consumed by MMU descriptors, base.c, memory code, VMM code, and R535 glue.

## Risks and Test Signals
Risks include incomplete function tables, wrong DMA bit widths, and page-table cache contract changes. Build all MMU variants and test memory allocation, VMM creation, page-table allocation/free, and R535 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/tu102.c

## Purpose
Defines Turing TU102 MMU support and the compact storage-kind table used by Turing/Ampere/Hopper-style layouts.

## Important APIs, Types, and Functions
`tu102_mmu_kind` returns a 16-entry kind table with invalid marker `0x07`. `tu102_mmu` selects 47-bit DMA, GF100 memory classes, `tu102_vmm_new`, and `kind_sys=true`. `tu102_mmu_new` delegates to `r535_mmu_new` when GSP RM is active.

## Control Flow, State, and Persistence
Construction is GSP-dependent. The selected VMM and firmware path persist for all user VMMs under the MMU.

## Dependencies and Integration Points
Depends on GSP detection, R535 MMU glue, GF100 memory code, TU102 VMM, and NVIF classes.

## Risks and Test Signals
Risks include wrong firmware/native split, compact kind-table invalid marker errors, and 47-bit mapping bugs. Test TU102 native and GSP paths, kind queries, high-address mappings, BAR1 maps, and compression behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/umem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/umem.c

## Purpose
Implements the user-visible NVIF memory object that allocates MMU memory, maps it to CPU or BAR1 IO, unmaps it, and lets VMM objects look it up by handle.

## Important APIs, Types, and Functions
Key symbols are `nvkm_umem_new`, `nvkm_umem_search`, `nvkm_umem_map`, `nvkm_umem_unmap`, and `nvkm_umem_dtor`. The object function table exposes map/unmap/dtor.

## Control Flow, State, and Persistence
Creation validates a user type index, records the resolved memory type flags, forces mappable memory to at least PAGE_SHIFT, allocates memory through `nvkm_mem_new_type`, links the object into the client `umem` list, and returns page/address/size. Map supports host `vmap` for host memory without extra args or BAR1 IO mapping for VRAM/kind memory. Unmap releases BAR1 VMA or CPU vmap. Search can find memory in the local client or the master client list.

## Dependencies and Integration Points
Depends on `ummu`, `nvkm_mem_new_type`, BAR1 VMM, client object lookup, NVIF memory ABI, and VMM mapping code.

## Risks and Test Signals
Risks include stale client list entries, map/unmap state confusion, master-client handle exposure, BAR1 VMA leaks, and host map lifetime issues. Test user memory allocation, cross-client lookup rules, repeated map/unmap errors, host vmap, VRAM BAR1 map, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/umem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/umem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/umem.h

## Purpose
Declares the private user memory object structure and constructor.

## Important APIs, Types, and Functions
`struct nvkm_umem` embeds `nvkm_object`, stores MMU pointer, type flags, `mappable`/`io` state, backing `nvkm_memory`, client list node, and either BAR VMA or CPU map pointer. `nvkm_umem_new` is declared for user class construction.

## Control Flow, State, and Persistence
No executable flow. The structure persists user object map state and backing memory until object destruction.

## Dependencies and Integration Points
Includes `core/object.h` and `mem.h`; consumed by `umem.c`, `ummu.c`, and `uvmm.c`.

## Risks and Test Signals
Risks are union misuse between BAR and CPU mappings and stale list state. Build coverage plus user memory map/unmap/destruction tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/umem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/ummu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/ummu.c

## Purpose
Implements the user-visible MMU object that reports memory heaps/types/kinds and exposes memory/VMM child classes.

## Important APIs, Types, and Functions
Important symbols are `nvkm_ummu_new`, `nvkm_ummu_sclass`, `nvkm_ummu_heap`, `nvkm_ummu_type`, `nvkm_ummu_kind`, and `nvkm_ummu_mthd`.

## Control Flow, State, and Persistence
Creation unpacks the MMU object request and returns DMA bits plus heap/type/kind counts. Method dispatch handles heap-size queries, type flag queries, and kind table copies. Subclass enumeration exposes a user memory class when available and a user VMM class when available.

## Dependencies and Integration Points
Depends on `umem`, `uvmm`, NVIF MMU ABI, `nvkm_mmu` heap/type arrays, and kind callbacks.

## Risks and Test Signals
Risks include out-of-range index handling, copying an absent kind table, stale class descriptors, and ABI version mismatch. Test NVIF heap/type/kind queries, child class enumeration, no-kind devices, and invalid user arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/ummu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/ummu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/ummu.h

## Purpose
Declares the private user MMU object wrapper.

## Important APIs, Types, and Functions
`struct nvkm_ummu` embeds `nvkm_object` and points to the owning `nvkm_mmu`. `nvkm_ummu_new` constructs the object from a device and object class.

## Control Flow, State, and Persistence
No executable flow. The object pointer persists to route user methods and child-object constructors to the correct MMU.

## Dependencies and Integration Points
Includes `core/object.h` and `priv.h`; consumed by user memory and user VMM wrappers.

## Risks and Test Signals
Risks are stale MMU pointers and constructor signature drift. Build and NVIF MMU object creation tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/ummu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/uvmm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/uvmm.c

## Purpose
Implements the user-visible VMM object for address-space allocation, mapping user memory, PFN map/clear, raw managed-range operations, backend-specific methods, and VMM lookup by handle.

## Important APIs, Types, and Functions
Key symbols are `nvkm_uvmm_new`, `nvkm_uvmm_search`, `nvkm_uvmm_mthd_get`, `put`, `map`, `unmap`, `pfnmap`, `pfnclr`, `page`, and raw helpers `raw_get`, `raw_put`, `raw_map`, `raw_unmap`, `raw_sparse`.

## Control Flow, State, and Persistence
Creation either constructs a per-user VMM through the chip VMM constructor or references the global MMU VMM, then optionally promotes it and reports page count/address/size. Standard methods lock `vmm->mutex.vmm`, validate managed raw restrictions, split VMAs when needed, mark VMAs busy during asynchronous map work, and use `nvkm_umem_search` to bind memory handles. Raw methods operate only inside managed ranges and require `vmm->managed.raw`.

## Dependencies and Integration Points
Depends on `umem`, `ummu`, `nvkm_vmm_*` core APIs, NVIF VMM ABI, client objects, and chip-specific VMM method hooks.

## Risks and Test Signals
Risks include VMA busy-state leaks on map failure, managed/raw range bypass, handle lifetime races, split/merge bugs, PFN array size validation, and global VMM size misuse. Test get/put/map/unmap sequences, raw managed VMM operations, PFN mapping with invalid entries, backend methods, concurrent maps, and object destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/uvmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/uvmm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/uvmm.h

## Purpose
Declares the private user VMM object structure and constructor.

## Important APIs, Types, and Functions
`struct nvkm_uvmm` embeds `nvkm_object` and owns a referenced `nvkm_vmm`. `nvkm_uvmm_new` is declared for user VMM class construction.

## Control Flow, State, and Persistence
No executable flow. The referenced VMM persists until object destruction and is used by all VMM user methods.

## Dependencies and Integration Points
Includes `core/object.h` and `vmm.h`; consumed by `uvmm.c` and `ummu.c`.

## Risks and Test Signals
Risks are VMM reference leaks or premature unrefs. Build coverage and user VMM create/destroy stress validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/uvmm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmm.c

## Purpose
Implements the common virtual memory manager: VMA allocation/free, page-table reference counting, sparse mappings, raw/PFN mappings, memory map/unmap, page-table bootstrapping, VMM construction/destruction, and reference lifetime.

## Important APIs, Types, and Functions
Important APIs include `nvkm_vmm_new`, `nvkm_vmm_new_`, `nvkm_vmm_get_locked`, `nvkm_vmm_get`, `nvkm_vmm_put_locked`, `nvkm_vmm_put`, `nvkm_vmm_map`, `nvkm_vmm_unmap`, `nvkm_vmm_unmap_locked`, `nvkm_vmm_pfn_map`, `nvkm_vmm_pfn_unmap`, `nvkm_vmm_raw_get/put/unmap/sparse`, `nvkm_vmm_boot`, `nvkm_vmm_join/part`, `nvkm_vmm_ref`, and `nvkm_vmm_unref`.

## Control Flow, State, and Persistence
The core walk engine `nvkm_vmm_iter` deconstructs virtual addresses into per-level PTE indices, allocates software/hardware page tables on demand, applies PTE map/clear callbacks, tracks flush depth, and unwinds partial failures. VMA state is stored in a list plus RB trees for address lookup and size-ordered free lookup. Allocation splits free VMAs, optionally preallocates PTEs or sparse PTEs, and records page/ref state. Put unmaps memory, drops PTE references, merges split regions, and returns space to the free tree.

## Dependencies and Integration Points
Depends on `vmm.h` backend descriptors, MMU page-table cache, `nvkm_memory` mapping/tag APIs, FB tag handling, R535 vaspace deletion, and chip-specific flush/join/part/valid callbacks.

## Risks and Test Signals
Risks include page-table reference leaks, dual large/small page transition errors, sparse state corruption, VMA split/merge bugs, PFN DMA unmap ordering, flush-depth mistakes, raw managed-range misuse, and destructor cleanup of bootstrapped VMMs. Test VMM allocation fragmentation, sparse get/put, mixed page sizes, map replacement, PFN map/unmap, raw managed VMM operations, bootstrapped BAR VMMs, concurrent map/ref locks, and fault injection in page-table allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmm.h

## Purpose
Defines the private VMM data structures, backend descriptor contracts, public internal VMM APIs, PFN encoding, page-size flags, and PTE write helper macros.

## Important APIs, Types, and Functions
Important types are `union nvkm_pte_tracker`, `struct nvkm_vmm_pt`, `struct nvkm_vmm_desc_func`, `struct nvkm_vmm_desc`, `struct nvkm_vmm_page`, `struct nvkm_vmm_func`, and `struct nvkm_vmm_join`. The header declares all common VMM operations and chip-specific constructors from NV04 through GH100.

## Control Flow, State, and Persistence
The header has inline range validation through `nvkm_vmm_in_managed_range` and macro-based PTE iteration/write helpers. Persistent VMM state defined here includes page directory tracking, dual-page-table refcounts, sparse PDE/PTE markers, backend page layouts, and joined instance-memory lists.

## Dependencies and Integration Points
Includes MMU private definitions and `core/memory.h`; consumed by common VMM code, chip-specific VMM implementations, user VMM code, and memory mapping code.

## Risks and Test Signals
Risks include macro side effects, PFN bit encoding drift, descriptor/layout mismatches, and incorrect managed-range checks on overflow. Build all VMM backends, run sparse/PFN/dual-page-size tests, and enable MMU debug tracing for page-table transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmm.h -->
