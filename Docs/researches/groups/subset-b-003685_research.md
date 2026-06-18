# subset-b-003685 research

Grouped research for nouveau NVKM fault-buffer and framebuffer/RAM files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/`. Each source file section preserves the source path in its title and is delimited for deterministic splitting into the mapped source-tree-aligned research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/priv.h

## Purpose
Private interface for the NVKM fault subdevice. It defines replayable fault buffer objects, the generation-specific fault function table, and prototypes shared by GP100/GV100/TU102 implementations and the user object wrapper.

## Important APIs, Types, And Functions
`struct nvkm_fault_buffer` binds an NVKM object to a hardware fault buffer, cached get/put MMIO offsets, backing `nvkm_memory`, BAR address, and interrupt handle. `struct nvkm_fault_func` supplies subdevice lifecycle hooks, per-buffer hooks (`info`, `pin`, `init`, `fini`, `intr`), and the user class selector. Prototypes include `nvkm_fault_new_()`, GP100 buffer helpers, `gv100_fault_buffer_process()`, `gv100_fault_oneinit()`, and `nvkm_ufault_new()`.

## Control Flow
This header is declarative. Constructors choose a concrete `nvkm_fault_func`, the core uses it to allocate buffers and run lifecycle callbacks, and user-class creation later exposes the selected replayable buffer through `nvkm_ufault_new()`.

## State And Persistence
The buffer structure stores persistent runtime state for the lifetime of the fault subdevice: allocated memory, address, entry count, get/put register offsets, and interrupt registration. The header itself stores no state.

## Dependencies And Integration Points
Depends on `subdev/fault.h`, NVKM event/object infrastructure, memory allocation, interrupt handles, FIFO fault reporting, and MMU/GSP-generation code. It is the private contract between `base.c`, generation fault implementations, and `user.c`.

## Risks
The `user.rp` index, `entry_size`, and get/put register offsets must match hardware and user ABI expectations. Function-table holes or mismatched buffer counts can produce unmappable buffers, lost interrupts, or replayable faults that userspace cannot drain.

## Test Signals
Build coverage catches prototype drift. Runtime signals are successful fault subdevice oneinit/init, valid user object creation, event delivery on pending buffers, and FIFO fault reports with sane decoded fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/tu102.c

## Purpose
Implements the TU102/Turing fault subdevice path for non-GSP operation, including hardware fault buffer setup, interrupt registration, replayable fault event notification, and direct non-replayable fault decoding.

## Important APIs, Types, And Functions
Key routines are `tu102_fault_new()`, `tu102_fault_oneinit()`, `tu102_fault_init()`, `tu102_fault_fini()`, `tu102_fault_buffer_info()`, `tu102_fault_buffer_init()`, `tu102_fault_buffer_fini()`, `tu102_fault_buffer_intr()`, `tu102_fault_buffer_notify()`, and `tu102_fault_info_fault()`. The static `tu102_fault` table advertises two 32-byte buffers, GP100 pinning, GV100 worker processing, and user class `VOLTA_FAULT_BUFFER_A`.

## Control Flow
Construction refuses GSP-RM devices with `-ENODEV`, allocates the generic fault object, and installs `gv100_fault_buffer_process` as the buffer worker. Oneinit registers a direct info-fault interrupt from `0x100ee0` and buffer interrupts from `0x100ee4+`, then delegates shared GV100 setup. Init enables the info-fault interrupt, programs buffer zero, and allows pending-buffer events. Fini blocks notifications, flushes work, disables buffer zero, and blocks the info-fault interrupt.

## State And Persistence
Buffer state persists in `struct nvkm_fault_buffer` and hardware registers `0xb83000..0xb83010` per buffer. `tu102_fault_info_fault()` samples fault address, instance, engine, validity, GPC/hub, access, client, and reason registers, forwards them to FIFO via `nvkm_fifo_fault()`, and acknowledges `0xb83094`.

## Dependencies And Integration Points
Uses VFN interrupt routing, NVKM event notification, MMU/FIFO fault data, GP100 buffer memory pinning, GV100 common oneinit and worker logic, and GSP selection. Integrated by chipset-specific nouveau device construction through `tu102_fault_new()`.

## Risks
Register offsets and interrupt-vector extraction are hardware-specific. Only buffer zero is initialized in lifecycle hooks even though two buffers exist, so the user replayable-buffer index must remain consistent. Failing to block events before flushing work can race teardown.

## Test Signals
Signals include interrupt registration success, `NVKM_FAULT_BUFFER_EVENT_PENDING` delivery, correct user buffer map metadata, decoded FIFO fault records, and no Turing fault subdevice when GSP-RM owns fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/user.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/user.c

## Purpose
Exposes an NVKM user object for a replayable fault buffer so userspace can query buffer metadata, map the buffer through BAR2, and subscribe to pending-buffer events.

## Important APIs, Types, And Functions
`nvkm_ufault_new()` handles class construction and `nvif_clb069_v0` argument unpacking. `nvkm_ufault_map()` returns `NVKM_OBJECT_MAP_IO`, BAR2 instance address plus buffer offset, and allocation size. `nvkm_ufault_uevent()` subscribes to `NVKM_FAULT_BUFFER_EVENT_PENDING`. Object callbacks also include `nvkm_ufault_init()`, `nvkm_ufault_fini()`, and a no-op destructor.

## Control Flow
Creation selects `device->fault->buffer[fault->func->user.rp]`, unpacks ABI version 0 arguments, returns entries/get/put metadata to the caller, and constructs the object around the existing buffer object storage. Init/fini simply call generation-specific buffer programming callbacks. Event registration validates argument size before binding the user event to the fault event source.

## State And Persistence
No new memory is owned by the user object; it wraps the pre-existing `struct nvkm_fault_buffer`. Mapping exposes the persistent hardware-managed queue memory. Init/fini mutate hardware buffer enablement through the selected function table.

## Dependencies And Integration Points
Depends on NVIF class `clb069`, NVKM object/event helpers, BAR2 resource addressing, fault-buffer memory, and the generation fault function table. It is the user ABI bridge for draining replayable faults.

## Risks
The object does not validate that `device->fault`, `buffer`, or `buffer->mem` are non-NULL, relying on core construction ordering. ABI size mismatch returns `-ENOSYS`. BAR2 address calculation and `user.rp` must match the hardware buffer intended for userspace.

## Test Signals
Useful checks are successful CLB069 object creation, correct returned entry/get/put values, mmap size matching buffer memory, pending-event delivery, and init/fini toggling hardware without leaking events after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/Kbuild

## Purpose
Build manifest for the nouveau NVKM framebuffer subdevice and VRAM/RAM support files. It enumerates generation-specific framebuffer wrappers, RAM constructors, RAM timing calculators, and R535/GSP integration.

## Important APIs, Types, And Functions
The file does not define C APIs. It adds objects for `base.o`, legacy NV04/NV1x/NV2x/NV3x/NV4x, NV50/GT215/MCP, Fermi through Blackwell framebuffer wrappers, `r535.o`, common `ram.o`, generation RAM implementations, and type-specific timing calculators (`sddr2`, `sddr3`, `gddr3`, `gddr5`).

## Control Flow
Kbuild concatenates all `nvkm-y +=` entries into the NVKM object set. Runtime selection is done elsewhere through chipset function tables; this manifest only ensures the referenced implementations are linked.

## State And Persistence
No runtime state is stored. Build inclusion determines which constructor symbols and helper functions are available to the device table.

## Dependencies And Integration Points
Integrated by the parent nouveau NVKM build. The ordering groups framebuffer wrappers first, R535 support next, common RAM core next, then RAM generation/type helpers.

## Risks
Missing an object here produces link failures or absent chipset support even when source files exist. Adding a new wrapper without its RAM helper can leave function-table references unresolved.

## Test Signals
Kernel build/link coverage is the primary signal. Runtime probe coverage across GPU generations confirms that selected `*_fb_new()` and `*_ram_new()` symbols were linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/base.c

## Purpose
Common NVKM framebuffer subdevice implementation. It owns framebuffer construction, lifecycle, tile/comptag setup, RAM allocation/init, VPR scrub dispatch, system-memory flush-page setup, and generic wrappers around generation function tables.

## Important APIs, Types, And Functions
Public helpers include `nvkm_fb_ctor()`, `nvkm_fb_new_()`, `nvkm_fb_tile_init()`, `nvkm_fb_tile_prog()`, `nvkm_fb_tile_fini()`, `nvkm_fb_bios_memtype()`, `nvkm_fb_mem_unlock()`, and `nvkm_fb_vidmem_size()`. The `nvkm_subdev_func` instance supplies dtor/preinit/oneinit/init/intr.

## Control Flow
Oneinit constructs RAM through `func->ram_new`, runs optional generation oneinit, computes compression tags, and initializes the tag allocator. Init initializes RAM, reprograms all tile regions, initializes system-memory flush handling, runs generation init/remapper/page/unknown hooks, and returns errors for failed page setup. Teardown releases MMU scratch memory, tile state, tag allocator, RAM, VPR scrub firmware, and DMA flush page.

## State And Persistence
Persistent state lives in `struct nvkm_fb`: RAM object, tile regions, tag allocator, sysmem flush page, MMU read/write memory, and VPR scrubber firmware. Hardware state persists through tile registers, RAM controller registers, remapper/page setup, and VPR lock state.

## Dependencies And Integration Points
Depends on NVKM subdev lifecycle, BIOS M0203 RAM type parsing, core options, GR/MPEG tile notification, RAM helpers, MM allocator, DMA mapping, and VPR firmware hooks. It is the common base under every generation wrapper.

## Risks
Lifecycle ordering is critical: RAM must exist before tile/tag use, VPR scrub may require oneinit, and tile programming notifies engines that may or may not exist. BIOS memory type fallback to unknown affects downstream timing/reclocking. Flush page DMA cleanup must match allocation.

## Test Signals
Signals include framebuffer probe logs with RAM type/size, successful `nvkm_mm_init()` for tags and VRAM, tile programming without engine errors, VPR locked/unlocked messages, and suspend/resume init/fini stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/g84.c

## Purpose
NV50-family wrapper for G84 in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`g84_fb_new()` calls `nv50_fb_new_()` with NV50 RAM and NV20 tag helpers.

## Control Flow
The device table calls `g84_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
NV50 two-level function table is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ga100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ga100.c

## Purpose
Ampere GA100 framebuffer wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`ga100_fb_new()` selects `r535_fb_new()` under GSP-RM, otherwise uses GF100 oneinit, GM200 init, GV100 page init, GP100 unknown init, GP102 vidmem sizing, and GP102 RAM.

## Control Flow
The device table calls `ga100_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
GSP fallback and GP102 RAM reuse is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ga100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ga102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ga102.c

## Purpose
Ampere GA102 framebuffer wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`ga102_fb_oneinit()` loads VPR scrub firmware, `ga102_fb_new()` can use R535, and the table adds GA102 vidmem sizing plus VPR scrub hooks.

## Control Flow
The device table calls `ga102_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
VPR firmware and scrub lifecycle is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gb100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gb100.c

## Purpose
Blackwell GB100 GSP framebuffer wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gb100_fb_new()` always routes through `r535_fb_new()` with GB100 sysmem flush-page init and GA102 vidmem sizing.

## Control Flow
The device table calls `gb100_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
GSP-only construction is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gb100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gb202.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gb202.c

## Purpose
Blackwell GB202 GSP framebuffer wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gb202_fb_new()` routes through `r535_fb_new()` with GB202-specific sysmem flush-page address and GA102 vidmem sizing.

## Control Flow
The device table calls `gb202_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
GSP-only construction is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gb202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gddr3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gddr3.c

## Purpose
Calculates GDDR3 mode-register values from NVBIOS timing/config fields for use by the RAM reclocking scripts.

## Important APIs, Types, And Functions
Exports `nvkm_gddr3_calc(struct nvkm_ram *)`. Local `struct ramxlat` tables translate BIOS-encoded CL, WR, and CWL values into JEDEC-like mode register encodings.

## Control Flow
The calculator extracts CL, WR, CWL, DLL, ODT, RON, and high-frequency mode from `ram->next->bios`, applies translation tables, handles missing CWL by deriving it from CL on some paths, and writes the resulting MR values into `ram->mr[]` for later programming by generation-specific scripts.

## State And Persistence
It only mutates calculated `struct nvkm_ram` mode-register cache. Hardware persistence happens later when GT215/GF/GK scripts write MR registers.

## Dependencies And Integration Points
Called by GT215-style RAM calculation for GDDR3 targets. Depends on parsed NVBIOS rammap/timing fields and on generation scripts honoring `ram->mr[]`.

## Risks
Encoding tables are compatibility-sensitive; an unsupported BIOS value can produce invalid mode-register settings. DLL/ODT/RON interpretation must match board memory parts and voltage settings.

## Test Signals
Debug reclocking traces, successful memory clock transitions on GDDR3 boards, lack of post-reclock memory corruption, and comparison with known-good BIOS/NVIDIA behavior are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gddr3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gddr5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gddr5.c

## Purpose
Calculates GDDR5 mode-register values from parsed NVBIOS RAM timing/configuration data, including write latency, read latency, drive strength, termination, and optional per-partition differences.

## Important APIs, Types, And Functions
Exports `nvkm_gddr5_calc(struct nvkm_ram *, bool nuts)`. It fills `ram->mr[]` and `ram->mr1_nuts` using frequency, `ram->next->bios`, and GDDR5-specific latency/termination rules.

## Control Flow
The function derives WL, CL, WR and auxiliary timing variables from target frequency and BIOS fields, then constructs MR0/MR1/MR3/MR5/MR6/MR7/MR8 values. The `nuts` argument enables alternate MR1 handling for partitions whose physical memory wiring differs from the primary partition.

## State And Persistence
State is staged in the `nvkm_ram` object only. Actual persistence occurs when GK104-era scripts program MR registers and, for `nuts`, write adjusted values to non-uniform partitions.

## Dependencies And Integration Points
Used by GK104 and descendants for GDDR5 reclocking. Depends on BIOS rammap/timing decoding, partition-difference detection, and ramfuc command emission.

## Risks
GDDR5 mode-register values are extremely timing-sensitive. Wrong latency or drive/termination bits can cause immediate memory training failures or subtle data corruption. The `nuts` path must stay aligned with partition masks detected by the caller.

## Test Signals
Signals are successful reclocking across low/high memory clocks, stable GDDR5 training, no FIFO/FB errors after transition, and debug comparison of MR values against expected BIOS-derived configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gddr5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gf100.c

## Purpose
Fermi GF100 common framebuffer implementation in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gf100_fb_oneinit()` allocates MMU read/write scratch pages, `gf100_fb_init_page()` programs page/memory registers, `gf100_fb_intr()` decodes fault status, and `gf100_fb_new_()` shares construction.

## Control Flow
The device table calls `gf100_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
fault interrupt decoding and scratch-page setup is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gf100.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gf100.h

## Purpose
Private GF100 framebuffer wrapper header. It defines the GF100-derived framebuffer container and shared prototypes used by Fermi/Kepler/Maxwell/Pascal wrapper files.

## Important APIs, Types, And Functions
`struct gf100_fb` embeds `struct nvkm_fb`. Prototypes include `gf100_fb_new_()`, `gf100_fb_dtor()`, `gf100_fb_init()`, `gf100_fb_intr()`, and `gm200_fb_init()`.

## Control Flow
No runtime flow is implemented. Wrapper files include the header to share constructors and lifecycle hooks while supplying generation-specific `nvkm_fb_func` tables.

## State And Persistence
No state is stored in the header beyond the layout contract that allows `container_of` use in GF100 helpers.

## Dependencies And Integration Points
Depends on `priv.h` and the common framebuffer function table. Integrated by `gf100.c`, `gm200.c`, and later wrapper files.

## Risks
Changing the container layout or prototypes affects many generation wrappers. The minimal container assumes all extra generation state is either unnecessary or owned by common `nvkm_fb`.

## Test Signals
Compile coverage catches signature drift. Runtime probe coverage of GF100-derived wrappers validates the shared constructor and lifecycle assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gf100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gf108.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gf108.c

## Purpose
Fermi GF108 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gf108_fb_new()` reuses GF100 lifecycle hooks and selects `gf108_ram_new()`.

## Control Flow
The device table calls `gf108_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
GF108 RAM topology is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gf108.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gh100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gh100.c

## Purpose
Hopper GH100 GSP framebuffer wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gh100_fb_new()` routes through `r535_fb_new()` with GH100 sysmem flush-page init and GA102 vidmem sizing.

## Control Flow
The device table calls `gh100_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
GSP-only construction is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gh100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gk104.c

## Purpose
Kepler GK104 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gk104_fb_new()` reuses GF100 hooks, selects `gk104_ram_new()`, and provides a therm clkgate pack.

## Control Flow
The device table calls `gk104_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
clock-gate data plus GK104 RAM scripts is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gk104.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gk104.h

## Purpose
Small compatibility header for GK104 framebuffer support. It currently only includes `gf100.h`, making GK104 wrappers consume the GF100 framebuffer container and shared hooks.

## Important APIs, Types, And Functions
No new APIs are declared. Inclusion exposes `struct gf100_fb` and GF100/GF200-family helper prototypes.

## Control Flow
There is no runtime flow; it is a compile-time include bridge.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
Used by GK104-family code to avoid duplicating GF100 declarations while keeping a generation-named include point.

## Risks
The header can hide the fact that GK104 has no distinct framebuffer object type. Future GK104-only state should be added deliberately rather than overloading GF100 helpers silently.

## Test Signals
Build coverage and successful GK104/GK110 framebuffer probe are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gk104.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gk110.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gk110.c

## Purpose
Kepler GK110 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gk110_fb_new()` reuses GF100 hooks, selects GK104 RAM, and has a GK110-specific clkgate pack.

## Control Flow
The device table calls `gk110_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
clkgate register coverage is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gk110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gk20a.c

## Purpose
Tegra GK20A wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gk20a_fb_new()` reuses GF100 lifecycle hooks but has no RAM constructor, matching integrated/mobile memory handling.

## Control Flow
The device table calls `gk20a_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
absence of `ram_new` is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gm107.c

## Purpose
Maxwell GM107 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gm107_fb_new()` reuses GF100 hooks and selects `gm107_ram_new()`.

## Control Flow
The device table calls `gm107_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
GM107 FBP masks is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gm200.c

## Purpose
Maxwell GM200 common wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gm200_fb_init()` and `gm200_fb_init_page()` adjust GF100-era init for GM200, and `gm200_fb_new()` selects `gm200_ram_new()`.

## Control Flow
The device table calls `gm200_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
GM200 page/init register differences is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gm20b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gm20b.c

## Purpose
Tegra GM20B wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gm20b_fb_new()` reuses GM200 lifecycle hooks without a RAM constructor.

## Control Flow
The device table calls `gm20b_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
integrated-memory assumptions is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gm20b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gp100.c

## Purpose
Pascal GP100 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gp100_fb_new()` adds remapper and unknown init hooks, GM200 page init, and `gp100_ram_new()`.

## Control Flow
The device table calls `gp100_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
remapper and HBM init is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gp102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gp102.c

## Purpose
Pascal GP102 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gp102_fb_oneinit()` loads VPR scrub firmware, `gp102_fb_vidmem_size()` reads vidmem size, and table includes VPR scrub hooks plus `gp102_ram_new()`.

## Control Flow
The device table calls `gp102_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
VPR lock clearing and vidmem sizing is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gp102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gp10b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gp10b.c

## Purpose
Tegra GP10B wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gp10b_fb_new()` reuses GM200 lifecycle hooks without RAM construction.

## Control Flow
The device table calls `gp10b_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
integrated-memory assumptions is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gp10b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gt215.c

## Purpose
GT215 NV50-family wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gt215_fb_new()` calls `nv50_fb_new_()` with `gt215_ram_new()` and NV20 tags.

## Control Flow
The device table calls `gt215_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
GT215 reclocking RAM scripts is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gv100.c

## Purpose
Volta GV100 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`gv100_fb_new()` uses GP102 oneinit/VPR/vidmem, GM200 init, GV100 page init, GP100 unknown init, and GP102 RAM.

## Control Flow
The device table calls `gv100_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
Volta page init and VPR reuse is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/gv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/mcp77.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/mcp77.c

## Purpose
MCP77 integrated wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`mcp77_fb_new()` uses `nv50_fb_new_()` with `mcp77_ram_new()`.

## Control Flow
The device table calls `mcp77_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
stolen-memory reservations is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/mcp77.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/mcp89.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/mcp89.c

## Purpose
MCP89 integrated wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`mcp89_fb_new()` also uses `mcp77_ram_new()` via NV50 wrapper.

## Control Flow
The device table calls `mcp89_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
shared MCP77 RAM assumptions is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/mcp89.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv04.c

## Purpose
NV04 legacy wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`nv04_fb_init()` writes basic PFB registers and `nv04_fb_new()` selects `nv04_ram_new()`.

## Control Flow
The device table calls `nv04_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
legacy register initialization is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv10.c

## Purpose
NV10 legacy wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`nv10_fb_tile_*()` implement 8 tile regions and `nv10_fb_new()` selects `nv10_ram_new()`.

## Control Flow
The device table calls `nv10_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
tile register encoding is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv1a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv1a.c

## Purpose
NV1A integrated wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`nv1a_fb_new()` reuses NV10 tile helpers and selects `nv1a_ram_new()`.

## Control Flow
The device table calls `nv1a_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
stolen-memory detection is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv1a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv20.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv20.c

## Purpose
NV20 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`nv20_fb_tags()` computes comptags, `nv20_fb_tile_*()` add compression-aware tile programming, and `nv20_fb_new()` selects `nv20_ram_new()`.

## Control Flow
The device table calls `nv20_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
comptag/tile math is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv25.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv25.c

## Purpose
NV25 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`nv25_fb_tile_comp()` adjusts compression calculation while reusing NV20 tile/program hooks.

## Control Flow
The device table calls `nv25_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
compression tag calculation is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv30.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv30.c

## Purpose
NV30 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`nv30_fb_init()` programs memory-controller bias registers and NV30 tile/compression helpers.

## Control Flow
The device table calls `nv30_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
bias calculation from strap registers is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv35.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv35.c

## Purpose
NV35 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
Reuses NV30 init/tile helpers with NV35 compression calculation and NV20 RAM.

## Control Flow
The device table calls `nv35_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
NV35 compression layout is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv35.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv36.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv36.c

## Purpose
NV36 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
Reuses NV30 init/tile helpers with NV36 compression calculation and NV20 RAM.

## Control Flow
The device table calls `nv36_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
NV36 compression layout is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv36.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv40.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv40.c

## Purpose
NV40 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`nv40_fb_init()` programs NV40-specific registers, uses NV30 tile init, NV40 compression, and `nv40_ram_new()`.

## Control Flow
The device table calls `nv40_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
NV40 tile/comptag stride is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv41.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv41.c

## Purpose
NV41 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`nv41_fb_init()` and `nv41_fb_tile_prog()` support 12 tile regions with NV40 compression and `nv41_ram_new()`.

## Control Flow
The device table calls `nv41_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
12-region tile programming is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv41.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv44.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv44.c

## Purpose
NV44 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`nv44_fb_init()`, `nv44_fb_tile_init()`, and `nv44_fb_tile_prog()` support NV44 tile layout and `nv44_ram_new()`.

## Control Flow
The device table calls `nv44_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
NV44 tile address format is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv44.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv46.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv46.c

## Purpose
NV46 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
Uses NV44 init/programming, 15 tile regions, NV46 tile init, and NV44 RAM.

## Control Flow
The device table calls `nv46_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
15-region tile layout is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv46.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv47.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv47.c

## Purpose
NV47 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
Uses NV41 init/programming, 15 tile regions, NV40 compression, and NV41 RAM.

## Control Flow
The device table calls `nv47_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
NV47/NV41 helper reuse is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv47.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv49.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv49.c

## Purpose
NV49 wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
Uses NV41 init/programming, 15 tile regions, NV40 compression, and NV49 RAM.

## Control Flow
The device table calls `nv49_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
NV49 RAM type detection is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv49.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv4e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv4e.c

## Purpose
NV4E wrapper in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
Uses NV44 init/programming, 12 tile regions, NV46 tile init, and NV44 RAM.

## Control Flow
The device table calls `nv4e_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
helper reuse across close chipsets is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv4e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv50.c

## Purpose
NV50 common framebuffer implementation in the nouveau NVKM framebuffer subsystem. It supplies the chipset-specific function table that binds common framebuffer lifecycle code to the correct RAM, tile, tag, page, interrupt, VPR, or GSP behavior.

## Important APIs, Types, And Functions
`nv50_fb_intr()` decodes VM faults, `nv50_fb_init()` initializes trap handling, `nv50_fb_tags()` dispatches tags, and `nv50_fb_new_()` bridges NV50-specific function tables.

## Control Flow
The device table calls `nv50_fb_new()`, which delegates to `nvkm_fb_new_()`, `gf100_fb_new_()`, `nv50_fb_new_()`, or `r535_fb_new()` with a static function table. Common `base.c` then invokes the selected hooks during oneinit/init/intr/destruction.

## State And Persistence
The file mostly contributes static function-table state. Runtime persistence is in the common `struct nvkm_fb` and `struct nvkm_ram`, while hardware state is changed by the referenced init, tile, RAM, VPR, and sysmem flush-page hooks.

## Dependencies And Integration Points
Depends on `priv.h` and, for newer families, GF100/GM/GP/GV helper files and RAM constructors. Integrated by chipset-specific nouveau device construction.

## Risks
VM fault decode tables and two-level construction is the file-specific risk. A wrong hook selection can boot on nearby chips but corrupt VRAM layout, fault decode, tile programming, or VPR handling. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Per-chip probe logs, correct VRAM size/type, framebuffer init without MMIO faults, suspend/resume, fault interrupt behavior where present, and generation-specific boot tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv50.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv50.h

## Purpose
Private NV50 framebuffer header. It defines the NV50 wrapper around common `nvkm_fb` and a secondary `nv50_fb_func` table used by NV50/G84/GT215/MCP variants.

## Important APIs, Types, And Functions
`struct nv50_fb` stores a pointer to `struct nv50_fb_func` and embeds `struct nvkm_fb`. `struct nv50_fb_func` supplies `ram_new`, `tags`, and `trap` behavior. `nv50_fb_new_()` is the shared constructor.

## Control Flow
The header is declarative. `nv50_fb_new_()` in `nv50.c` wraps a narrower NV50-specific table into the generic framebuffer function table.

## State And Persistence
The only added persistent state is the selected NV50 function table pointer. Runtime VRAM/tile/tag state remains in the embedded common framebuffer object.

## Dependencies And Integration Points
Includes `priv.h` and is used by NV50-era wrapper files such as `g84.c`, `gt215.c`, `mcp77.c`, and `mcp89.c`.

## Risks
The two-level function-table design requires `nv50_fb_ram_new()` and tag dispatch to keep the embedded pointer valid through object lifetime.

## Test Signals
Compile/link checks for wrapper symbols and runtime VM fault/tag handling on NV50-family chips validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/nv50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/priv.h

## Purpose
Private framebuffer subdevice interface. It defines the generation function table consumed by `base.c` and declares shared tile, init, RAM, VPR, vidmem, and constructor helpers.

## Important APIs, Types, And Functions
`struct nvkm_fb_func` contains lifecycle hooks, sysmem flush-page init, vidmem sizing, VPR scrub hooks, tile operations, RAM construction, and clkgate packs. It declares `nvkm_fb_ctor()`, `nvkm_fb_new_()`, BIOS RAM-type lookup, legacy tile helpers, GF100/GM/GV/GP/GA helpers, R535 constructor, and vidmem/VPR operations.

## Control Flow
This header routes compile-time dependencies. Generation files fill `nvkm_fb_func` instances; `base.c` calls the hooks in lifecycle order; R535 wrappers use the same table to provide host-driver-backed RAM information.

## State And Persistence
No direct state is stored, but the function table controls persistent hardware state such as RAM object construction, tile programming, remapper/page setup, VPR unlock, and sysmem flush-page programming.

## Dependencies And Integration Points
Depends on NVKM framebuffer public types, BIOS, thermal clkgate packs, RAM constructors, and generation helpers. It is the central private contract for all files in `subdev/fb`.

## Risks
Hook semantics are broad and generation-specific. A wrong function pointer can corrupt framebuffer setup on only one architecture, and optional hooks require callers to preserve NULL checks.

## Test Signals
Compiler diagnostics catch missing declarations. Runtime probe, init, VPR scrub, vidmem sizing, and tile/comptag behavior across generations validate table wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/r535.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/r535.c

## Purpose
Framebuffer integration path for GPUs managed by NVIDIA's GSP/R535 resource-manager interface. It creates an NVKM framebuffer object while sourcing VRAM size/type from GSP RM instead of legacy hardware probing.

## Important APIs, Types, And Functions
`r535_fb_new()` clones a hardware `nvkm_fb_func`, overrides its `ram_new` hook, and calls `nvkm_fb_new_()`. `r535_fb_ram_new()` asks `nvkm_gsp_rm_alloc_get()` for `NV2080_CTRL_CMD_FB_GET_FB_REGION_INFO` and constructs RAM with `r535_ram`. `r535_ram` mainly supplies the `upper` address split.

## Control Flow
Wrapper constructors for newer chips call `r535_fb_new()` when GSP-RM is active. RAM construction allocates the RM control object, reads region information, maps RM RAM type to NVKM RAM type, creates a common RAM object, and frees RM resources through `r535_fb_dtor()`.

## State And Persistence
Persistent state includes the copied function table and GSP RM allocation handle. RAM size/type state is stored in the common `nvkm_ram` object; no legacy VRAM probing allocator split is performed here beyond `nvkm_ram_new_()`.

## Dependencies And Integration Points
Depends on GSP RM control headers, common framebuffer construction, RAM core, and per-chip wrappers such as GA/GB/GH. It is selected only when GSP RM owns low-level management.

## Risks
RM type translation currently handles specific GDDR/HBM values and returns unknown otherwise. Allocation failures abort probe. Function-table cloning must preserve all non-RAM hardware hooks from the caller.

## Test Signals
Signals include successful GSP RM framebuffer probe, correct logged VRAM size/type, clean RM free in dtor, and fallback to legacy constructors when GSP RM is inactive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/r535.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ram.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ram.c

## Purpose
Common VRAM memory object and RAM allocator implementation. It wraps framebuffer VRAM allocations as `nvkm_memory`, allocates/free ranges from the RAM memory manager, and initializes/destroys `struct nvkm_ram`.

## Important APIs, Types, And Functions
`struct nvkm_vram` wraps `nvkm_memory`, RAM owner, page size, and MM nodes. Public functions are `nvkm_ram_get()`, `nvkm_ram_wrap()`, `nvkm_ram_init()`, `nvkm_ram_del()`, `nvkm_ram_ctor()`, and `nvkm_ram_new_()`. Memory callbacks implement target/page/address/size/map/kmap/dtor.

## Control Flow
`nvkm_ram_get()` validates framebuffer RAM, creates a VRAM object, allocates one or more MM nodes from head or tail according to contiguity and alignment, and unwinds on failure. `nvkm_ram_wrap()` creates a synthetic node for a fixed physical range. Destruction returns allocated nodes to `ram->vram` under lock, except synthetic wrapped nodes are simply freed.

## State And Persistence
RAM state persists in `struct nvkm_ram`: type, size, function table, mutex, and MM allocator. VRAM memory objects persist allocated MM nodes until the memory reference is dropped. `nvkm_ram_ctor()` logs size/type and initializes the default allocator if generation constructors have not already provided one.

## Dependencies And Integration Points
Depends on NVKM memory/VMM APIs, instmem wrapping for kernel maps, MM allocator, framebuffer ownership, and RAM generation constructors. All VRAM allocations used by other NVKM subsystems flow through this layer.

## Risks
Allocator locking and unwind paths are safety-critical. `nvkm_ram_wrap()` creates a synthetic node not inserted in the MM list, so dtor must distinguish it correctly. Address/size truncation to `NVKM_RAM_MM_SHIFT` can silently drop sub-page portions if callers pass unaligned ranges.

## Test Signals
Signals include successful VRAM allocation/free under stress, contiguous and fragmented allocation behavior, VMM mapping correctness, kernel map wrapping, and no MM leaks on constructor or allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ram.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ram.h

## Purpose
Private RAM subsystem declarations for the framebuffer code. It exposes common RAM construction/destruction, generation RAM constructors, probe helpers, reclocking hooks, and memory-type timing calculators.

## Important APIs, Types, And Functions
Declares `nvkm_ram_ctor()`, `nvkm_ram_new_()`, `nvkm_ram_del()`, `nvkm_ram_init()`, `nv50_ram_ctor()`, GF100/GK104 constructors and reclocking hooks, FBP probing helpers, GM/GP probing/init helpers, memory-type calculators, and all legacy/generation `*_ram_new()` entry points.

## Control Flow
No runtime code exists. It lets framebuffer wrappers choose the correct `ram_new` hook and lets generation implementations share common constructors and probing functions.

## State And Persistence
No state is stored; declarations operate on `struct nvkm_ram`, whose state is managed by `ram.c` and generation implementations.

## Dependencies And Integration Points
Includes `priv.h` and connects `Kbuild`-linked RAM files to framebuffer function tables. It is the compile-time map of RAM support across NV04 through Pascal-era helpers.

## Risks
Signature drift affects many wrappers. Exporting internal reclocking helpers requires generation files to respect preconditions such as initialized function tables and parsed BIOS data.

## Test Signals
Build coverage across all linked RAM files and runtime probe/reclocking coverage validate the declaration surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramfuc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramfuc.h

## Purpose
Helper layer for building PMU memx scripts used by RAM reclocking code. It caches register values, emits masked writes/waits/delays/training commands, and manages script init/execute lifetime.

## Important APIs, Types, And Functions
`struct ramfuc` stores the active `nvkm_memx`, framebuffer, and sequence counter. `struct ramfuc_reg` describes cached register address, stride, mask, force flag, and data. Helpers include `ramfuc_reg()`, `ramfuc_reg2()`, `ramfuc_stride()`, `ramfuc_init()`, `ramfuc_exec()`, `ramfuc_rd32()`, `ramfuc_wr32()`, `ramfuc_mask()`, waits, delays, training, block/unblock, and macro aliases such as `ram_mask()` and `ram_exec()`.

## Control Flow
Generation reclocking code calls `ram_init()` to allocate a memx script, uses cached register helpers to emit writes only when values change or are forced, inserts waits/delays/training operations, and finishes with `ram_exec(exec)` to either run or discard the script.

## State And Persistence
Register cache state is per `ramfuc_reg` and invalidated by sequence number. The active memx command buffer persists between init and exec. Hardware state changes persist only when `nvkm_memx_fini(..., true)` executes the script.

## Dependencies And Integration Points
Depends on framebuffer, PMU memx, and generation RAM scripts (`ramgt215.c`, `ramgf100.c`, `ramgk104.c`). It isolates complex reclocking sequences from direct immediate MMIO writes.

## Risks
Using helpers outside an active `ram->fb`/memx lifetime is invalid. Register caching can skip writes unless `ram_nuke()` forces them. Stride masks must match partition/rank layout or only some memory partitions receive updates.

## Test Signals
Signals include successful script allocation/execution, expected MMIO command traces, stable reclocking with `NvMemExec=1`, and safe dry-run/discard behavior with `NvMemExec=0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramfuc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgf100.c

## Purpose
Fermi GF100 RAM implementation, including FBP-based VRAM sizing/allocation layout, GDDR5 training-pattern initialization, BIOS-driven reclocking script generation, and shared helpers for later generations.

## Important APIs, Types, And Functions
Defines `struct gf100_ramfuc`, `struct gf100_ram`, `gf100_ram_new_()`, `gf100_ram_new()`, `gf100_ram_ctor()`, FBP probe helpers, `gf100_ram_init()`, `gf100_ram_calc()`, `gf100_ram_prog()`, `gf100_ram_tidy()`, and `gf100_ram_train()`.

## Control Flow
Construction probes enabled FBPs/LTCs, computes lower and upper VRAM regions for mixed-memory layouts, initializes the MM allocator, parses reference and memory PLL BIOS records, and registers ramfuc MMIO targets. Init loads GDDR5 training patterns. Calc parses RAMMAP/RAMCFG/timing BIOS entries, determines current and target clock modes, builds a memx script for PLL changes, self-refresh, timing/MR programming, training, and reenable. Prog executes or discards the script according to `NvMemExec`; tidy discards any pending script.

## State And Persistence
Persistent state includes RAM type/size, MM allocator regions, PLL descriptors, ramfuc register cache, and generated scripts between calc/prog. Hardware persistence includes memory controller timing registers, PLL registers, MR values, training state, and VRAM address split.

## Dependencies And Integration Points
Depends on BIOS RAMMAP/timing/PLL parsers, clock source reads, ramfuc/memx, common RAM allocator, and GF100 framebuffer wrappers. Later RAM files reuse FBP probing and constructor helpers.

## Risks
This is high-risk hardware sequencing. Mixed-memory allocator math must not expose reserved VGA/VBIOS areas incorrectly. BIOS version assumptions (`0x10`) and magic register scripts can fail on boards outside known coverage. Reclocking with wrong PLL/timing values can hang memory.

## Test Signals
Signals include probe logs for FBP/LTC sizes and lower/upper VRAM split, GDDR5 training load, successful `NvMemExec` reclock cycles, stable VRAM allocation in mixed configurations, and no FB/FIFO faults after clock changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgf108.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgf108.c

## Purpose
GF108 RAM wrapper for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`gf108_ram_probe_fbp_amount()` sums FBPA sizes per FBP using `0x022438/0x02243c` topology and reuses GF100 init/calc/prog/tidy.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
GF108 FBP/FBPA topology differs from GF100; wrong FBPA grouping misreports VRAM and allocator layout. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgf108.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgk104.c

## Purpose
Kepler GK104 RAM implementation. It extends GF100 allocation with RAMMAP table caching, partition-difference handling, GDDR5/DDR3 reclocking scripts, PLL calculation, GPIO voltage switching, and BIOS training-data upload.

## Important APIs, Types, And Functions
Defines `struct gk104_ramfuc`, `struct gk104_ram`, `gk104_ram_new_()`, `gk104_ram_new()`, `gk104_ram_dtor()`, `gk104_ram_init()`, `gk104_ram_calc()`, `gk104_ram_prog()`, `gk104_ram_tidy()`, `gk104_ram_calc_gddr5()`, `gk104_ram_calc_sddr3()`, PLL helpers, and training-table helpers.

## Control Flow
Construction calls `gf100_ram_ctor()`, detects disabled and non-uniform memory partitions (`pmask`/`pnuts`), parses all RAMMAP entries into a list while recording fields that differ, parses ref/mem PLL BIOS entries, finds voltage GPIOs, and registers all ramfuc targets. Init runs RAMMAP init scripts and uploads M0205/M0209 GDDR5 training data. Calc selects former/target/xition configurations, calculates PLLs, snapshots MRs, calls DDR3 or GDDR5 MR calculators, then emits a detailed memx transition script. Prog applies static RAMMAP register changes before and after executing the script; tidy clears pending transition state.

## State And Persistence
State includes cached RAMMAP configs, diff masks, transition state (`former`, `target`, `xition`, `next`), PLL coefficients, voltage GPIO choices, partition masks, MR values, and ramfuc script state. Hardware state persists in PLLs, controller timings, MR registers, training tables, and per-partition adjustments.

## Dependencies And Integration Points
Depends on GF100 allocation/probe logic, NVBIOS RAMMAP/timing/M0205/M0209/PLL parsers, GPIO, clock, ramfuc/memx, and type calculators for DDR3/GDDR5. Used by GK104/GK110 wrappers and descendants that reuse GK104 RAM behavior.

## Risks
Very high risk: BIOS field-diff logic intentionally avoids touching fields that do not vary, and changing that can regress boards. The two-step xition path, partition `nuts` writes, and voltage GPIO timing are hardware-sensitive. Training data remapping must match BIOS table semantics.

## Test Signals
Signals include parsed RAMMAP count, missing training-data warnings, successful low-to-high and high-to-low reclocks, stable GDDR5/DDR3 operation, correct behavior with non-uniform partitions, and debug PLL target/refclock logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgm107.c

## Purpose
GM107 RAM wrapper for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`gm107_ram_probe_fbp()` checks disable mask `0x021c14` and reuses GF100 amount probing with GK104 RAM operations.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
GM107 has different FBP disable registers; using GF100 masks would expose disabled memory. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgm200.c

## Purpose
GM200 RAM wrapper for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`gm200_ram_probe_fbp_amount()` reads LTC/FBPA topology and disabled LTC masks to compute active memory per FBP, reusing GK104 operations.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
Disabled LTC accounting affects mixed-memory allocator size and compression/cache assumptions. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgp100.c

## Purpose
GP100 RAM wrapper for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`gp100_ram_init()` runs RAMMAP init scripts selected around `0x9a065c`, `gp100_ram_probe_fbp()` reads HBM partition size, and `gp100_ram_new()` reuses GF100 construction with GP100 init only.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
HBM init scripts and address registers are generation-specific; bad script selection can leave memory controller partially initialized. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgp102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgp102.c

## Purpose
GP102 RAM wrapper for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
Defines a thin `nvkm_ram_func` with GP102 upper address split and constructs RAM from `fb->func->vidmem.size()` through `nvkm_ram_new_()`.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
Relies on framebuffer vidmem sizing hook being correct; no per-FBP probing occurs here. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgp102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgt215.c

## Purpose
GT215/NVA3 RAM implementation for NV50-era DDR2/DDR3/GDDR3 reclocking, including optional one-time DDR link training, timing calculation, GPIO voltage/ODT control, PLL switching, and memx script generation.

## Important APIs, Types, And Functions
Defines `struct gt215_ramfuc`, `struct gt215_ltrain`, `struct gt215_ram`, `gt215_ram_new()`, `gt215_ram_init()`, `gt215_ram_calc()`, `gt215_ram_prog()`, `gt215_ram_tidy()`, `gt215_ram_dtor()`, link-training helpers, timing calculator, PLL lock helper, and GPIO helper.

## Control Flow
Init checks BIOS M0205 training support, allocates training VRAM, programs pattern buffers, and snapshots training registers. On first calc, optional link training reclocks to the training frequency, executes a training script, reads results, computes median settings, and reclocks back. Normal calc parses RAMMAP/RAMCFG/timing data, computes GT215 MCLK settings, calculates mode registers for DDR2/DDR3/GDDR3, and emits a script that disables display/FB access, enters self-refresh, switches PLL or bypass clocks, programs timing/MR registers, toggles GPIO voltage/ODT, resets DLLs, and re-enables FB.

## State And Persistence
State includes target BIOS timing/config, MR cache, training memory, training state machine and computed registers, ramfuc cache, and RAM allocator data from `nv50_ram_ctor()`. Hardware persistence includes PLL, timing, mode registers, GPIO voltage/ODT, and training registers.

## Dependencies And Integration Points
Depends on NV50 RAM construction, GT215 clock helpers, GPIO, BIOS RAMMAP/timing/M0205 tables, ramfuc/memx, and type-specific calculators. Used by `gt215.c` framebuffer wrapper.

## Risks
Training and reclocking are timing-sensitive and depend on PMU memx execution. Error paths must post clocks correctly. Multiple partition training is marked incomplete. GPIO inversion/log interpretation and DLL disable/reset ordering can break board-specific memory.

## Test Signals
Signals include training result debug dumps, computed `r_100720/r_1111e0/r_111400`, successful `NvMemExec` reclocks across supported memory types, no display flicker beyond expected masks, and clean cleanup of training memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/rammcp77.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/rammcp77.c

## Purpose
MCP77 integrated-memory wrapper for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`mcp77_ram_new()` builds stolen-memory RAM from chipset registers, reserves VGA/VBIOS/poller memory, and `mcp77_ram_init()` programs poller offsets near the top of stolen memory.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
Register-reported stolen memory windows and reserved tail math must be exact or poller space can overlap usable VRAM. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/rammcp77.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv04.c

## Purpose
NV04 RAM detector for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`nv04_ram_new()` reads `NV04_PFB_BOOT_0`, decodes size from straps or register fields, selects SGRAM/SDRAM, and uses the simple `nv04_ram_func`.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
Legacy strap interpretation is chipset-specific and has limited validation. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv10.c

## Purpose
NV10 RAM detector for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`nv10_ram_new()` reads size from `0x10020c`, DDR/SDR type from `0x100200`, and reuses `nv04_ram_func`.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
Assumes register size field is trustworthy and does not set partition count. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv1a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv1a.c

## Purpose
NV1A/NForce stolen-memory detector for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`nv1a_ram_new()` locates the host bridge, reads chipset-specific PCI config, computes stolen-memory MiB, and constructs stolen RAM.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
PCI bridge lookup and chipset register offsets are platform-specific; missing bridge aborts probe. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv1a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv20.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv20.c

## Purpose
NV20 RAM detector for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`nv20_ram_new()` decodes SDR/DDR/GDDR type from `0x001218`, size from `0x10020c`, creates RAM, and records partition count from `0x100200`.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
Incorrect type or partition count breaks tile/comptag calculations. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv40.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv40.c

## Purpose
NV40 RAM implementation for legacy memory clock calculation and programming plus RAM type/size detection. It provides a shared constructor used by several NV4x RAM wrappers.

## Important APIs, Types, And Functions
Defines `nv40_ram_calc()`, `nv40_ram_prog()`, `nv40_ram_tidy()`, `nv40_ram_new_()`, and `nv40_ram_new()`. Uses `struct nv40_ram` from `ramnv40.h` to cache PLL control and coefficient values.

## Control Flow
Calc parses the memory PLL BIOS record and computes PLL coefficients with `nv04_pll_calc()`. Prog detects active CRTCs, waits for vblank, disables VGA memory access, precharges/refreshes RAM, enters self-refresh, programs memory PLL registers per chipset, exits self-refresh, runs the BIOS memory reset script, then restores CRTC access. `nv40_ram_new()` reads type/size from registers and sets partition count.

## State And Persistence
Calculated PLL control/coefficient values persist in `struct nv40_ram` between calc and prog. Hardware state includes VGA sequencer access bits, RAM refresh/self-refresh, PLL registers, BIOS init side effects, and partition count.

## Dependencies And Integration Points
Depends on BIOS BIT/M/init/pll parsing, NV04 PLL calculation, timer delays, legacy display vblank registers, and wrappers such as NV40/NV41/NV49.

## Risks
Display memory access disable/restore timing is fragile. Vblank polling timeouts, wrong chipset PLL register set, or missing BIOS memory reset script can blank displays or hang memory. Type detection is register-based and board-specific.

## Test Signals
Signals include successful memory clock change on NV4x boards, no stuck VGA sequencer state, BIOS M script execution, stable display after reclock, and correct RAM type/partition logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv40.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv40.h

## Purpose
Private header for NV40-style RAM reclocking state and constructor sharing.

## Important APIs, Types, And Functions
Defines `struct nv40_ram`, embedding `struct nvkm_ram` plus cached `ctrl` and `coef` PLL programming values. Declares `nv40_ram_new_()`.

## Control Flow
No runtime flow. NV41/NV44/NV49 wrappers call the shared constructor after detecting type/size.

## State And Persistence
The `ctrl` and `coef` fields persist between `calc` and `prog` and drive hardware PLL writes in `ramnv40.c`.

## Dependencies And Integration Points
Includes `ram.h` and is used by NV40-family RAM files.

## Risks
All users share the same PLL-state layout; constructor callers must pass correct type and size from generation-specific detection.

## Test Signals
Build coverage and successful NV4x RAM construction/reclocking validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv41.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv41.c

## Purpose
NV41 RAM detector for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`nv41_ram_new()` reads type bits from `0x100474`, constructs via `nv40_ram_new_()`, and sets partition count.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
Multiple type bits are handled by last assignment; malformed registers can choose a surprising type. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv41.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv44.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv44.c

## Purpose
NV44 RAM detector for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`nv44_ram_new()` reads size/type from NV44 registers and delegates to `nv40_ram_new_()` without setting partitions.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
Type-bit precedence and missing partition count matter for callers expecting NV40-like behavior. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv44.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv49.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv49.c

## Purpose
NV49 RAM detector for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`nv49_ram_new()` decodes type from `0x100914`, delegates to NV40 reclocking support, and sets partition count.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
Unsupported type code 3 remains unknown; partition count still comes from legacy register bits. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv49.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv4e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv4e.c

## Purpose
NV4E RAM detector for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`nv4e_ram_new()` reads size and creates unknown-type RAM with `nv04_ram_func`.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
Unknown type disables advanced timing assumptions and leaves capability lower than specific RAM wrappers. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv4e.c -->
