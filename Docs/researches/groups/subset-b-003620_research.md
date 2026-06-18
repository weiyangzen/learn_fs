# Research Report: subset-b-003620

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/handlers.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/handlers.c

## Purpose
`handlers.c` is the central MMIO policy table and special-register emulator for Intel GVT-g vGPUs. It converts the i915 MMIO table into GVT-tracked register metadata, overlays device/platform-specific handlers, and implements the guest-visible side effects that cannot be represented by plain virtual-register storage. It covers display, interrupts, forcewake, fences, ring control, PV info, DP AUX/DPCD, power/PLL registers, execlist enablement, reset, and selected command-accessible registers.

## Important APIs, Types, And Functions
The exported entry points are `intel_gvt_get_device_type`, `intel_gvt_render_mmio_to_engine`, `intel_gvt_find_mmio_info`, `intel_gvt_setup_mmio_info`, `intel_gvt_clean_mmio_info`, `intel_gvt_for_each_tracked_mmio`, `intel_vgpu_default_mmio_read`, `intel_vgpu_default_mmio_write`, `intel_vgpu_mask_mmio_write`, `intel_vgpu_mmio_reg_rw`, `intel_gvt_restore_fence`, and `intel_gvt_restore_mmio`. Internal helpers include `setup_mmio_info`, `init_generic_mmio_info`, `init_bdw_mmio_info`, `init_skl_mmio_info`, `init_bxt_mmio_info`, `find_mmio_block`, and many register-specific callbacks.

The file builds on `struct intel_gvt_mmio_info`, `struct gvt_mmio_block`, GVT MMIO attributes such as `F_RO`, `F_MODE_MASK`, `F_GMADR`, `F_CMD_ACCESS`, `F_PM_SAVE`, and device masks from `mmio.h` (`D_BDW`, `D_SKL`, `D_BXT`, `D_CFL`, etc.). The `MMIO_*` macros are the declarative layer that assigns handlers and attributes to registers already discovered from the i915 MMIO table.

## Control Flow
Initialization starts in `intel_gvt_setup_mmio_info`: allocate `gvt->mmio.mmio_attribute`, enumerate the i915 MMIO table with `init_mmio_info`, assign the PV info block handler, then layer generic, Broadwell, Skylake/Kaby Lake/Coffee Lake/Comet Lake, and Broxton-specific registrations. Each `MMIO_*` entry calls `setup_mmio_info`, which validates device applicability, ensures the register was tracked, sets attributes and read/write callbacks, and stores read-only masks.

Runtime access is driven by `intel_vgpu_mmio_reg_rw`. It first checks for large special MMIO blocks such as the PV info page, then looks up per-register metadata in the hash table. Reads call the registered read callback. Writes enforce read-only masks and mode-mask semantics, then call the registered write callback. If no metadata exists, the access falls back to virtual-register read/write.

Several callbacks model hardware side effects: fence writes update the hardware fence; forcewake writes update virtual ACK registers; reset writes call `intel_gvt_reset_vgpu_locked`; ring mode writes validate PV notification and start execlist scheduling; ELSP writes assemble four dwords before submitting workloads; DP AUX writes emulate native DPCD reads/writes and link training; plane-surface writes update live surface and flip counters; `pvinfo_mmio_write` handles guest-to-vGVT notifications and display-ready uevents.

## State And Persistence
Persistent per-vGPU state is stored in `vgpu->mmio.vreg`, PV notification flags, display port/DPCD data, flip-done bitmaps, vGPU fence state, hardware status page addresses, SBI register cache, and submission/execlist fields. Global GVT state includes the MMIO info hash table, MMIO block array, attribute array, number of tracked MMIOs, and device-specific type masks. Power-management restore state is encoded through `F_PM_SAVE` and restored by `intel_gvt_restore_mmio`; fences are restored separately by `intel_gvt_restore_fence`.

`enter_failsafe_mode` flips `vgpu->failsafe` and is used when the guest accesses unsupported or unsafe semantics, such as out-of-range fences before PV notification, unsupported PPGTT/run-list setup without PV info, or disallowed masked register bits.

## Dependencies And Integration Points
This file integrates with i915 display and GT register definitions, GVT GTT and workload submission, interrupt emulation (`intel_vgpu_reg_*_handler`, `intel_vgpu_trigger_virtual_event`), I2C/DP helpers, PV info (`i915_pvinfo.h`), scheduler policy (`intel_vgpu_start_schedule`), hardware access wrappers (`mmio_hw_access_pre/post`), and uncore register access. It is called from `mmio.c` for every emulated MMIO access and from `kvmgt.c` through VFIO BAR0 reads/writes.

## Risks
The main risk is semantic drift from real hardware or from upstream i915 register definitions. Many handlers encode exact sticky-bit, mask-bit, PLL-lock, power-state, and interrupt side effects; a missed register or stale bit definition can break guest drivers. Large block handling must not accidentally route PV info through raw hardware-like storage. The failsafe path intentionally trades functionality for containment, so false positives can disable a guest. DP AUX and DPCD emulation has bounds checks, but malformed transactions still stress offset/length handling. `intel_gvt_for_each_tracked_mmio` iterates both hash and block regions, so restore behavior depends on correct `F_PM_SAVE` attributes.

## Test Signals
Useful signals include successful GVT initialization without duplicate/non-tracked MMIO warnings, guest boot past PV info probing, execlist workload submission after ring-mode writes, display hotplug and DP AUX link-training success, vblank/flip-done delivery, fence restore after suspend/resume, and no guest-triggered failsafe during supported driver flows. Negative tests should cover out-of-range fences, invalid FORCE_NONPRIV writes, unsupported GuC DMA start, malformed AUX lengths, and read-only/mode-mask writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/handlers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/interrupt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/interrupt.c

## Purpose
`interrupt.c` implements virtual interrupt register semantics for Intel GVT-g. It maps guest-visible interrupt events to virtual ISR/IIR/IMR/IER register groups, propagates downstream interrupt bits to upstream master groups, and injects MSI notifications into the guest through VFIO/KVM eventfd.

## Important APIs, Types, And Functions
Key public functions are `intel_gvt_init_irq`, `intel_vgpu_trigger_virtual_event`, `intel_vgpu_reg_imr_handler`, `intel_vgpu_reg_master_irq_handler`, `intel_vgpu_reg_ier_handler`, and `intel_vgpu_reg_iir_handler`. The file defines private `struct intel_gvt_irq_info` for each interrupt register group and `struct intel_gvt_irq_map` for upstream/downstream relationships. Gen8+ setup uses `gen8_irq_map`, `gen8_init_irq`, `gen8_check_pending_irq`, and `gen8_irq_ops`.

## Control Flow
Initialization assigns `gen8_irq_ops`, points `irq->irq_map` at the Gen8 mapping, initializes every event with `handle_default_event_virt`, fills per-event bit/group mappings in `gen8_init_irq`, and calls `init_irq_map` to mark downstream relationships. Guest writes to IMR/IER/IIR/master registers update virtual registers and then call `check_pending_irq`.

When a vGPU event is raised through `intel_vgpu_trigger_virtual_event`, its virtual handler sets the appropriate IIR bit if the IMR bit is not masked. `gen8_check_pending_irq` walks groups that feed an upstream interrupt, updates master/parent bits, checks `GEN8_MASTER_IRQ_CONTROL`, and calls `inject_virtual_interrupt` when a pending master bit exists. MSI injection reads the virtual PCI MSI capability and signals `vgpu->msi_trigger` only when the vGPU is attached and MSI is enabled.

## State And Persistence
Per-GVT state is in `gvt->irq`: the ops table, active group table, event metadata, and map. Per-vGPU state is virtual interrupt register contents inside `vgpu->mmio.vreg`, plus `vgpu->irq.irq_warn_once` and MSI eventfd state owned by KVMGT. IIR writes clear bits, IMR/IER writes alter masking/enabling, and upstream bits are recomputed from downstream `IIR & IER`.

## Dependencies And Integration Points
The file depends on register offsets from i915 display/interrupt headers, event names from `interrupt.h`, MMIO handlers installed by `handlers.c`, and eventfd signaling used by `kvmgt.c`. Display flip, vblank, AUX, render, blitter, video, PCH, and PCU events are triggered by other GVT subsystems through `intel_vgpu_trigger_virtual_event`.

## Risks
Interrupt correctness is highly sensitive to bit maps. A wrong event-to-bit assignment or upstream mask can cause stuck interrupts, missing vblank/flip events, or excess MSI injection. `inject_virtual_interrupt` assumes only one MSI vector and ignores unattached vGPUs, which is intentional but can mask sequencing bugs during VM teardown/reuse. Register write handlers assume 32-bit data and are normally reached through validated MMIO paths.

## Test Signals
Expected signals include guest-observed MSI only after enabling MSI and master IRQ, IIR bits clearing on guest write-one-to-clear, masked events not propagating, enabled downstream groups setting master bits, vblank/flip/AUX events reaching the guest, and no warnings from `regbase_to_irq_info`. Suspend/resume and VM restart should not inject through stale `msi_trigger`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/interrupt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/interrupt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/interrupt.h

## Purpose
`interrupt.h` declares the interrupt virtualization contract shared by MMIO handlers, display emulation, workload submission, and the KVMGT backend. It enumerates all virtual events that GVT can raise and defines the metadata structures used by `interrupt.c`.

## Important APIs, Types, And Functions
The central type is `enum intel_gvt_event_type`, covering render/video/blitter/VECS command events, display pipe events, flip done events, PCH hotplug/AUX events, PCU events, and reserved/max sentinels. `gvt_event_virt_handler_t` is the event handler callback. `struct intel_gvt_irq_ops` abstracts initialization and pending-check logic. `struct intel_gvt_event_info` stores event bit, register group, and handler. `struct intel_gvt_irq` stores the active IRQ model.

Exported functions include `intel_gvt_init_irq`, `intel_vgpu_trigger_virtual_event`, generic virtual IRQ register handlers, and ring-id conversion helpers for pipe-control, flush, and user-interrupt events.

## Control Flow
The header itself has no executable flow. Consumers initialize `struct intel_gvt_irq`, register its event mappings, then raise events by enum. MMIO handlers use the declared `intel_vgpu_reg_*_handler` callbacks for guest writes to interrupt registers.

## State And Persistence
The declared state is per-device IRQ metadata, not per-guest saved data. Runtime persistence happens in `vgpu->mmio.vreg` and in `struct intel_gvt_irq` arrays allocated as part of the `intel_gvt` device.

## Dependencies And Integration Points
It includes only `linux/bitops.h` and forward-declares GVT structs to keep dependencies light. `handlers.c` uses the handler prototypes, `interrupt.c` fills the structures, and display/workload paths use event enums.

## Risks
Adding, reordering, or removing event enum entries affects event mapping tables and derived macros such as flip-event calculations in `reg.h`. `INTEL_GVT_EVENT_MAX` must continue to bound every per-event array. Helper declarations must match implementations; missing implementation would surface at link time.

## Test Signals
Compile coverage is the primary signal. Runtime signals include correct mapping of ring IDs to events, no out-of-bounds event accesses, and successful guest interrupt handling for every event raised by display and workload code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/interrupt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/kvmgt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/kvmgt.c

## Purpose
`kvmgt.c` is the KVM/VFIO mediated-device backend for Intel GVT-g. It exposes a vGPU as a VFIO PCI-like device, routes userspace reads/writes/mmap/ioctls to GVT emulation, manages custom opregion and EDID regions, registers KVM page tracking, pins and DMA-maps guest pages, owns the GVT service thread, and registers the module-level GVT ops.

## Important APIs, Types, And Functions
Private types include `struct vfio_region`, `struct vfio_edid_region`, `struct kvmgt_pgfn`, and `struct gvt_dma`. Device-facing ops are collected in `intel_vgpu_dev_ops`; mdev-facing ops are in `intel_vgpu_mdev_driver`; GVT core integration is in `intel_gvt_vgpu_ops`.

Important functions include `intel_vgpu_probe/remove`, `intel_vgpu_init_dev/release_dev`, `intel_vgpu_open_device/close_device`, `intel_vgpu_read/write/mmap/ioctl`, `intel_vgpu_ioctl_get_region_info`, `intel_gvt_set_opregion`, `intel_gvt_set_edid`, `intel_gvt_page_track_add/remove`, `intel_gvt_dma_map_guest_page`, `intel_gvt_dma_pin_guest_page`, `intel_gvt_dma_unmap_guest_page`, `intel_gvt_init_device`, `intel_gvt_clean_device`, `intel_gvt_pm_resume`, `kvmgt_init`, and `kvmgt_exit`.

## Control Flow
Module load calls `kvmgt_init`, installs `intel_gvt_vgpu_ops` into the i915 GVT core, and registers the mdev driver. i915 GVT initialization calls `intel_gvt_init_device`, which allocates `struct intel_gvt`, initializes IDs/locks/device info, sets up MMIO, engine MMIO context, firmware, IRQs, GTT, workload scheduler, scheduling policy, command parser, service thread, vGPU types, idle vGPU, debugfs, and mdev parent registration.

When userspace creates an mdev, `intel_vgpu_probe` allocates a VFIO emulated IOMMU device. VFIO `.init` creates the actual vGPU from its type config and initializes page-protection/DMA caches. `.open_device` rejects attaching two vGPUs from the same KVM, registers KVM page tracking, marks the vGPU attached, creates debugfs state, and activates the vGPU. `.close_device` releases the vGPU, unregisters page tracking, destroys write-protect and DMA caches, and releases MSI eventfd.

VFIO read/write paths decode the VFIO PCI region index. Config space goes to config emulation, BAR0 goes to MMIO emulation, BAR2 accesses the aperture with IO mappings, and custom regions call opregion/EDID region ops. `mmap` only supports shared BAR2 aperture mappings. `ioctl` handles VFIO device info, region info, IRQ setup, reset, plane query, and dmabuf retrieval.

## State And Persistence
Persistent state includes per-vGPU VFIO device fields, custom region array, MSI trigger eventfd, protected-GFN hash table, DMA mapping rbtrees keyed by GFN and DMA address, cache entry refcounts, debugfs counters, and KVM page-track notifier state. Global GVT state includes the service thread, waitqueue, service request bits, vGPU IDR, type definitions, idle vGPU, and mdev parent registration. DMA cache entries pin guest pages and must be released on vfio DMA unmap, vGPU close, or explicit unmap.

## Dependencies And Integration Points
This file depends on VFIO, mdev, KVM page tracking, eventfd, DMA mapping APIs, debugfs, i915/GVT core operations, GTT, display/dmabuf helpers, MMIO/config emulation, and scheduler/service requests. It is the bridge between QEMU/VFIO userspace and the internal GVT emulators implemented in the neighboring files.

## Risks
Guest memory mapping is the highest-risk area. `gvt_pin_guest_page` requires contiguous PFNs for compound mappings and must unwind partial pins correctly. DMA cache refcounts must stay balanced across map, pin, VFIO unmap, and close paths. Page-track state is protected by `vgpu_lock` and mirrored in a local hash; missed removal can cause stale write protection. Region index arithmetic and sparse mmap caps must remain consistent with VFIO ABI. Lifecycle error paths in `intel_gvt_init_device` are long and order-sensitive.

## Test Signals
Signals include successful mdev type listing and availability counts, vGPU create/open/close cycles without cache leaks, VFIO config/BAR0/BAR2 access working, BAR2 mmap restricted to the aperture, MSI eventfd delivery, EDID link up/down hotplug behavior, opregion region reads, KVM page-track callbacks on protected GFNs, DMA map/unmap refcount balance, service thread scheduling/vblank handling, suspend/resume restoring fence/MMIO/GGTT state, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/kvmgt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio.c

## Purpose
`mmio.c` is the front door for guest MMIO and GGTT MMIO emulation. It translates guest physical addresses into BAR0 offsets, validates access size/alignment/ranges, dispatches GGTT accesses to GTT emulation, dispatches tracked MMIO accesses to `handlers.c`, and owns allocation/reset/free of each vGPU's virtual MMIO register image.

## Important APIs, Types, And Functions
Public functions are `intel_vgpu_gpa_to_mmio_offset`, `intel_vgpu_emulate_mmio_read`, `intel_vgpu_emulate_mmio_write`, `intel_vgpu_reset_mmio`, `intel_vgpu_init_mmio`, and `intel_vgpu_clean_mmio`. Private helpers include `reg_is_mmio`, `reg_is_gtt`, and `failsafe_emulate_mmio_rw`.

## Control Flow
Reads and writes first check `vgpu->failsafe`. Failsafe mode takes the vGPU lock, computes BAR0 offset, and performs minimal virtual-register or virtual-GGTT memory copying. Normal mode locks `vgpu->vgpu_lock`, computes the offset, validates access width, determines whether the offset is in the GGTT aperture or MMIO range, dispatches to `intel_vgpu_emulate_ggtt_mmio_read/write` for GGTT entries, or calls `intel_vgpu_mmio_reg_rw` for MMIO registers. Successful MMIO accesses mark the register as accessed through `intel_gvt_mmio_set_accessed`.

`intel_vgpu_reset_mmio` copies firmware-captured MMIO defaults into `vgpu->mmio.vreg`. Device-model-level reset restores the full MMIO image and adjusts status bits such as GT core status, GuC reset, and Broxton PHY/power defaults. Non-DMLR reset copies only the engine-related prefix up to `0x44200`.

## State And Persistence
The main state is `vgpu->mmio.vreg`, a `vzalloc` buffer sized by `gvt->device_info.mmio_size`. Reset seeds it from `gvt->firmware.mmio`. The function also touches virtual GGTT memory in failsafe mode and relies on GVT device info fields such as `gtt_start_offset`, `mmio_size`, and GGTT size.

## Dependencies And Integration Points
`kvmgt.c` calls these functions for BAR0 access. `handlers.c` provides `intel_vgpu_mmio_reg_rw` and default handlers. GTT emulation provides GGTT MMIO reads/writes. Firmware loading supplies the MMIO reset image. i915 register headers supply Broxton and GT status constants.

## Risks
Address validation must correctly distinguish MMIO, GGTT, and out-of-range GPA accesses. Alignment checks intentionally allow known unaligned MMIO only when GVT metadata says so. Failsafe mode is permissive and bypasses most semantic handlers, so it must be entered only for containment cases. Reset behavior is platform-specific and can leave stale state if firmware defaults or hardcoded offsets drift.

## Test Signals
Signals include correct BAR0 MMIO/GGTT routing from VFIO, warnings on invalid widths or ranges, successful vGPU reset to expected virtual register defaults, Broxton power/PHY default bits after reset, GGTT 4- and 8-byte accesses working, no lock inversions around `vgpu_lock`, and failsafe accesses not crashing after unsupported guest behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio.h

## Purpose
`mmio.h` declares the GVT MMIO emulation interface and device-generation masks used by the handler table. It is the shared contract between BAR access, MMIO handler setup, power-management restore, and vGPU MMIO allocation/reset.

## Important APIs, Types, And Functions
The header defines device masks `D_BDW`, `D_SKL`, `D_KBL`, `D_BXT`, `D_CFL`, aggregate masks such as `D_GEN9PLUS`, and `D_ALL`. `gvt_mmio_func` is the common callback signature for register handlers. `struct intel_gvt_mmio_info` stores offset, read-only mask, read/write callbacks, and hash-list node.

Declared functions cover device type detection, render-MMIO-to-engine mapping, MMIO metadata setup/cleanup/iteration, lookup, vGPU MMIO init/reset/cleanup, GPA translation, read/write emulation, default handlers, masked writes, and PM restore helpers.

## Control Flow
The header has no executable flow. It defines how `mmio.c`, `handlers.c`, `mmio_context.c`, and `kvmgt.c` exchange MMIO operations and metadata.

## State And Persistence
The declared structures persist in `gvt->mmio.mmio_info_table`; virtual register contents persist separately in `vgpu->mmio.vreg`. The generation masks constrain which handlers are installed for the active hardware generation.

## Dependencies And Integration Points
This header includes `linux/types.h` and forward-declares GVT structs. It is consumed by most GVT files that touch MMIO and by platform setup code that needs the device mask constants.

## Risks
Changing callback signatures or generation masks can silently mis-register handlers across hardware families. The aggregate masks must stay synchronized with `intel_gvt_get_device_type` and supported platforms. `struct intel_gvt_mmio_info` is hash-table storage, so layout changes affect setup and cleanup.

## Test Signals
Compile coverage across GVT is the first signal. Runtime signals include platform-specific handler registration matching the active device type and successful MMIO init/read/write/reset/restore paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio_context.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio_context.c

## Purpose
`mmio_context.c` saves, restores, and switches engine-related MMIO context when ownership moves between host and vGPU workloads. It also restores context-inhibited state through command-stream LRI packets and handles MOCS and TLB-invalidate state across engines.

## Important APIs, Types, And Functions
The public functions are `intel_gvt_switch_mmio`, `intel_gvt_init_engine_mmio_context`, `is_inhibit_context`, and `intel_vgpu_restore_inhibit_context`. Private data includes `struct engine_mmio`, Gen8/Gen9 engine MMIO lists, Gen9 render MOCS tables, MOCS offset lists, and TLB invalidate offset lists.

Important helpers are `load_render_mocs`, `restore_context_mmio_for_inhibit`, `restore_render_mocs_control_for_inhibit`, `restore_render_mocs_l3cc_for_inhibit`, `handle_tlb_pending_event`, `switch_mocs`, and `switch_mmio`.

## Control Flow
Initialization chooses Gen8 or Gen9 MMIO lists, assigns TLB and MOCS offset arrays, counts in-context MMIOs per engine, and marks those registers as save/restore-in-context in GVT MMIO metadata. At runtime `intel_gvt_switch_mmio` forcewakes all domains, calls `switch_mmio`, and releases forcewake.

`switch_mmio` saves current hardware register values into the previous vGPU or host shadow, restores values for the next vGPU or host, skips Gen9 registers that live in normal context state unless the context restore-inhibit bit requires manual restoration, switches MOCS when needed, and handles pending per-engine TLB invalidation. `intel_vgpu_restore_inhibit_context` emits MI commands into an i915 request: disable arbitration, load tracked context MMIOs, load render MOCS/L3CC for RCS, then re-enable arbitration.

## State And Persistence
Per-vGPU MMIO context values live in `vgpu->mmio.vreg`; host baseline values are cached in `engine_mmio.value` and `gen9_render_mocs`. Pending TLB invalidations are recorded in `vgpu->submission.tlb_handle_pending`. `gvt->engine_mmio_list` stores the active register lists and per-engine counts. The code mutates hardware registers through uncore writes during context switches.

## Dependencies And Integration Points
This file integrates with i915 engine/context/request/ring APIs, uncore forcewake, GVT submission shadow contexts, MMIO metadata marking from `handlers.c`, and tracepoints. The scheduler calls `intel_gvt_switch_mmio` when engine ownership changes, and MMIO handlers set TLB pending bits that this file consumes.

## Risks
Incorrect save/restore ordering can leak register state between vGPUs or host workloads. Forcewake domains must cover raw MMIO reads/writes. Gen9 in-context register skipping depends on accurate `is_inhibit_context` detection. MOCS handling is special: RCS Gen9 render MOCS are initialized by command stream for inhibit contexts, while non-RCS MOCS are switched directly. TLB invalidation waits can time out and affect guest address translation correctness.

## Test Signals
Signals include stable workload execution while switching between vGPUs and host, no register leakage across vGPU boundaries, successful inhibit-context requests, MOCS values preserved after switches, pending TLB bits cleared after invalidation, no forcewake warnings, and trace output showing expected old/new MMIO values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio_context.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio_context.h

## Purpose
`mmio_context.h` declares the render/engine MMIO context-switch interface for GVT. It lets scheduler and submission code switch engine MMIO ownership and restore manually loaded state for contexts that inhibit normal hardware restoration.

## Important APIs, Types, And Functions
The header forward-declares `struct i915_request`, `struct intel_context`, `struct intel_engine_cs`, `struct intel_gvt`, and `struct intel_vgpu`. It declares `intel_gvt_switch_mmio`, `intel_gvt_init_engine_mmio_context`, `is_inhibit_context`, and `intel_vgpu_restore_inhibit_context`.

## Control Flow
There is no local control flow. Callers initialize engine MMIO context once per GVT device, switch MMIO on scheduling transitions, check inhibit status on contexts, and emit restore commands when needed.

## State And Persistence
The header exposes functions that operate on `gvt->engine_mmio_list`, `vgpu->mmio.vreg`, i915 context state, and request ring buffers, but it owns no state itself.

## Dependencies And Integration Points
It includes `linux/types.h` and otherwise relies on forward declarations. It is consumed by scheduler, submission, and initialization code that must avoid depending on `mmio_context.c` internals.

## Risks
The interface assumes callers pass valid engine/context/request objects and hold the scheduler/engine locks required by the implementation. Misuse can cause host/vGPU MMIO state leakage or command-stream corruption.

## Test Signals
Compile-time linkage and runtime scheduling transitions are the main signals. Inhibit-context workloads should execute with expected register state, and host transitions should restore non-vGPU values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/opregion.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/opregion.c

## Purpose
`opregion.c` creates and emulates the guest IGD OpRegion used by graphics drivers, especially Windows guests. It synthesizes a minimal OpRegion with a virtual VBT mailbox, records where the guest maps that OpRegion, and handles SWSCI OpRegion service requests.

## Important APIs, Types, And Functions
The public functions are `intel_vgpu_init_opregion`, `intel_vgpu_opregion_base_write_handler`, `intel_vgpu_clean_opregion`, and `intel_vgpu_emulate_opregion_request`. Private packed structures model the OpRegion header, BDB data header, a virtual child-device config, and `struct vbt`. Helpers include `virt_vbt_generation`, `querying_capabilities`, and name-formatting helpers for functions/subfunctions.

## Control Flow
Initialization allocates two zeroed pages, writes the `IntelGraphicsMem` OpRegion signature, sets version/size/mailbox fields, forces the LID field open, generates a virtual VBT, and copies it at `INTEL_GVT_OPREGION_VBT_OFFSET`. When the guest writes the OpRegion base register, `intel_vgpu_opregion_base_write_handler` records the two GFNs used by the guest mapping.

SWSCI emulation computes guest physical addresses for SCIC and PARM inside the guest OpRegion, reads them with `intel_gvt_read_gpa`, filters out SMI and non-trigger transitions, decodes function/subfunction, supports only capability queries, writes success-style zero SCIC/PARM for supported calls, or clears exit status for unsupported runtime services, then writes the fields back with `intel_gvt_write_gpa`.

## State And Persistence
Per-vGPU state is `vgpu_opregion(vgpu)->va` for the host-side template and `vgpu_opregion(vgpu)->gfn[]` for the guest-mapped pages. The generated VBT hardcodes DP child devices on ports A-D and no LVDS. The allocated pages live until `intel_vgpu_clean_opregion`.

## Dependencies And Integration Points
It depends on ACPI/OpRegion constants from `reg.h`, VBT structures from `display/intel_vbt_defs.h`, GVT guest memory access helpers, VFIO region exposure in `kvmgt.c`, and config/MMIO handlers that detect OpRegion base and SWSCI writes.

## Risks
The VBT is intentionally synthetic and hardcoded; guest driver expectations can change. The child-device structure is pegged to BDB version 186 sizing. SWSCI support is minimal and rejects runtime services, which is acceptable only if guest drivers tolerate capability-only behavior. Guest GFN recording must happen before SWSCI emulation or GPA reads/writes target invalid memory.

## Test Signals
Signals include valid opregion VFIO region reads, guest detection of OpRegion/VBT, Windows guest display initialization, correct GFN recording on base write, SWSCI capability queries returning success, unsupported runtime services failing without crashing, and no leaks on vGPU destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/opregion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/page_track.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/page_track.c

## Purpose
`page_track.c` is the GVT-side registry for guest page write tracking. It lets GVT subsystems register a handler for a guest frame number, enable/disable write protection through the backend, and dispatch KVM page-track write callbacks to the registered handler.

## Important APIs, Types, And Functions
Public functions are `intel_vgpu_find_page_track`, `intel_vgpu_register_page_track`, `intel_vgpu_unregister_page_track`, `intel_vgpu_enable_page_track`, `intel_vgpu_disable_page_track`, and `intel_vgpu_page_track_handler`. The runtime record type is `struct intel_vgpu_page_track` from `page_track.h`, with a callback, `tracked` flag, and private data pointer.

## Control Flow
Registration checks whether the GFN already exists in `vgpu->page_track_tree`, allocates a record, initializes handler/private data, and inserts it into the radix tree. Enabling looks up the record and calls backend `intel_gvt_page_track_add`; disabling calls `intel_gvt_page_track_remove`. Unregistering removes the radix-tree record, removes backend write protection if active, and frees it.

The dispatch path receives a GPA, looks up `gpa >> PAGE_SHIFT`, and either calls the registered handler or, in failsafe mode, removes backend write protection to avoid repeated traps.

## State And Persistence
State lives in `vgpu->page_track_tree`; each record persists until explicit unregister. The `tracked` flag mirrors whether KVM/backend write protection is active. Handler-specific state is external and referenced by `priv_data`.

## Dependencies And Integration Points
The file depends on the KVMGT backend functions `intel_gvt_page_track_add/remove` and on callers that initialize the vGPU radix tree. `kvmgt.c` invokes `intel_vgpu_page_track_handler` from the KVM page-track notifier under `vgpu_lock`.

## Risks
Radix-tree state and backend write-protection state must stay synchronized. Duplicate registration returns `-EEXIST`; enable/disable on unknown GFNs returns `-ENXIO`. In failsafe mode, write protection is removed without setting `tracked = false`, so subsequent local state may be stale unless the teardown path handles it. Handler failures are logged and propagated.

## Test Signals
Signals include successful register/enable/disable/unregister sequences, KVM write traps reaching the right handler, duplicate registration rejection, unknown GFN errors, backend protection table updates, failsafe trap suppression, and no leaked records after vGPU teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/page_track.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/page_track.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/page_track.h

## Purpose
`page_track.h` declares the GVT guest-page write-tracking interface. It abstracts the storage of per-GFN handlers from the KVMGT implementation that actually enables and receives write-protection traps.

## Important APIs, Types, And Functions
`gvt_page_track_handler_t` is the callback signature: it receives the page-track record, GPA, written data, and byte count. `struct intel_vgpu_page_track` stores the callback, backend-tracked state, and private data. The header declares find/register/unregister/enable/disable/dispatch functions.

## Control Flow
There is no executable flow in the header. Typical use is register a GFN, enable tracking, receive writes through `intel_vgpu_page_track_handler`, then disable/unregister during teardown.

## State And Persistence
The header defines the per-GFN state object stored by `page_track.c` in `vgpu->page_track_tree`. Persistence is per-vGPU and ends on unregister or vGPU teardown.

## Dependencies And Integration Points
It includes `linux/types.h`, forward-declares GVT objects, and is used by page-track users and KVMGT page-track callbacks.

## Risks
Callback implementations must tolerate arbitrary guest write sizes and offsets within a page. The `tracked` flag is a mirror of backend state, so callers should use the API rather than mutating records directly.

## Test Signals
Compile-time coverage and runtime write-trap delivery are the key signals. Tests should verify handler private data, enable/disable idempotence, and teardown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/page_track.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/reg.h

## Purpose
`reg.h` centralizes GVT-specific PCI, OpRegion, display, forcewake, ring-buffer, GMBUS, TRTT, and compatibility register constants that are not directly provided or stable in upstream i915 headers. It also defines helper macros used by MMIO handlers.

## Important APIs, Types, And Functions
Important constants include PCI offsets such as `INTEL_GVT_PCI_SWSCI` and `INTEL_GVT_PCI_OPREGION`, OpRegion offsets/sizes, flip-event helpers, `REG_50080` and reverse mapping macros, masked-bit helpers, forcewake register offsets, ring head/tail masks, PCH GMBUS/PPS offsets, TRTT registers, `RING_EXCC`, `RING_GFX_MODE`, and `VF_GUARDBAND`.

## Control Flow
The header has no functions. Its statement-expression macros compute register offsets, pipe/plane identities, masked-bit states, and ring-buffer sizes at compile time or inline runtime.

## State And Persistence
No state is owned here. Constants define how other files interpret virtual MMIO state and guest PCI/config/OpRegion state.

## Dependencies And Integration Points
`handlers.c`, `opregion.c`, and other GVT files rely on these constants for register emulation. Many macros depend on i915 register types such as `_MMIO`, `PIPE_*`, plane identifiers, and masked-field helpers supplied by included users.

## Risks
This file intentionally patches gaps where i915 definitions changed. Stale constants can break guest-visible behavior, especially OpRegion SWSCI decoding, flip-event mapping, forcewake ACK handling, and ring buffer interpretation. Statement-expression macros are GNU C-specific and assume compatible argument types.

## Test Signals
Signals include successful compilation against current i915 headers, correct flip event selection for primary/sprite writes, valid OpRegion size/offset handling, forcewake handler ACK updates, ring-buffer size calculations, and no mismatches with hardware register offsets used by guest drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/sched_policy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/sched_policy.c

## Purpose
`sched_policy.c` implements the default time-based scheduling policy for GVT vGPUs. It maintains an LRU run queue, balances per-vGPU time slices according to configured weights, gives newly started vGPUs a temporary priority window, selects the next busy vGPU or idle vGPU, and coordinates with the workload scheduler service thread.

## Important APIs, Types, And Functions
Public functions are `intel_gvt_schedule`, `intel_gvt_init_sched_policy`, `intel_gvt_clean_sched_policy`, `intel_vgpu_init_sched_policy`, `intel_vgpu_clean_sched_policy`, `intel_vgpu_start_schedule`, `intel_gvt_kick_schedule`, and `intel_vgpu_stop_schedule`. Private types are `struct vgpu_sched_data` and `struct gvt_sched_data`. The active ops table is `tbs_schedule_ops`.

Important helpers include `vgpu_has_pending_workload`, `vgpu_update_timeslice`, `gvt_balance_timeslice`, `try_to_schedule_next_vgpu`, `find_busy_vgpu`, `tbs_sched_func`, `tbs_timer_fn`, and the per-vGPU/global init/clean/start/stop functions.

## Control Flow
Global init allocates `gvt_sched_data`, initializes the run queue and high-resolution timer, and stores it in `gvt->scheduler.sched_data`. Per-vGPU init allocates `vgpu_sched_data` with the configured weight. Starting a vGPU inserts it into the LRU run queue, grants a two-second priority window, and starts the timer if inactive.

The timer periodically requests `INTEL_GVT_REQUEST_SCHED`. The service thread calls `intel_gvt_schedule`, which takes `sched_lock`, rebalances timeslices every 100 ms, clears event-schedule requests, accounts current vGPU time, and calls `tbs_sched_func`. Selection prefers vGPUs with pending workloads and either active priority time or positive remaining timeslice; otherwise it schedules the idle vGPU. `try_to_schedule_next_vgpu` waits until no current workloads are in flight, switches `current_vgpu`, and wakes per-engine dispatch waitqueues.

Stopping a vGPU removes it from the run queue, clears pending/current references, stops dispatch, switches any engine MMIO context it owns back to host, and clears engine ownership.

## State And Persistence
Global scheduling state includes `gvt->scheduler.current_vgpu`, `next_vgpu`, `need_reschedule`, per-engine `current_workload`, `engine_owner`, dispatch waitqueues, `sched_data`, and service request bits. Per-vGPU state includes active flag, priority scheduling flag/time, schedule-in timestamp, accumulated scheduled time, remaining and allocated timeslice, and scheduling weight. State is protected primarily by `gvt->sched_lock`; engine owner MMIO switching uses `mmio_context_lock`.

## Dependencies And Integration Points
The scheduler depends on workload queues, the GVT service thread in `kvmgt.c`, request bits, i915 runtime PM during stop, and `intel_gvt_switch_mmio` from `mmio_context.c`. MMIO ring-mode handlers start scheduling when execlist mode is enabled. Workload dispatchers consume `current_vgpu` and wake queues.

## Risks
Scheduling correctness depends on lock ordering and accurate workload-in-flight checks. `gvt_balance_timeslice` uses a static `stage_check`, which is shared across GVT instances. Weight totals must be nonzero when balancing. Stopping the current vGPU must restore MMIO context before host or another vGPU runs. Priority scheduling can temporarily bypass fairness by design.

## Test Signals
Signals include timer-driven scheduling requests, fair weighted runtime over time, immediate service after `intel_gvt_kick_schedule`, newly started vGPU priority behavior, idle vGPU selection when no work is pending, no dispatch while `need_reschedule` is set, clean engine MMIO switch-back on stop, and no hrtimer activity after all vGPUs are removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/sched_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/sched_policy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/sched_policy.h

## Purpose
`sched_policy.h` declares the scheduling-policy abstraction and public scheduler control functions for Intel GVT-g. It lets the workload scheduler invoke policy operations without depending on the concrete time-based implementation.

## Important APIs, Types, And Functions
`struct intel_gvt_sched_policy_ops` defines callbacks for global init/clean, per-vGPU init/clean, and per-vGPU start/stop scheduling. Public functions include `intel_gvt_schedule`, `intel_gvt_init_sched_policy`, `intel_gvt_clean_sched_policy`, `intel_vgpu_init_sched_policy`, `intel_vgpu_clean_sched_policy`, `intel_vgpu_start_schedule`, `intel_vgpu_stop_schedule`, and `intel_gvt_kick_schedule`.

## Control Flow
The header has no executable flow. The normal call sequence is initialize global policy during GVT device setup, initialize each vGPU policy state on vGPU creation, start scheduling when the guest enables workload submission, kick scheduling on events, stop scheduling during teardown, and clean all policy state during device removal.

## State And Persistence
The header declares operations that manipulate `gvt->scheduler.sched_ops`, `gvt->scheduler.sched_data`, and `vgpu->sched_data`; it owns no storage itself.

## Dependencies And Integration Points
It forward-declares `struct intel_gvt` and `struct intel_vgpu`. It is included by `sched_policy.c`, KVMGT initialization/cleanup, MMIO handlers that start scheduling, and workload scheduler code.

## Risks
The abstraction assumes the ops table is installed before per-vGPU calls. Missing callbacks or calls after cleanup will dereference invalid scheduler state. New policies must obey existing locking expectations around `gvt->sched_lock`.

## Test Signals
Compile-time coverage plus runtime vGPU create/start/kick/stop/destroy flows are the primary signals. A scheduler-policy replacement should pass the same workload dispatch and teardown tests as the time-based policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/sched_policy.h -->
