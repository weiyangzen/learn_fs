# subset-b-005415 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-params.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-params.c

## Purpose
`ipu3-css-params.c` converts V4L2/user IPU3 parameter payloads into firmware ABI structures consumed by the IPU3 CSS pipeline while streaming. It builds accelerator (`acc`) parameters, late-bound VMEM0/DMEM0 parameter blocks, output-system scaler/formatter state, 3A operation schedules, and default GDC warp tables. The file is the bridge between user controls in `ipu3_uapi_params`, firmware binary memory-offset metadata, and the device-visible parameter buffers queued by `ipu3-css.c`.

## Important APIs, Types, and Functions
- Exported functions are `imgu_css_cfg_acc()`, `imgu_css_cfg_vmem0()`, `imgu_css_cfg_dmem0()`, and `imgu_css_cfg_gdc_table()`.
- `struct imgu_css_scaler_info`, `struct imgu_css_reso`, `struct imgu_css_frame_params`, and `struct imgu_css_stripe_params` are local calculation carriers for scaler and output-system programming.
- `imgu_css_scaler_setup_lut()`, `imgu_css_scaler_calc_scaled_output()`, and `imgu_css_scaler_calc()` compute fixed-point phase steps, coefficient LUTs, padding, cropping, and actual scaled output sizes.
- `imgu_css_osys_calc_frame_and_stripe_params()` and `imgu_css_osys_calc()` program output formatter/scaler ABI fields for main and VF pins, including split-stripe geometry.
- `imgu_css_shd_ops_calc()` and `imgu_css_acc_process_lines()` generate accelerator operation lists for shading, AF, AWB, and AWB FR metadata handshakes.
- `imgu_css_cfg_copy()` uses firmware offset tables and `imgu_css_fw_pipeline_params()` to locate ABI substructures, then copies user values, previous values, or returns a region that must be initialized from defaults.

## Control Flow
Parameter submission starts in `imgu_css_set_parameters()` in `ipu3-css.c`, which allocates/reuses pool entries and calls this file's configuration functions. `imgu_css_cfg_acc()` always recalculates stripe and geometry-sensitive state first, then walks each accelerator block: it copies a user-provided block when the matching `use` bit is set, otherwise reuses the old block if present, otherwise installs driver defaults from `ipu3-tables.h` or zero/default literals. After block copies, it patches fields that depend on the current format, selected firmware binary, BDS/GDC dimensions, stripe count, and auxiliary frame sizes.

The OSYS path computes the VF scaler first, then calculates per-stripe input offsets, phase initialization, padding, crop, chunk sizes, block sizes, and output offsets. `imgu_css_osys_calc()` then materializes those values into `struct imgu_abi_osys_config` scaler, frame, formatter, and stripe arrays. The 3A paths derive grid ends and per-stripe grids, decide whether a statistics grid belongs to the left stripe, right stripe, or both, and generate process-line/read/transfer operation tables.

VMEM0 and DMEM0 configuration is offset-table driven: the destination block is zeroed to the firmware-declared size, then each supported sub-parameter is copied from user/old state or initialized from defaults. GDC table generation writes a unity/no-warp table containing luma and chroma block descriptors and input address offsets for each DVS block.

## State and Persistence Behavior
This file does not persist state directly. It builds transient ABI parameter snapshots into DMA-backed pool entries owned by `struct imgu_css_pipe`. State continuity is achieved by receiving old pool entries from `ipu3-css.c`; when a new user payload omits a section, the previous ABI section is copied forward. Defaults are used only when there is no prior state. Calculated fields are deterministic from the current CSS pipe format rectangles, selected firmware binary metadata, and user/default parameters.

## Dependencies and Integration Points
The code depends heavily on `ipu3-css.h` for CSS pipe/queue geometry, `ipu3-css-fw.h` for firmware offset helpers, `ipu3-tables.h` for static default tables and coefficient LUTs, and `ipu3-abi.h`/UAPI structures for exact ABI layouts. It integrates with `ipu3-css.c` parameter queueing and with the firmware's memory initializer tables; `imgu_css_fw_pipeline_params()` is the safety gate that verifies requested ABI substructure ranges are valid for the selected binary.

## Risks
- Arithmetic is dense and hardware-specific; off-by-one, alignment, and signed/unsigned mistakes in stripe/scaler/grid calculations can cause corrupt output or firmware hangs.
- Several paths assume two stripes by indexing stripe 1 during grid splitting; correctness relies on firmware-selected `num_stripes` and earlier format constraints.
- User-provided grids can cause `-EINVAL` through zero widths, impossible height-per-slice values, or out-of-frame grids; callers must handle retries without stopping streaming.
- `imgu_css_cfg_vmem0()` initializes only one XNR3 LUT element after setting `i = IPU3_UAPI_ISP_TNR3_VMEM_LEN`, which is notable and should be compared with expected ABI table sizing.
- Firmware metadata corruption or ABI drift returns `-EPROTO`; this is a hard compatibility risk because the code writes directly into offset-derived firmware memory layouts.

## Test Signals
Useful tests include format/rectangle combinations that exercise one-stripe and two-stripe binaries, VF scaling ratios around 0.5 and 0.875 thresholds, grids that fall fully left/right/across stripe overlap, omitted parameter sections that should preserve old state, default initialization with `set_params == NULL`, and invalid grid dimensions that must return `-EINVAL`. Hardware or simulator validation should watch for firmware warnings/asserts, queue acceptance of parameter buffers, correct 3A metadata completion, and no image corruption around stripe boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-params.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-params.h

## Purpose
`ipu3-css-params.h` declares the parameter conversion API used by the CSS core. It keeps parameter-building internals out of `ipu3-css.c` while exposing the functions needed to create accelerator, VMEM0, DMEM0, and GDC warp ABI blocks.

## Important APIs, Types, and Functions
- `imgu_css_cfg_acc()` fills `struct imgu_abi_acc_param` from user parameters, old accelerator state, current CSS pipe geometry, and defaults.
- `imgu_css_cfg_vmem0()` fills the ISP VMEM0 late-binding parameter memory.
- `imgu_css_cfg_dmem0()` fills the ISP DMEM0 late-binding parameter memory.
- `imgu_css_cfg_gdc_table()` generates a no-warp GDC table for DVS/GDC output geometry.

## Control Flow
The header is consumed by `ipu3-css.c`, primarily from `imgu_css_set_parameters()`. The caller allocates DMA-backed buffers from CSS pools, passes current and previous buffer virtual addresses, and receives a fully populated ABI parameter block or an error code.

## State and Persistence Behavior
The header itself stores no state. Its prototypes encode the state handoff contract: `acc_old`, `vmem0_old`, and `dmem0_old` allow omitted user sections to inherit prior values, while `use` flags select user-provided sections.

## Dependencies and Integration Points
The declarations rely on forward visibility of `struct imgu_css`, IPU3 UAPI parameter types, and firmware ABI parameter types from surrounding includes. It is integrated directly with the CSS parameter queueing path and indirectly with firmware memory-offset validation.

## Risks
The API passes raw `void *` memory for VMEM/DMEM blocks and expects caller-provided buffers to match firmware-declared sizes. Any mismatch in selected binary, old/new buffer pairing, or UAPI/ABI struct layout can corrupt firmware-visible parameter memory.

## Test Signals
Compile coverage should verify prototype consistency across `ipu3-css.c` and `ipu3-css-params.c`. Runtime tests should confirm parameter updates preserve old values when `use` bits are clear and correctly reject invalid geometry or firmware offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-pool.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-pool.c

## Purpose
`ipu3-css-pool.c` implements a small circular pool of DMA-mapped CSS parameter buffers. The pool allows the streaming parameter path to retain several generations of firmware-visible parameter blocks so new parameter submissions can reuse old state and avoid overwriting buffers still visible to firmware.

## Important APIs, Types, and Functions
- `imgu_css_dma_buffer_resize()` grows an existing DMA map when the selected firmware binary requires a larger block.
- `imgu_css_pool_init()` allocates `IPU3_CSS_POOL_SIZE` entries, initializes validity, and sets `last` to the sentinel value.
- `imgu_css_pool_cleanup()` frees every mapped entry.
- `imgu_css_pool_get()` advances to the oldest/recycled entry and marks it valid.
- `imgu_css_pool_put()` rolls back the most recent `get()` and invalidates that entry.
- `imgu_css_pool_last()` returns the nth valid map back from the current `last`, or a static null map when the slot is invalid.

## Control Flow
Pipeline setup initializes pools for parameter-set descriptors, accelerator data, GDC tables, OB grid, and per-memory late-binding parameter blocks. During parameter submission, the CSS core calls `imgu_css_pool_get()` for each block that needs a new generation. If configuration or queueing fails, `imgu_css_pool_put()` unwinds only the entries allocated for that failed submission. Consumers use `imgu_css_pool_last(pool, 0)` for current state and `imgu_css_pool_last(pool, 1)` for previous state.

## State and Persistence Behavior
Persistent streaming state is the pool ring itself: each entry has an `imgu_css_map` and a `valid` bit, and `last` tracks the newest valid generation. A static zeroed map from `imgu_css_pool_last()` represents "no previous/current value" without requiring callers to test for NULL. Pool entries persist until pipeline cleanup or binary cleanup frees their DMA maps.

## Dependencies and Integration Points
The implementation depends on `imgu_dmamap_alloc()` and `imgu_dmamap_free()` from the DMA mapping layer and on `struct imgu_device` from `ipu3.h`. It is used by the CSS parameter queueing path in `ipu3-css.c` and shares `struct imgu_css_map` with both firmware buffer handling and MMU mapping code.

## Risks
- `imgu_css_dma_buffer_resize()` only grows existing allocations and does not allocate when `map->vaddr` is NULL, so callers must initialize maps before relying on resize.
- `imgu_css_pool_last()` warns on `n >= IPU3_CSS_POOL_SIZE` but still computes an index; callers should treat the warning as a contract violation.
- There is no internal locking. Pool operations must remain serialized by higher-level CSS streaming/parameter control.
- Rollback correctness depends on callers pairing every successful `get()` in a failed submission with a matching `put()`.

## Test Signals
Tests should cover zero-size initialization, allocation failure cleanup, get/last/put ring ordering, retrieving invalid entries as a null map, and resizing to larger firmware parameter sizes without leaking the old map. Stress testing should submit more than four parameter generations while firmware dequeues old parameter buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-pool.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-pool.h

## Purpose
`ipu3-css-pool.h` defines the shared DMA map descriptor and fixed-size circular pool used for CSS firmware-visible buffers and parameter snapshots.

## Important APIs, Types, and Functions
- `IPU3_CSS_POOL_SIZE` is four entries.
- `struct imgu_css_map` stores byte size, kernel virtual address, IOVA DMA address, and the backing page array.
- `struct imgu_css_pool` stores four maps with validity flags plus a `last` write pointer.
- The header declares buffer resize, pool initialization/cleanup, ring get/put, and last-entry lookup helpers.

## Control Flow
CSS initialization allocates `imgu_css_map` objects for common ABI structures and initializes `imgu_css_pool` objects for streaming parameter generations. Parameter code advances pools before building a new ABI parameter set and rolls them back if queueing fails.

## State and Persistence Behavior
`struct imgu_css_map` is the common persistent descriptor tying kernel virtual memory to firmware-visible IOVA. `struct imgu_css_pool` persists several recent maps so omitted user parameters can be inherited and firmware can safely consume prior generations.

## Dependencies and Integration Points
This header is included by `ipu3-css.h`, `ipu3-css.c`, `ipu3-css-pool.c`, and `ipu3-dmamap.c`. It is a shared contract between CSS high-level state, DMA allocation, and parameter generation.

## Risks
The types expose raw memory addresses and page arrays; ownership is implicit. Double-free, stale map reuse, or using an invalid pool entry would directly affect firmware DMA. The fixed depth of four must remain sufficient for the firmware queueing behavior.

## Test Signals
Compile-time integration should validate all users agree on `struct imgu_css_map`. Runtime tests should confirm pool depth is enough under rapid parameter updates and that cleanup frees all map entries exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css.c

## Purpose
`ipu3-css.c` is the main IPU3 Camera Subsystem control layer. It negotiates formats and firmware binaries, powers and boots CSS hardware, allocates firmware-visible ABI structures, starts/stops streaming, queues and dequeues buffers through firmware queues, submits parameter sets, and acknowledges CSS interrupts.

## Important APIs, Types, and Functions
- Public V4L/CSS API: `imgu_css_init()`, `imgu_css_cleanup()`, `imgu_css_fmt_try()`, `imgu_css_fmt_set()`, `imgu_css_meta_fmt_set()`, `imgu_css_buf_queue()`, `imgu_css_buf_dequeue()`, `imgu_css_start_streaming()`, `imgu_css_stop_streaming()`, `imgu_css_queue_empty()`, `imgu_css_pipe_queue_empty()`, and `imgu_css_is_streaming()`.
- Hardware API: `imgu_css_set_powerup()`, `imgu_css_set_powerdown()`, and `imgu_css_irq_ack()`.
- Internal hardware helpers boot firmware (`imgu_css_hw_init()`, `imgu_css_hw_start_sp()`, `imgu_css_hw_start()`, `imgu_css_hw_stop()`, `imgu_css_hw_cleanup()`).
- Pipeline/memory helpers allocate and configure ABI structures (`imgu_css_map_init()`, `imgu_css_binary_preallocate()`, `imgu_css_binary_setup()`, `imgu_css_pipeline_init()`, cleanup counterparts).
- Queue helpers (`imgu_css_queue_data()`, `imgu_css_dequeue_data()`, `imgu_css_queue_pos()`) operate on SP DMEM host/SP queue rings.

## Control Flow
Initialization sets default pipe state, initializes disabled queues, allocates shared DMA structures for every pipe, allocates the SP group, and loads firmware metadata/binaries. Format negotiation builds temporary queues, clamps and aligns image sizes, derives effective/BDS/envelope/GDC rectangles, finds a compatible firmware binary, and writes adjusted values back to callers. Format setting repeats try logic and commits queue/rectangle state to the selected pipe.

Streaming startup first resizes binary-specific parameter and auxiliary frame maps for enabled pipes, initializes hardware registers and GDC LUTs, boots bootloader/SP firmware, builds each enabled pipeline ABI stage/group, marks streaming true, enables interrupts, submits default parameters, drains stale queues A/B, and sends start-stream events. Stop sends stop-stream events, halts firmware/hardware, cleans pipeline pools, marks outstanding queued buffers failed, and clears streaming.

Buffer queueing fills a per-queue ABI buffer with the user DMA address, records queue position, appends the buffer to the software list under `qlock`, queues the ABI buffer IOVA to firmware, and sends a buffer-enqueued event. Dequeue reads an event, maps event type to CSS queue, dequeues the firmware ABI buffer address, verifies it matches the software head and stored queue position, marks the buffer done, and removes it from the list.

Parameter submission advances pool entries, invokes `ipu3-css-params.c` to populate new/changed blocks, builds `imgu_abi_parameter_set_info` from current pool IOVAs, queues it to firmware queue A, sends the corresponding event, and drains old parameter buffers from queue A.

## State and Persistence Behavior
`struct imgu_css` persists device pointer, base registers, firmware image/header, mapped firmware binaries, streaming flag, enabled pipe bitmap, per-pipe state, and the shared SP group map. Each `struct imgu_css_pipe` persists format queues, rectangles, selected binary index, pipe id, queue lock, common ABI maps, binary parameter maps, auxiliary frame maps, parameter pools, and per-queue ABI buffer maps. Buffer software state is in per-queue linked lists and `enum imgu_css_buffer_state`.

## Dependencies and Integration Points
The file integrates with V4L2 format/meta APIs, PCI/device driver data (`struct imgu_device`), firmware parsing in `ipu3-css-fw.h`, parameter generation in `ipu3-css-params.h`, DMA/MMU mapping through `ipu3-dmamap.h`, static tables in `ipu3-tables.h`, and hardware register definitions from `ipu3.h`/ABI headers. It is interrupt-context aware for queue/dequeue operations and uses spinlocks for software queue lists.

## Risks
- `imgu_css_queue_empty()` initializes `ret` to `false` and then ANDs per-pipe results, so it will always return false; this is a likely functional bug for callers that depend on global empty detection.
- `imgu_css_buf_queue()` appends to the list before firmware queueing and calls `list_del()` on failure without holding `qlock`, creating a concurrency risk if failure can race with dequeue/stop.
- Streaming startup has many partial-allocation and firmware-boot failure paths; leaks or stale hardware state are possible if cleanup coverage diverges from allocation order.
- Queue correctness relies on firmware queue positions matching software FIFO order and stored ABI buffer maps; any firmware desynchronization becomes `-EIO`.
- Hardware register polling timeouts and firmware ABI drift can fail startup or shutdown, especially around power/runtime sequencing.

## Test Signals
Coverage should include format try/set for supported RAW10 inputs and NV12 outputs, no-input/no-output rejection, firmware binary selection boundaries, start/stop streaming with enabled pipes, parameter queue full rollback, buffer queue/dequeue FIFO matching, invalid event handling, IRQ ack with and without pending status, and cleanup after every injected allocation/startup failure. Hardware tests should monitor firmware warnings/asserts, SP/ISP idle transitions, queue drain behavior, and outstanding buffers becoming `FAILED` on stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css.h

## Purpose
`ipu3-css.h` defines the public CSS driver interface and the core state structures for IPU3 image processing. It describes pipe/queue IDs, CSS formats, buffer states, queue configuration, per-pipe firmware-visible memory, and the top-level CSS object.

## Important APIs, Types, and Functions
- Queue constants identify input, parameters, output, VF output, and 3A statistics queues.
- Rectangle constants identify effective, BDS, DVS envelope, and GDC output geometry.
- `enum imgu_css_pipe_id` and `enum imgu_css_buffer_state` model firmware pipe kinds and buffer lifecycle.
- `struct imgu_css_buffer`, `struct imgu_css_format`, `struct imgu_css_queue`, `struct imgu_css_pipe`, and `struct imgu_css` are the key state structures.
- Public functions cover init/cleanup, format negotiation, metadata format sizing, buffer queue/dequeue, streaming lifecycle, hardware power/IRQ, and parameter submission.
- Inline helpers expose buffer state and initialize CSS buffer metadata.

## Control Flow
External driver code configures queue formats and rectangles through `imgu_css_fmt_try()`/`imgu_css_fmt_set()`, initializes buffers with `imgu_css_buf_init()`, queues them while streaming, repeatedly dequeues completed buffers after interrupts/events, and submits `ipu3_uapi_params` through `imgu_css_set_parameters()`. Hardware power management uses the exported powerup/powerdown helpers around CSS runtime.

## State and Persistence Behavior
The header defines all long-lived CSS state. `struct imgu_css_pipe` stores per-pipe queue formats/lists, rectangle geometry, selected binary, stage maps, binary parameter maps, auxiliary frames, parameter pools, and ABI queue buffer maps. `struct imgu_css` stores firmware and global hardware state plus enabled pipes. Buffer state transitions from NEW to QUEUED to DONE or FAILED.

## Dependencies and Integration Points
The header pulls in V4L2 types, IPU3 ABI definitions, and the CSS pool definitions. It is the main contract between the IPU3 V4L2 driver, firmware loader, parameter builder, DMA mapper, and hardware control code.

## Risks
The structure layouts mix software-only locks/lists with firmware-visible DMA maps; misuse can expose stale IOVAs or inconsistent queue state to firmware. The API assumes callers honor streaming state, queue IDs, and pipe IDs. `imgu_css_buf_init()` only resets local metadata and does not initialize the list head, so callers must ensure list usage is valid before queueing.

## Test Signals
Compile tests should catch ABI/type drift. Runtime tests should exercise every public function's state preconditions, buffer state transitions, metadata buffer size constants, and per-pipe isolation when multiple pipes are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-dmamap.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-dmamap.c

## Purpose
`ipu3-dmamap.c` provides CSS buffer allocation and IOVA mapping on top of the IPU3 private MMU and Linux IOVA allocator. It allocates highmem-capable backing pages, maps them into the IPU3 MMU aperture, vmaps them for CPU access when needed, and maps external scatterlists for user/video buffers.

## Important APIs, Types, and Functions
- `imgu_dmamap_alloc()` allocates pages, reserves IOVA space, maps every page with `imgu_mmu_map()`, vmaps the pages, and fills `struct imgu_css_map`.
- `imgu_dmamap_free()` unmaps the IOVA, unmaps the kernel virtual address, frees backing pages, and clears `vaddr`.
- `imgu_dmamap_map_sg()` validates and maps a scatterlist into a contiguous IPU3 IOVA range.
- `imgu_dmamap_unmap()` releases an existing IOVA/MMU mapping.
- `imgu_dmamap_init()` and `imgu_dmamap_exit()` manage the IOVA domain and global IOVA cache reference.
- Local helpers allocate/free the page array and backing pages, using high-order allocations opportunistically.

## Control Flow
Internal CSS allocations call `imgu_dmamap_alloc()`: reserve an IOVA extent, allocate pages, map each page into the IPU3 MMU, vmap pages for CPU writes, then store size/IOVA/pages/vaddr. Failure unwinds mapped pages and IOVA reservations. External buffer mapping validates page alignment and total size, reserves IOVA, delegates scatter-gather PTE population to `imgu_mmu_map_sg()`, and records only IOVA/size because no CPU vmap or page ownership is taken.

## State and Persistence Behavior
Mapping state lives in `struct imgu_css_map`. Allocated buffers own `pages` and `vaddr`; scatterlist mappings only record device IOVA and size. The IOVA domain persists in `struct imgu_device` between `imgu_dmamap_init()` and `imgu_dmamap_exit()`. Freeing sets `vaddr` to NULL but leaves other fields stale unless overwritten by later allocation.

## Dependencies and Integration Points
The code depends on Linux IOVA helpers, `vmap()`/`vunmap()`, highmem page allocation, scatterlist iteration, `struct imgu_device`, `struct imgu_css_map`, and the IPU3 MMU functions in `ipu3-mmu.c`. CSS pools, firmware binary maps, ABI buffers, and video buffer mapping all use this layer.

## Risks
- `imgu_dmamap_map_sg()` does not call `imgu_mmu_unmap()` if `imgu_mmu_map_sg()` maps only a prefix then returns less than requested; `imgu_mmu_map_sg()` performs its own unwind on error, so this relies on that contract.
- `imgu_dmamap_unmap()` warns and returns if the IOVA is not found, which can leak MMU mappings if the domain and map state diverge.
- Page allocation uses high-order fallbacks and manual split/free logic; partial failure paths must stay correct to avoid leaks.
- Scatterlist inputs must have zero offsets and page-aligned intermediate lengths, or mapping is rejected.
- `imgu_dmamap_free()` uses `vaddr` as the ownership test, so scatterlist mappings must be unmapped with `imgu_dmamap_unmap()`, not `imgu_dmamap_free()`.

## Test Signals
Tests should inject allocation failures after IOVA reservation, after page allocation, during page-by-page MMU mapping, and during `vmap()`. Scatterlist tests should cover invalid offsets, non-aligned intermediate lengths, short final lengths, successful map/unmap, and MMU-map failure unwind. Leak checks should validate IOVA domain state and backing page release after CSS cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-dmamap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-dmamap.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-dmamap.h

## Purpose
`ipu3-dmamap.h` declares the DMA mapping facade used by CSS code to allocate internal firmware-visible buffers and map external scatterlists into the IPU3 MMU aperture.

## Important APIs, Types, and Functions
- `imgu_dmamap_alloc()` / `imgu_dmamap_free()` own internally allocated, CPU-vmapped buffers.
- `imgu_dmamap_map_sg()` / `imgu_dmamap_unmap()` map externally owned scatterlists.
- `imgu_dmamap_init()` / `imgu_dmamap_exit()` manage the per-device IOVA domain.

## Control Flow
Probe/setup initializes the DMA map subsystem after MMU initialization. CSS allocation paths use alloc/free for internal structures; video-buffer paths use map_sg/unmap for buffer queues. Teardown releases the IOVA domain after all maps have been removed.

## State and Persistence Behavior
State is carried by the caller-provided `struct imgu_css_map` and the `imgu_device` IOVA domain. The header separates ownership-bearing allocations from borrowed scatterlist mappings.

## Dependencies and Integration Points
The header forward-declares `struct imgu_device` and `struct scatterlist` and relies on `struct imgu_css_map` from `ipu3-css-pool.h` being visible to users. It is the interface between CSS memory users and `ipu3-mmu.c`.

## Risks
The API is easy to misuse because both allocation and scatterlist mapping fill the same map type but have different cleanup functions. Callers must keep allocation ownership clear to avoid leaks or invalid frees.

## Test Signals
Compile and runtime tests should verify every alloc has free, every map_sg has unmap, and subsystem exit occurs only after all mappings are gone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-dmamap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-mmu.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-mmu.c

## Purpose
`ipu3-mmu.c` implements the IPU3 private two-level page-table MMU. It initializes dummy mappings, allocates L2 page tables on demand, maps/unmaps physical pages into the IPU3 IOVA aperture, invalidates hardware TLBs when powered, and handles suspend/resume register programming.

## Important APIs, Types, and Functions
- `struct imgu_mmu` stores device/register pointers, spinlock, dummy page/table state, L1/L2 page-table pointers, and public geometry.
- `imgu_mmu_init()` allocates dummy page, dummy L2 table, L2 pointer array, L1 table, writes the L1 physical pointer register, invalidates TLB, unhalts memory access, and returns `struct imgu_mmu_info`.
- `imgu_mmu_map()`, `imgu_mmu_map_sg()`, and `imgu_mmu_unmap()` are exported mapping operations.
- `imgu_mmu_exit()`, `imgu_mmu_suspend()`, and `imgu_mmu_resume()` manage hardware halt/TLB/register state.
- Internal helpers split IOVA addresses, allocate/free uncached page tables, lazily install L2 tables, and write individual PTEs.

## Control Flow
Initialization halts external memory access before page tables exist, creates dummy mappings because the hardware lacks a valid bit, programs the L1 table address, invalidates TLB, and clears halt. Mapping checks alignment, then maps one 4 KiB IPU3 page at a time. `__imgu_mmu_map()` lazily allocates an L2 table for the L1 index, verifies the target PTE still points at the dummy page, and writes the physical page frame. Scatterlist mapping iterates entries, page-aligns the final length when needed, maps each segment, and unmaps the prefix on error. Unmap replaces PTEs with the dummy page value until it reaches an unmapped entry or requested size.

## State and Persistence Behavior
Page-table state persists in CPU memory marked uncached with `set_memory_uc()`. The `l2pts` array records allocated L2 CPU pointers; the L1 table stores physical PTEs to either dummy L2 or real L2 tables. Invalid pages point to the dummy page. Hardware state includes the L1 physical register, TLB contents, and GP halt state. Suspend halts memory access; resume reprograms L1, invalidates TLB, and unhalts.

## Dependencies and Integration Points
This file depends on Linux DMA, polling, runtime PM, slab/vmalloc allocation, x86 memory attribute helpers, scatterlist page access, and IPU3 register definitions local to the file. It is consumed by `ipu3-dmamap.c`, which handles IOVA allocation and page ownership.

## Risks
- `imgu_mmu_map()` can return after partially mapping pages if a later PTE is busy or allocation fails; callers must unmap the prefix when needed. `imgu_dmamap_alloc()` does this for internal allocations.
- `imgu_mmu_unmap()` stops at the first dummy/unmapped PTE, so fragmented or inconsistent unmaps may leave later PTEs mapped.
- TLB invalidation is skipped when runtime PM reports the device is off; correctness relies on resume/startup invalidating before use.
- Page tables are set uncached and restored write-back on free; architecture assumptions matter.
- The dummy page strategy means invalid IOVA accesses hit real memory, reducing fault visibility.

## Test Signals
Tests should cover aligned/unaligned map and unmap arguments, busy-PTE mapping failures, scatterlist partial-failure unwind, repeated map/unmap cycles, suspend/resume retaining mappings, runtime-PM-off mapping followed by resume, and exit after all dynamic L2 tables have been allocated. Hardware tests should watch for TLB stale translations and CIO gate halt timeout messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-mmu.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-mmu.h

## Purpose
`ipu3-mmu.h` declares the IPU3 private MMU interface and aperture geometry used by the DMA mapping layer.

## Important APIs, Types, and Functions
- `IPU3_PAGE_SHIFT` and `IPU3_PAGE_SIZE` define the 4 KiB page granularity.
- `struct imgu_mmu_info` exposes the IOVA aperture start and end.
- `imgu_mmu_init()` / `imgu_mmu_exit()` allocate and destroy MMU state.
- `imgu_mmu_suspend()` / `imgu_mmu_resume()` handle power-management transitions.
- `imgu_mmu_map()`, `imgu_mmu_unmap()`, and `imgu_mmu_map_sg()` expose mapping primitives.

## Control Flow
The device driver initializes the MMU with a parent device and mapped register base, then initializes the DMA-map IOVA domain from the returned aperture. DMA mapping code reserves IOVA ranges and calls the map/unmap functions for allocated pages or scatterlists. Power-management paths call suspend/resume around hardware power transitions.

## State and Persistence Behavior
The public state is only aperture geometry; implementation-private page tables are hidden behind `struct imgu_mmu_info`. Mappings persist until explicitly unmapped or the MMU is exited.

## Dependencies and Integration Points
The header forward-declares Linux device and scatterlist types and uses DMA/physical address types. It is included by `ipu3-dmamap.c` and any IPU3 device setup/teardown code that owns the MMU lifecycle.

## Risks
All mappings must be 4 KiB aligned. The API returns byte counts for unmap/map_sg and error codes for map, so callers must interpret each function's return convention correctly. Calling map/unmap before successful init or after exit would dereference invalid private state.

## Test Signals
Integration tests should confirm the DMA-map layer initializes the IOVA domain from aperture geometry, respects 4 KiB alignment, and unwinds mappings before MMU exit. PM tests should verify mappings survive suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-mmu.h -->
