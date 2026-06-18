# Research: subset-b-003670

Grouped source research for subset B work item `subset-b-003670`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/falcon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/falcon.h

## Purpose

This header defines the core Falcon microcontroller service layer: IMEM/DMEM/EMEM transfer backends, Falcon reset/boot helpers, high-security firmware loading, and command/message queue management used by PMU, SEC2, GSP boot, video, and other firmware-backed engines.

## Important APIs, Types, and Functions

Important contracts include `enum nvkm_falcon_mem`, `struct nvkm_falcon_func_pio`, `struct nvkm_falcon_func_dma`, `struct nvkm_falcon_fw`, `struct nvfw_falcon_msg`, `nvkm_falcon_ctor`, `nvkm_falcon_reset`, `nvkm_falcon_pio_wr`, `nvkm_falcon_pio_rd`, `nvkm_falcon_dma_wr`, `nvkm_falcon_fw_ctor`, `nvkm_falcon_fw_oneinit`, `nvkm_falcon_fw_boot`, and the queue-manager APIs `nvkm_falcon_cmdq_send` and `nvkm_falcon_msgq_recv`.

## Control Flow

Callers construct a Falcon wrapper for a hardware engine, reset or select the unit, transfer firmware through PIO or DMA into IMEM/DMEM/EMEM, patch/sign high-security images when required, bind instance memory/VMM mappings, and then boot through mailbox handshakes. Queue users initialize firmware-advertised command and message rings, submit commands with callbacks and timeouts, and drain init or asynchronous messages.

## State and Persistence Behavior

The header describes persistent firmware image metadata, signature offsets, fuse/engine IDs, memory-window offsets, bootloader addresses, bound instance memory, VMM/VMA mappings, Falcon user ownership, and queue offsets. These fields are volatile driver state but they mirror persistent hardware microcode state until reset or teardown.

## Dependencies and Integration Points

It depends on `core/firmware.h`, `engine/falcon.h`, NVKM memory/VMM objects, subdev logging, and chip-specific implementations for GM200, GP102, TU102, GA100, and GA102. It is the bridge between generic firmware blobs and the engine-specific Falcon register programming.

## Risks

Incorrect IMEM/DMEM bounds, security flags, signature offsets, or mailbox success masks can leave firmware unbootable or silently boot the wrong image. Queue sequencing is timeout-sensitive and callback ownership must remain valid until replies arrive. RISC-V Falcon variants add reset and interrupt behavior that differs from classic Falcon units.

## Test Signals

Useful validation includes firmware load/boot on PMU/SEC2/GSP-backed engines, signature patch checks, secure and non-secure IMEM transfers, DMA-vs-PIO transfer fallback, timeout and mailbox failure injection, queue init-message receipt, and suspend/resume reset coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/falcon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/firmware.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/firmware.h

## Purpose

This header defines the NVKM firmware blob wrapper used to represent firmware stored in kernel RAM, DMA memory, or scatter-gather tables, plus helpers for locating versioned firmware files and selecting firmware loader variants from module options.

## Important APIs, Types, and Functions

Key elements are `struct nvkm_firmware`, `struct nvkm_firmware_func`, `enum nvkm_firmware_type`, `struct nvkm_firmware_mem`, `nvkm_firmware_ctor`, `nvkm_firmware_dtor`, `nvkm_firmware_get`, `nvkm_firmware_put`, `nvkm_firmware_load_blob`, `nvkm_firmware_load_name`, and the `nvkm_firmware_load()` selection macro.

## Control Flow

Drivers request a named or versioned firmware image, wrap it as an NVKM memory-like object, and later pass it to Falcon/GSP loaders or engine init code. The load macro first checks `Nv<name>Fw` to force a loader entry, then checks `Nv<name>FwVer`, iterates available loader versions, and stops on the first success or explicit requested version.

## State and Persistence Behavior

The wrapper owns image length, bytes, optional physical address, and DMA/SGT allocation state. Firmware contents remain immutable after construction and are released through the destructor or `nvkm_firmware_put`.

## Dependencies and Integration Points

It integrates Linux firmware loading with NVKM memory abstractions, `nvkm_blob`, driver config options, and subdevice logging. Falcon high-security firmware and GSP boot code consume this interface heavily.

## Risks

Option-driven loader selection can force unsupported versions; error pointers from the macro must be handled. DMA/SGT lifetime must outlive hardware transfer. Firmware path/version mismatches are runtime failures that normal build tests do not catch.

## Test Signals

Exercise missing firmware, forced firmware version options, RAM/DMA/SGT constructors, destructor cleanup under failure paths, and Falcon/GSP firmware boot on devices that require signed blobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/gpuobj.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/gpuobj.h

## Purpose

This file defines the GPU object contract for Nouveau/NVKM. It covers parented GPU-resident objects with optional child heaps, memory wrappers, register-style accessors, VMM map hooks, and memcpy helpers.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_gpuobj`, `nvkm_gpuobj_func`, `nvkm_memory`, `nvkm_mm_node`, `nvkm_mm`, `nvkm_vmm`, `nvkm_vma`, `nvkm_device`, `nvkm_gpuobj_new`, `nvkm_gpuobj_del`, `nvkm_gpuobj_wrap`, `nvkm_gpuobj_memcpy_to`, `nvkm_gpuobj_memcpy_from`, `NVOBJ_FLAG_ZERO_ALLOC`. Important callable entry points include `nvkm_gpuobj_new`, `nvkm_gpuobj_del`, `nvkm_gpuobj_wrap`, `nvkm_gpuobj_memcpy_to`, `nvkm_gpuobj_memcpy_from`. The visible chip-family constructors are `nvkm_gpuobj_new`; they bind the generic GPU object role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/gpuobj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/intr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/intr.h

## Purpose

This file defines the interrupt routing contract for Nouveau/NVKM. It covers interrupt source descriptors, leaf masks, subdevice handlers, priority queues, block/allow/reset hooks, and installed interrupt handles.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_subdev`, `nvkm_intr_prio`, `nvkm_intr_type`, `nvkm_intr`, `nvkm_intr_func`, `nvkm_intr_data`, `nvkm_subdev_type`, `list_head`, `nvkm_inth`, `nvkm_intr_ctor`, `nvkm_intr_dtor`, `nvkm_intr_install`, `nvkm_intr_unarm`. Important callable entry points include `nvkm_intr_ctor`, `nvkm_intr_dtor`, `nvkm_intr_install`, `nvkm_intr_unarm`, `nvkm_intr_rearm`, `nvkm_intr_add`, `nvkm_intr_block`, `nvkm_intr_allow`, `nvkm_inth_add`, `nvkm_inth_allow`. The file exposes the interrupt routing interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/intr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/ioctl.h

## Purpose

This file defines the NVKM ioctl dispatch contract for Nouveau/NVKM. It covers the low-level client ioctl entry point that receives packed user requests and may return an object pointer.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_client`, `nvkm_ioctl`. Important callable entry points include `nvkm_ioctl`. The file exposes the NVKM ioctl dispatch interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/layout.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/layout.h

## Purpose

This file defines the device layout contract for Nouveau/NVKM. It covers the macro-expanded map from subdevice/engine type to field name and struct type inside the generated NVKM device layout.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_fsp`, `nvkm_gsp`, `nvkm_top`, `nvkm_vfn`, `nvkm_pci`, `nvkm_bios`, `nvkm_devinit`, `nvkm_subdev`, `nvkm_gpio`, `nvkm_i2c`, `nvkm_fuse`, `nvkm_mc`, `nvkm_bus`, `nvkm_timer`. Important callable entry points include constructor/function declarations selected by including modules. The file exposes the device layout interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/layout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/memory.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/memory.h

## Purpose

This header defines the polymorphic NVKM memory object used for instance memory, VRAM, host coherent memory, and non-coherent host allocations. It provides reference counting, compression-tag accounting, mapping hooks, and register-style access helpers.

## Important APIs, Types, and Functions

Important contracts include `enum nvkm_memory_target`, `struct nvkm_memory`, `struct nvkm_memory_func`, `struct nvkm_memory_ptrs`, `struct nvkm_tags`, `nvkm_memory_new`, `nvkm_memory_ref`, `nvkm_memory_unref`, `nvkm_memory_tags_get`, `nvkm_memory_tags_put`, and access macros such as `nvkm_kmap`, `nvkm_done`, `nvkm_ro32`, `nvkm_wo32`, `nvkm_mo32`, `nvkm_robj`, `nvkm_wobj`, `nvkm_fo32`, and `nvkm_fo64`.

## Control Flow

Backends construct a memory object with function tables, callers map or kmap it through backend hooks, perform 32/64-bit access or bulk fill/copy, and release mappings before dropping references. VMM mapping routes through the `map` hook, while compression tags are leased and returned through the tag helpers.

## State and Persistence Behavior

The base object persists target type, page geometry, physical/BAR addresses supplied by callbacks, krefs, and optional compression tag references. The underlying memory can represent durable VRAM contents or transient instance memory that may be lost across suspend.

## Dependencies and Integration Points

It is used by GPU objects, firmware wrappers, VMM mappings, framebuffer tag allocation, RAM wrappers, and engine context storage. Correct acquire/release pairing is required because some backends expose I/O memory only while mapped.

## Risks

Using access macros outside `kmap`/`done` semantics can break on chipsets with special mapping requirements. Tag reference leaks affect compression resources. Wrong target/page reporting causes invalid PTE programming and data coherency bugs.

## Test Signals

Validate refcounting, kmap fallback paths, BAR2/addr/size reporting, memory fill/copy helpers, VMM map/unmap, compression-tag get/put, and suspend behavior for `INST_SR_LOST` versus preserved targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/mm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/mm.h

## Purpose

This header exposes NVKM's small range allocator for GPU-managed address spaces such as RAMHT slots, notifier heaps, VRAM heaps, tile/tag regions, and firmware-local heaps.

## Important APIs, Types, and Functions

The main types are `struct nvkm_mm` and `struct nvkm_mm_node`; APIs include `nvkm_mm_init`, `nvkm_mm_fini`, `nvkm_mm_head`, `nvkm_mm_tail`, `nvkm_mm_free`, `nvkm_mm_dump`, `nvkm_mm_heap_size`, `nvkm_mm_contiguous`, `nvkm_mm_addr`, and `nvkm_mm_size`.

## Control Flow

Callers initialize an allocator over an offset/length/block-size range, allocate from the head or tail with heap/type/size/alignment constraints, use returned node chains, then free them back into the allocator. Helpers verify whether allocations are contiguous before deriving a single address.

## State and Persistence Behavior

Allocator state lives in node and free lists plus the heap node count and block size. Allocation nodes persist until explicitly freed and may represent chained non-contiguous ranges.

## Dependencies and Integration Points

It underpins RAM heaps, channel notifier suballocations, compression tag heaps, GPU object child heaps, and legacy ABI16 notifier allocation.

## Risks

Callers that assume contiguity can program invalid hardware addresses for chained nodes. Alignment and min/max size mistakes fragment scarce GPU heaps. Leaked nodes keep resources unavailable until device teardown.

## Test Signals

Allocation/free stress, head/tail placement, alignment corner cases, heap/type filtering, chained allocation size calculations, and fini-time leak detection are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/object.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/object.h

## Purpose

This file defines the NVKM object model contract for Nouveau/NVKM. It covers base object lifetime, init/fini/method/notify/map/bind hooks, object insertion/removal, and client handle lookup.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_event`, `nvkm_gpuobj`, `nvkm_uevent`, `nvkm_object`, `nvkm_object_func`, `nvkm_client`, `nvkm_engine`, `list_head`, `rb_node`, `nvkm_object_map`, `nvkm_suspend_state`, `nvkm_oclass`, `nvkm_object_ctor`, `nvkm_object_new_`. Important callable entry points include `nvkm_object_ctor`, `nvkm_object_new_`, `nvkm_object_new`, `nvkm_object_del`, `nvkm_object_init`, `nvkm_object_fini`, `nvkm_object_mthd`, `nvkm_object_ntfy`, `nvkm_object_map`, `nvkm_object_unmap`. The visible chip-family constructors are `nvkm_object_new_, nvkm_object_new`; they bind the generic NVKM object model role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/object.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/oclass.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/oclass.h

## Purpose

This file defines the object class metadata contract for Nouveau/NVKM. It covers supported class descriptors, constructor pointers, base class ranges, engine identifiers, and client-visible object classes.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_oclass`, `nvkm_object`, `nvkm_sclass`, `nvkm_object_func`, `nvkm_client`, `nvkm_engine`. Important callable entry points include constructor/function declarations selected by including modules. The file exposes the object class metadata interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/oclass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/oproxy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/oproxy.h

## Purpose

This file defines the object proxy contract for Nouveau/NVKM. It covers proxy base object forwarding, class enumeration, constructor delegation, and nested object ownership.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_oproxy`, `nvkm_oproxy_func`, `nvkm_object`, `nvkm_suspend_state`, `nvkm_oclass`, `nvkm_oproxy_ctor`, `nvkm_oproxy_new_`. Important callable entry points include `nvkm_oproxy_ctor`, `nvkm_oproxy_new_`. The visible chip-family constructors are `nvkm_oproxy_new_`; they bind the generic object proxy role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/oproxy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/option.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/option.h

## Purpose

This file defines the configuration options contract for Nouveau/NVKM. It covers boolean, debug, and long option parsing helpers used by NVKM module-option strings.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_boolopt`, `nvkm_dbgopt`. Important callable entry points include `nvkm_boolopt`, `nvkm_dbgopt`, `strncasecmpz`. The file exposes the configuration options interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/option.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/os.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/os.h

## Purpose

This file defines the OS glue contract for Nouveau/NVKM. It covers small kernel abstraction helpers including `nvkm_blob`, list find/foreach macros, and blob cleanup.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_blob`, `nvkm_list_find_next`, `nvkm_list_find`, `nvkm_list_foreach`. Important callable entry points include `nvkm_blob_dtor`. The file exposes the OS glue interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/os.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/pci.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/pci.h

## Purpose

This file defines the PCI device construction contract for Nouveau/NVKM. It covers PCI-backed NVKM device wrapper creation with config/debug/name/detect/mmio/subdev-mask arguments.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device_pci`, `nvkm_device`, `pci_dev`, `nvkm_device_pci_new`. Important callable entry points include `nvkm_device_pci_new`. The visible chip-family constructors are `nvkm_device_pci_new`; they bind the generic PCI device construction role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/ramht.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/ramht.h

## Purpose

This file defines the RAM hash table contract for Nouveau/NVKM. It covers legacy GPU object handle table allocation, insertion, removal, lookup, and GPU object backing.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_object`, `nvkm_ramht_data`, `nvkm_gpuobj`, `nvkm_ramht`, `nvkm_device`, `nvkm_ramht_new`, `nvkm_ramht_del`, `nvkm_ramht_insert`, `nvkm_ramht_remove`, `nvkm_ramht_search`. Important callable entry points include `nvkm_ramht_new`, `nvkm_ramht_del`, `nvkm_ramht_insert`, `nvkm_ramht_remove`, `nvkm_ramht_search`. The visible chip-family constructors are `nvkm_ramht_new`; they bind the generic RAM hash table role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/ramht.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/subdev.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/subdev.h

## Purpose

This file defines the subdevice base class contract for Nouveau/NVKM. It covers subdevice type layout, lifecycle hooks, disable/refcount/preinit/oneinit/init/fini/info/intr functions, and logging macros.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_subdev_type`, `nvkm_subdev`, `nvkm_subdev_func`, `nvkm_device`, `mutex`, `nvkm_inth`, `list_head`, `nvkm_suspend_state`, `nvkm_subdev_new_`, `nvkm_subdev_disable`, `nvkm_subdev_del`, `nvkm_subdev_ref`, `nvkm_subdev_unref`, `nvkm_subdev_preinit`. Important callable entry points include `nvkm_subdev_new_`, `__nvkm_subdev_ctor`, `nvkm_subdev_ctor`, `nvkm_subdev_disable`, `nvkm_subdev_del`, `nvkm_subdev_ref`, `nvkm_subdev_unref`, `nvkm_subdev_preinit`, `nvkm_subdev_oneinit`, `nvkm_subdev_init`. The visible chip-family constructors are `nvkm_subdev_new_`; they bind the generic subdevice base class role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/subdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/suspend_state.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/suspend_state.h

## Purpose

This file defines the suspend state enum contract for Nouveau/NVKM. It covers NVKM suspend/fini state values distinguishing normal runtime teardown from suspend paths.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_suspend_state`. Important callable entry points include constructor/function declarations selected by including modules. The file exposes the suspend state enum interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/suspend_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/tegra.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/tegra.h

## Purpose

This file defines the Tegra platform device support contract for Nouveau/NVKM. It covers SoC device wrapper, platform resource fields, IOMMU/MMIO/IRQ state, and platform constructor hooks.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device_tegra`, `nvkm_device_tegra_func`, `nvkm_device`, `platform_device`, `reset_control`, `clk`, `regulator`, `mutex`, `nvkm_mm`, `iommu_domain`, `nvkm_device_tegra_new`. Important callable entry points include `nvkm_device_tegra_new`. The visible chip-family constructors are `nvkm_device_tegra_new`; they bind the generic Tegra platform device support role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/tegra.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/bsp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/bsp.h

## Purpose

This file defines the BSP video bitstream processor contract for Nouveau/NVKM. It covers legacy video decode engine constructor declarations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_subdev_type`, `nvkm_engine`, `g84_bsp_new`. Important callable entry points include `g84_bsp_new`. The visible chip-family constructors are `g84_bsp_new`; they bind the generic BSP video bitstream processor role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/bsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/ce.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/ce.h

## Purpose

This file defines the copy engine contract for Nouveau/NVKM. It covers copy-engine constructor declarations for multiple GPU generations and engine instances.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_subdev_type`, `nvkm_engine`, `gt215_ce_new`, `gf100_ce_new`, `gk104_ce_new`, `gm107_ce_new`, `gm200_ce_new`, `gp100_ce_new`, `gp102_ce_new`, `gv100_ce_new`, `tu102_ce_new`, `ga100_ce_new`, `ga102_ce_new`. Important callable entry points include `gt215_ce_new`, `gf100_ce_new`, `gk104_ce_new`, `gm107_ce_new`, `gm200_ce_new`, `gp100_ce_new`, `gp102_ce_new`, `gv100_ce_new`, `tu102_ce_new`, `ga100_ce_new`. The visible chip-family constructors are `gt215_ce_new, gf100_ce_new, gk104_ce_new, gm107_ce_new, gm200_ce_new, gp100_ce_new, gp102_ce_new, gv100_ce_new, tu102_ce_new, ga100_ce_new, ga102_ce_new`; they bind the generic copy engine role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/ce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/cipher.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/cipher.h

## Purpose

This file defines the cipher engine contract for Nouveau/NVKM. It covers legacy cipher engine constructor declarations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_subdev_type`, `nvkm_engine`, `g84_cipher_new`. Important callable entry points include `g84_cipher_new`. The visible chip-family constructors are `g84_cipher_new`; they bind the generic cipher engine role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/cipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/disp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/disp.h

## Purpose

This header defines the display engine container, including head/IOR/output/connector lists, hotplug/vblank/user events, supervisor work, display channel objects, RAMHT/instance storage, and GSP-RM display integration.

## Important APIs, Types, and Functions

Important state is in `struct nvkm_disp`; event flags include `NVKM_DPYID_PLUG`, `NVKM_DPYID_UNPLUG`, `NVKM_DPYID_IRQ`, `NVKM_DISP_HEAD_EVENT_VBLANK`, and `NVKM_DISP_EVENT_CHAN_AWAKEN`. Constructors range from `nv04_disp_new` to `ga102_disp_new`.

## Control Flow

Generation-specific constructors populate the display engine, enumerate heads/outputs/connectors, create display channels, and wire hotplug/vblank events. GSP-capable paths use RM client/device/object handles and GSP events for HPD/IRQ delivery. Supervisor work coalesces pending display updates under its mutex.

## State and Persistence Behavior

The display object owns connector/output/head lists, event objects, assigned SOR masks, display instance/RAMHT objects, channel slots, masks/counts for display hardware blocks, and a client object protected by a spinlock. Hardware state persists in display channels and RM objects until engine fini.

## Dependencies and Integration Points

It connects NVKM display internals to DRM/KMS through higher Nouveau layers, GSP event handling, RAMHT legacy display objects, and per-generation display engine code.

## Risks

Incorrect masks or channel slot indexing can expose nonexistent hardware. Event loss affects hotplug/vblank correctness. GSP and non-GSP paths must keep object lifetime and assigned SOR accounting consistent.

## Test Signals

Validate connector enumeration, hotplug and unplug events, vblank delivery, supervisor work processing, display channel creation/destruction, GSP HPD/IRQ routing, and suspend/resume display reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/disp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/dma.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/dma.h

## Purpose

This file defines the DMA object engine contract for Nouveau/NVKM. It covers DMA object lookup and DMA engine constructors, plus the DMA object base type and target/access fields.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_client`, `nvkm_dmaobj`, `nvkm_dmaobj_func`, `nvkm_dma`, `nvkm_object`, `nvkm_dma_func`, `nvkm_engine`, `nvkm_device`, `nvkm_subdev_type`, `nv04_dma_new`, `nv50_dma_new`, `gf100_dma_new`, `gf119_dma_new`, `gv100_dma_new`. Important callable entry points include `nv04_dma_new`, `nv50_dma_new`, `gf100_dma_new`, `gf119_dma_new`, `gv100_dma_new`. The visible chip-family constructors are `nv04_dma_new, nv50_dma_new, gf100_dma_new, gf119_dma_new, gv100_dma_new`; they bind the generic DMA object engine role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/falcon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/falcon.h

## Purpose

This header defines `struct nvkm_falcon`, the engine-facing representation of Falcon microcontrollers. It captures register bases, firmware code/data windows, ownership locking, DMA index constants, and chip-specific function tables.

## Important APIs, Types, and Functions

Important elements are `enum nvkm_falcon_dmaidx`, `struct nvkm_falcon`, `struct nvkm_falcon_func`, `nvkm_falcon_get`, `nvkm_falcon_put`, `nvkm_falcon_new_`, `nvkm_falcon_rd32`, `nvkm_falcon_wr32`, `nvkm_falcon_mask`, `nvkm_falcon_load_imem`, `nvkm_falcon_load_dmem`, and `nvkm_falcon_start`.

## Control Flow

An engine constructor embeds a Falcon, fills generation-specific function pointers, then users acquire it through `nvkm_falcon_get` before reset, load, start, or queue operations. Register helpers offset all accesses by the Falcon base address. Optional function pointers select/reset RISC-V variants, bind instance memory, configure PIO/DMA loaders, dispatch interrupts, and publish user object classes.

## State and Persistence Behavior

State includes owner/user subdevices, mutexes, one-time init flag, version/security/debug bits, optional core memory, code/data blob metadata, external ownership, and the embedded `nvkm_engine`. Hardware state persists in Falcon registers and loaded microcode until reset.

## Dependencies and Integration Points

It is included by the core Falcon loader, PMU/SEC2/GSP/video engines, and chip-specific Falcon implementations. It depends on `core/engine.h`, NVKM device MMIO helpers, and channel-aware interrupt callbacks.

## Risks

Ownership errors can allow concurrent firmware access. Wrong DMA index or register base corrupts unrelated engine state. RISC-V Falcon reset/interrupt paths must not be treated as classic Falcon behavior.

## Test Signals

Test Falcon acquire/release locking, IMEM/DMEM load on engines using static blobs and runtime firmware, start/reset sequencing, interrupt dispatch, and suspend/resume reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/falcon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/fifo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/fifo.h

## Purpose

This header defines FIFO/channel scheduling state for Nouveau: channel objects, run queues/lists, USERD memory, RAMFC/cache/engine contexts, non-stall events, fault handling, and per-generation FIFO constructors.

## Important APIs, Types, and Functions

Key contracts are `struct nvkm_chan`, `struct nvkm_fifo`, `nvkm_chan_get_chid`, `nvkm_chan_get_inst`, `nvkm_chan_put`, `nvkm_uchan_chan`, `nvkm_fifo_fault`, `nvkm_fifo_pause`, `nvkm_fifo_start`, and `nvkm_fifo_ctxsw_in_progress`, plus constructors from `nv04_fifo_new` through `ga102_fifo_new`.

## Control Flow

Channel lookup pins a channel under FIFO locking by CHID or instance address. FIFO pause/start bracket fault recovery, runlist manipulation, or context-switch sensitive operations. Fault paths receive `nvkm_fault_data`, identify the channel/engine, and coordinate with non-stall event delivery and channel error/block state.

## State and Persistence Behavior

Channels persist GPU object references for instance memory, push buffer, RAMFC, RAMHT, cache and engine contexts, VMM, USERD memory/base, GSP RM objects, scheduler IDs, blocked/errored atomics, and context lists. FIFO state tracks CHID/CGID allocators, run queues, runlists, USERD BAR1 mapping, RM method buffer size, and locks.

## Dependencies and Integration Points

It integrates NVKM engine/object/event infrastructure, GSP RM channel objects, fault subdevices, graphics/video/copy engines, and DRM channel allocation through NVIF.

## Risks

Stale channel references during interrupts or fault handling can use freed context memory. Pause/start imbalance can deadlock scheduling. USERD or RAMFC programming mistakes break pushbuffer submission and recovery.

## Test Signals

Exercise channel allocation/free, runlist scheduling, GPU fault injection, non-stall event delivery, context-switch pause/resume, GSP-backed channels, and concurrent channel lookup during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/fifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/gr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/gr.h

## Purpose

This header defines the graphics engine wrapper, Z-cull information exposed to legacy userspace, context-switch controls, TLB flush support, and per-generation graphics constructors.

## Important APIs, Types, and Functions

Core items are `struct nvkm_gr_zcull_info`, `struct nvkm_gr`, `nvkm_gr_units`, `nvkm_gr_tlb_flush`, `nvkm_gr_ctxsw_pause`, `nvkm_gr_ctxsw_resume`, `nvkm_gr_ctxsw_inst`, and generation constructors from NV04 through GA102.

## Control Flow

Graphics constructors build a generation-specific engine and optionally populate Z-cull geometry/context-switch metadata. Runtime helpers report active units, flush graphics TLBs after VMM changes, and pause/resume context switching around sensitive register or memory operations.

## State and Persistence Behavior

Persistent driver state is the engine object plus cached Z-cull fields and `has_zcull_info`. Hardware context-switch state changes when pause/resume helpers execute and must be restored after protected operations.

## Dependencies and Integration Points

It is used by ABI16 getparam/Z-cull ioctls, MMU invalidation paths, channel context management, and all chip-specific GR implementations.

## Risks

Wrong Z-cull metadata breaks userspace tiling assumptions. Missing TLB flushes can cause GPU faults after remapping. Context-switch pause imbalance can hang graphics channels.

## Test Signals

Run graphics channel creation, Z-cull info ioctls, TLB flush after buffer remap, context-switch pause/resume fault injection, and generation selection build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/gr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/mpeg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/mpeg.h

## Purpose

This file defines the MPEG video engine contract for Nouveau/NVKM. It covers legacy MPEG video engine constructors and engine wrapper declarations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_subdev_type`, `nvkm_engine`, `nv31_mpeg_new`, `nv40_mpeg_new`, `nv44_mpeg_new`, `nv50_mpeg_new`, `g84_mpeg_new`. Important callable entry points include `nv31_mpeg_new`, `nv40_mpeg_new`, `nv44_mpeg_new`, `nv50_mpeg_new`, `g84_mpeg_new`. The visible chip-family constructors are `nv31_mpeg_new, nv40_mpeg_new, nv44_mpeg_new, nv50_mpeg_new, g84_mpeg_new`; they bind the generic MPEG video engine role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/mpeg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/msenc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/msenc.h

## Purpose

This file defines the MSENC engine contract for Nouveau/NVKM. It covers legacy media encoder engine constructor declarations.

## Important APIs, Types, and Functions

Visible declarations include The file is intentionally narrow and exports only the declarations visible to its consumers.. Important callable entry points include constructor/function declarations selected by including modules. The file exposes the MSENC engine interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/msenc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/mspdec.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/mspdec.h

## Purpose

This file defines the MSPDEC engine contract for Nouveau/NVKM. It covers VP2-era media parser/decoder constructor declarations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_subdev_type`, `nvkm_engine`, `g98_mspdec_new`, `gt215_mspdec_new`, `gf100_mspdec_new`, `gk104_mspdec_new`. Important callable entry points include `g98_mspdec_new`, `gt215_mspdec_new`, `gf100_mspdec_new`, `gk104_mspdec_new`. The visible chip-family constructors are `g98_mspdec_new, gt215_mspdec_new, gf100_mspdec_new, gk104_mspdec_new`; they bind the generic MSPDEC engine role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/mspdec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/msppp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/msppp.h

## Purpose

This file defines the MSPPP engine contract for Nouveau/NVKM. It covers VP2-era post-processing engine constructor declarations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_subdev_type`, `nvkm_engine`, `g98_msppp_new`, `gt215_msppp_new`, `gf100_msppp_new`. Important callable entry points include `g98_msppp_new`, `gt215_msppp_new`, `gf100_msppp_new`. The visible chip-family constructors are `g98_msppp_new, gt215_msppp_new, gf100_msppp_new`; they bind the generic MSPPP engine role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/msppp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/msvld.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/msvld.h

## Purpose

This file defines the MSVLD engine contract for Nouveau/NVKM. It covers VP2-era variable-length decode engine constructor declarations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_subdev_type`, `nvkm_engine`, `g98_msvld_new`, `gt215_msvld_new`, `mcp89_msvld_new`, `gf100_msvld_new`, `gk104_msvld_new`. Important callable entry points include `g98_msvld_new`, `gt215_msvld_new`, `mcp89_msvld_new`, `gf100_msvld_new`, `gk104_msvld_new`. The visible chip-family constructors are `g98_msvld_new, gt215_msvld_new, mcp89_msvld_new, gf100_msvld_new, gk104_msvld_new`; they bind the generic MSVLD engine role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/msvld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/nvdec.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/nvdec.h

## Purpose

This file defines the NVDEC video decoder contract for Nouveau/NVKM. It covers NVDEC video decoder engine declarations with per-instance engine objects, optional Falcon-backed firmware state, and constructors for supported GPU generations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_nvdec`, `nvkm_nvdec_func`, `nvkm_engine`, `nvkm_falcon`, `nvkm_device`, `nvkm_subdev_type`, `gm107_nvdec_new`, `tu102_nvdec_new`, `ga102_nvdec_new`. Important callable entry points include `gm107_nvdec_new`, `tu102_nvdec_new`, `ga102_nvdec_new`. The visible chip-family constructors are `gm107_nvdec_new, tu102_nvdec_new, ga102_nvdec_new`; they bind the generic NVDEC video decoder role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/nvdec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/nvenc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/nvenc.h

## Purpose

This file defines the NVENC video encoder contract for Nouveau/NVKM. It covers NVENC video encoder engine declarations with per-instance engine objects, optional Falcon-backed firmware state, and constructors for supported GPU generations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_nvenc`, `nvkm_nvenc_func`, `nvkm_engine`, `nvkm_falcon`, `nvkm_device`, `nvkm_subdev_type`, `gm107_nvenc_new`, `tu102_nvenc_new`. Important callable entry points include `gm107_nvenc_new`, `tu102_nvenc_new`. The visible chip-family constructors are `gm107_nvenc_new, tu102_nvenc_new`; they bind the generic NVENC video encoder role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/nvenc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/sec.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/sec.h

## Purpose

This file defines the SEC security engine contract for Nouveau/NVKM. It covers legacy security engine constructor declarations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_subdev_type`, `nvkm_engine`, `g98_sec_new`. Important callable entry points include `g98_sec_new`. The visible chip-family constructors are `g98_sec_new`; they bind the generic SEC security engine role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/sec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/sec2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/sec2.h

## Purpose

This file defines the SEC2 security Falcon engine contract for Nouveau/NVKM. It covers the SEC2 engine wrapper around a Falcon microcontroller, including queue manager state, command/message queues, init-message storage, and generation constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_sec2`, `nvkm_sec2_func`, `nvkm_engine`, `nvkm_falcon`, `nvkm_falcon_qmgr`, `nvkm_falcon_cmdq`, `nvkm_falcon_msgq`, `work_struct`, `nvkm_device`, `nvkm_subdev_type`, `gp102_sec2_new`, `gp108_sec2_new`, `tu102_sec2_new`, `ga102_sec2_new`. Important callable entry points include `gp102_sec2_new`, `gp108_sec2_new`, `tu102_sec2_new`, `ga102_sec2_new`. The visible chip-family constructors are `gp102_sec2_new, gp108_sec2_new, tu102_sec2_new, ga102_sec2_new`; they bind the generic SEC2 security Falcon engine role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/sec2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/sw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/sw.h

## Purpose

This file defines the software engine contract for Nouveau/NVKM. It covers software class engine state, event hooks, and constructors for software object classes.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_sw`, `nvkm_sw_func`, `nvkm_engine`, `list_head`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_sw_mthd`, `nv04_sw_new`, `nv10_sw_new`, `nv50_sw_new`, `gf100_sw_new`. Important callable entry points include `nvkm_sw_mthd`, `nv04_sw_new`, `nv10_sw_new`, `nv50_sw_new`, `gf100_sw_new`. The visible chip-family constructors are `nv04_sw_new, nv10_sw_new, nv50_sw_new, gf100_sw_new`; they bind the generic software engine role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/sw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/vic.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/vic.h

## Purpose

This file defines the VIC engine contract for Nouveau/NVKM. It covers Tegra video image compositor engine constructor declarations.

## Important APIs, Types, and Functions

Visible declarations include The file is intentionally narrow and exports only the declarations visible to its consumers.. Important callable entry points include constructor/function declarations selected by including modules. The file exposes the VIC engine interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/vic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/vp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/vp.h

## Purpose

This file defines the VP video processor contract for Nouveau/NVKM. It covers legacy video processor engine constructor declarations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_subdev_type`, `nvkm_engine`, `g84_vp_new`. Important callable entry points include `g84_vp_new`. The visible chip-family constructors are `g84_vp_new`; they bind the generic VP video processor role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/vp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/xtensa.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/xtensa.h

## Purpose

This file defines the Xtensa firmware engine contract for Nouveau/NVKM. It covers Xtensa engine wrapper with firmware name, address, size, boot vector, and constructors for Xtensa-backed engines.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_xtensa`, `nvkm_xtensa_func`, `nvkm_engine`, `nvkm_memory`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_sclass`, `nvkm_xtensa_new_`. Important callable entry points include `nvkm_xtensa_new_`. The visible chip-family constructors are `nvkm_xtensa_new_`; they bind the generic Xtensa firmware engine role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/xtensa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/acr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/acr.h

## Purpose

This file defines the ACR secure boot subdevice contract for Nouveau/NVKM. It covers Authenticated Code Region firmware loading and high-secure Falcon bootstrap state, including LSF metadata, WPR layout, unload blobs, and HS firmware constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_acr`, `nvkm_acr_lsf_id`, `nvkm_acr_func`, `nvkm_subdev`, `list_head`, `nvkm_memory`, `nvkm_vmm`, `nvkm_acr_lsf`, `firmware`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_acr_lsfw`, `nvkm_acr_lsf_func`, `nvkm_falcon`. Important callable entry points include `nvkm_acr_lsf_id`, `nvkm_acr_managed_falcon`, `nvkm_acr_bootstrap_falcons`, `gm200_acr_new`, `gm20b_acr_new`, `gp102_acr_new`, `gp108_acr_new`, `gp10b_acr_new`, `gv100_acr_new`, `tu102_acr_new`. The visible chip-family constructors are `gm200_acr_new`; they bind the generic ACR secure boot subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/acr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bar.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bar.h

## Purpose

This file defines the BAR subdevice contract for Nouveau/NVKM. It covers BAR1/BAR2 VMM/memory mappings, flush helpers, BAR object refs, and per-generation BAR constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_vma`, `nvkm_bar`, `nvkm_bar_func`, `nvkm_subdev`, `nvkm_memory`, `nvkm_vmm`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_bar_bar1_reset`, `nvkm_bar_bar2_init`, `nvkm_bar_bar2_fini`, `nvkm_bar_bar2_reset`, `nvkm_bar_flush`, `nv50_bar_new`. Important callable entry points include `nvkm_bar_bar1_reset`, `nvkm_bar_bar2_init`, `nvkm_bar_bar2_fini`, `nvkm_bar_bar2_reset`, `nvkm_bar_flush`, `nv50_bar_new`, `g84_bar_new`, `gf100_bar_new`, `gk20a_bar_new`, `gm107_bar_new`. The visible chip-family constructors are `nv50_bar_new, g84_bar_new, gf100_bar_new, gk20a_bar_new, gm107_bar_new`; they bind the generic BAR subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios.h

## Purpose

This file defines the subdevice interface contract for Nouveau/NVKM. It covers NVKM subdevice declarations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`, `nvkm_subdev`, `nvkm_device`, `nvkm_subdev_type`, `nvbios_checksum`, `nvbios_findstr`, `nvbios_memcmp`, `nvbios_rd08`, `nvbios_rd16`, `nvbios_rd32`, `nvkm_bios_new`. Important callable entry points include `nvbios_checksum`, `nvbios_findstr`, `nvbios_memcmp`, `nvbios_rd08`, `nvbios_rd16`, `nvbios_rd32`, `nvkm_bios_new`. The visible chip-family constructors are `nvkm_bios_new`; they bind the generic subdevice interface role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/M0203.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/M0203.h

## Purpose

This file defines the VBIOS M0203 table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `M0203` table family. It exports parser helpers such as `nvbios_M0203Te, nvbios_M0203Tp, nvbios_M0203Ee, nvbios_M0203Ep, nvbios_M0203Em`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_M0203T`, `nvkm_bios`, `nvbios_M0203E`, `nvbios_M0203Te`, `nvbios_M0203Tp`, `nvbios_M0203Ee`, `nvbios_M0203Ep`, `nvbios_M0203Em`, `M0203T_TYPE_RAMCFG`, `M0203E_TYPE_DDR2`, `M0203E_TYPE_DDR3`, `M0203E_TYPE_GDDR3`, `M0203E_TYPE_GDDR5`, `M0203E_TYPE_HBM2`. Important callable entry points include `nvbios_M0203Te`, `nvbios_M0203Tp`, `nvbios_M0203Ee`, `nvbios_M0203Ep`, `nvbios_M0203Em`. The file exposes the VBIOS M0203 table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/M0203.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/M0205.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/M0205.h

## Purpose

This file defines the VBIOS M0205 table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `M0205` table family. It exports parser helpers such as `nvbios_M0205Te, nvbios_M0205Tp, nvbios_M0205Ee, nvbios_M0205Ep, nvbios_M0205Se, nvbios_M0205Sp`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_M0205T`, `nvkm_bios`, `nvbios_M0205E`, `nvbios_M0205S`, `nvbios_M0205Te`, `nvbios_M0205Tp`, `nvbios_M0205Ee`, `nvbios_M0205Ep`, `nvbios_M0205Se`, `nvbios_M0205Sp`. Important callable entry points include `nvbios_M0205Te`, `nvbios_M0205Tp`, `nvbios_M0205Ee`, `nvbios_M0205Ep`, `nvbios_M0205Se`, `nvbios_M0205Sp`. The file exposes the VBIOS M0205 table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/M0205.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/M0209.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/M0209.h

## Purpose

This file defines the VBIOS M0209 table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `M0209` table family. It exports parser helpers such as `nvbios_M0209Te, nvbios_M0209Ee, nvbios_M0209Ep, nvbios_M0209Se, nvbios_M0209Sp`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`, `nvbios_M0209E`, `nvbios_M0209S`, `nvbios_M0209Te`, `nvbios_M0209Ee`, `nvbios_M0209Ep`, `nvbios_M0209Se`, `nvbios_M0209Sp`. Important callable entry points include `nvbios_M0209Te`, `nvbios_M0209Ee`, `nvbios_M0209Ep`, `nvbios_M0209Se`, `nvbios_M0209Sp`. The file exposes the VBIOS M0209 table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/M0209.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/P0260.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/P0260.h

## Purpose

This file defines the VBIOS P0260 table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `P0260` table family. It exports parser helpers such as `nvbios_P0260Te, nvbios_P0260Ee, nvbios_P0260Ep, nvbios_P0260Xe, nvbios_P0260Xp`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`, `nvbios_P0260E`, `nvbios_P0260X`, `nvbios_P0260Te`, `nvbios_P0260Ee`, `nvbios_P0260Ep`, `nvbios_P0260Xe`, `nvbios_P0260Xp`. Important callable entry points include `nvbios_P0260Te`, `nvbios_P0260Ee`, `nvbios_P0260Ep`, `nvbios_P0260Xe`, `nvbios_P0260Xp`. The file exposes the VBIOS P0260 table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/P0260.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/bit.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/bit.h

## Purpose

This file defines the VBIOS bit table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `bit` table family. It exports parser helpers such as `bit_entry`.

## Important APIs, Types, and Functions

Visible declarations include `bit_entry`, `nvkm_bios`. Important callable entry points include `bit_entry`. The file exposes the VBIOS bit table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/bit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/bmp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/bmp.h

## Purpose

This file defines the VBIOS bmp table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `bmp` table family. It exports parser helpers such as `bmp_version, bmp_mem_init_table, bmp_sdr_seq_table, bmp_ddr_seq_table`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`. Important callable entry points include `bmp_version`, `bmp_mem_init_table`, `bmp_sdr_seq_table`, `bmp_ddr_seq_table`. The file exposes the VBIOS bmp table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/bmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/boost.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/boost.h

## Purpose

This file defines the VBIOS boost table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `boost` table family. It exports parser helpers such as `nvbios_boostTe, nvbios_boostEe, nvbios_boostEp, nvbios_boostEm, nvbios_boostSe, nvbios_boostSp`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`, `nvbios_boostE`, `nvbios_boostS`, `nvbios_boostTe`, `nvbios_boostEe`, `nvbios_boostEp`, `nvbios_boostEm`, `nvbios_boostSe`, `nvbios_boostSp`. Important callable entry points include `nvbios_boostTe`, `nvbios_boostEe`, `nvbios_boostEp`, `nvbios_boostEm`, `nvbios_boostSe`, `nvbios_boostSp`. The file exposes the VBIOS boost table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/boost.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/conn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/conn.h

## Purpose

This file defines the VBIOS conn table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `conn` table family. It exports parser helpers such as `nvbios_connTe, nvbios_connTp, nvbios_connEe, nvbios_connEp`.

## Important APIs, Types, and Functions

Visible declarations include `dcb_connector_type`, `comment`, `nvbios_connT`, `nvkm_bios`, `nvbios_connE`, `nvbios_connTe`, `nvbios_connTp`, `nvbios_connEe`, `nvbios_connEp`. Important callable entry points include `nvbios_connTe`, `nvbios_connTp`, `nvbios_connEe`, `nvbios_connEp`. The file exposes the VBIOS conn table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/conn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/cstep.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/cstep.h

## Purpose

This file defines the VBIOS cstep table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `cstep` table family. It exports parser helpers such as `nvbios_cstepTe, nvbios_cstepEe, nvbios_cstepEp, nvbios_cstepEm, nvbios_cstepXe, nvbios_cstepXp`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`, `nvbios_cstepE`, `nvbios_cstepX`, `nvbios_cstepTe`, `nvbios_cstepEe`, `nvbios_cstepEp`, `nvbios_cstepEm`, `nvbios_cstepXe`, `nvbios_cstepXp`. Important callable entry points include `nvbios_cstepTe`, `nvbios_cstepEe`, `nvbios_cstepEp`, `nvbios_cstepEm`, `nvbios_cstepXe`, `nvbios_cstepXp`. The file exposes the VBIOS cstep table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/cstep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/dcb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/dcb.h

## Purpose

This file defines the VBIOS dcb table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `dcb` table family. It exports parser helpers such as `dcb_table, dcb_outp, dcb_outp_parse, dcb_outp_match, dcb_outp_foreach`.

## Important APIs, Types, and Functions

Visible declarations include `dcb_output_type`, `dcb_output`, `sor_conf`, `nvkm_bios`, `dcb_table`, `dcb_outp`, `dcb_outp_parse`, `dcb_outp_match`, `dcb_outp_foreach`. Important callable entry points include `dcb_table`, `dcb_outp`, `dcb_outp_parse`, `dcb_outp_match`, `dcb_outp_foreach`. The file exposes the VBIOS dcb table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/dcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/disp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/disp.h

## Purpose

This file defines the VBIOS disp table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `disp` table family. It exports parser helpers such as `nvbios_disp_table, nvbios_disp_entry, nvbios_disp_parse, nvbios_outp_entry, nvbios_outp_parse, nvbios_outp_match, nvbios_ocfg_entry, nvbios_ocfg_parse`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`, `nvbios_disp`, `nvbios_outp`, `nvbios_ocfg`, `nvbios_disp_table`, `nvbios_disp_entry`, `nvbios_disp_parse`, `nvbios_outp_entry`, `nvbios_outp_parse`, `nvbios_outp_match`, `nvbios_ocfg_entry`, `nvbios_ocfg_parse`, `nvbios_ocfg_match`, `nvbios_oclk_match`. Important callable entry points include `nvbios_disp_table`, `nvbios_disp_entry`, `nvbios_disp_parse`, `nvbios_outp_entry`, `nvbios_outp_parse`, `nvbios_outp_match`, `nvbios_ocfg_entry`, `nvbios_ocfg_parse`, `nvbios_ocfg_match`, `nvbios_oclk_match`. The file exposes the VBIOS disp table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/disp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/dp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/dp.h

## Purpose

This file defines the VBIOS dp table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `dp` table family. It exports parser helpers such as `nvbios_dp_table, nvbios_dpout_parse, nvbios_dpout_match, nvbios_dpcfg_parse, nvbios_dpcfg_match`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`, `nvbios_dpout`, `nvbios_dpcfg`, `nvbios_dp_table`, `nvbios_dpout_parse`, `nvbios_dpout_match`, `nvbios_dpcfg_parse`, `nvbios_dpcfg_match`. Important callable entry points include `nvbios_dp_table`, `nvbios_dpout_parse`, `nvbios_dpout_match`, `nvbios_dpcfg_parse`, `nvbios_dpcfg_match`. The file exposes the VBIOS dp table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/extdev.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/extdev.h

## Purpose

This file defines the VBIOS extdev table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `extdev` table family. It exports parser helpers such as `nvbios_extdev_parse, nvbios_extdev_find, nvbios_extdev_skip_probe`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_extdev_type`, `nvbios_extdev_func`, `nvkm_bios`, `nvbios_extdev_parse`, `nvbios_extdev_find`, `nvbios_extdev_skip_probe`. Important callable entry points include `nvbios_extdev_parse`, `nvbios_extdev_find`, `nvbios_extdev_skip_probe`. The file exposes the VBIOS extdev table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/extdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/fan.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/fan.h

## Purpose

This file defines the VBIOS fan table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `fan` table family. It exports parser helpers such as `nvbios_fan_parse`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`, `nvbios_therm_fan`, `nvbios_fan_parse`. Important callable entry points include `nvbios_fan_parse`. The file exposes the VBIOS fan table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/fan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/gpio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/gpio.h

## Purpose

This file defines the VBIOS gpio table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `gpio` table family. It exports parser helpers such as `dcb_gpio_table, dcb_gpio_entry, dcb_gpio_parse, dcb_gpio_match`.

## Important APIs, Types, and Functions

Visible declarations include `dcb_gpio_func_name`, `dcb_gpio_func`, `nvkm_bios`, `dcb_gpio_table`, `dcb_gpio_entry`, `dcb_gpio_parse`, `dcb_gpio_match`, `DCB_GPIO_LOG_DIR`, `DCB_GPIO_LOG_DIR_OUT`, `DCB_GPIO_LOG_DIR_IN`, `DCB_GPIO_LOG_VAL`, `DCB_GPIO_LOG_VAL_LO`, `DCB_GPIO_LOG_VAL_HI`. Important callable entry points include `dcb_gpio_table`, `dcb_gpio_entry`, `dcb_gpio_parse`, `dcb_gpio_match`. The file exposes the VBIOS gpio table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/i2c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/i2c.h

## Purpose

This file defines the VBIOS i2c table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `i2c` table family. It exports parser helpers such as `dcb_i2c_table, dcb_i2c_entry, dcb_i2c_parse`.

## Important APIs, Types, and Functions

Visible declarations include `dcb_i2c_type`, `dcb_i2c_entry`, `nvkm_bios`, `dcb_i2c_table`, `dcb_i2c_parse`. Important callable entry points include `dcb_i2c_table`, `dcb_i2c_entry`, `dcb_i2c_parse`. The file exposes the VBIOS i2c table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/iccsense.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/iccsense.h

## Purpose

This file defines the VBIOS iccsense table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `iccsense` table family. It exports parser helpers such as `nvbios_iccsense_parse`.

## Important APIs, Types, and Functions

Visible declarations include `pwr_rail_resistor_t`, `pwr_rail_t`, `nvbios_iccsense`, `nvkm_bios`, `nvbios_iccsense_parse`. Important callable entry points include `nvbios_iccsense_parse`. The file exposes the VBIOS iccsense table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/iccsense.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/image.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/image.h

## Purpose

This file defines the VBIOS image table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `image` table family. It exports parser helpers such as `nvbios_image`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_image`, `nvkm_bios`. Important callable entry points include `nvbios_image`. The file exposes the VBIOS image table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/image.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/init.h

## Purpose

This file defines the VBIOS init table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `init` table family. It exports parser helpers such as `nvbios_exec, nvbios_post`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_init`, `nvkm_subdev`, `dcb_output`, `nvbios_exec`, `nvbios_post`. Important callable entry points include `nvbios_exec`, `nvbios_post`. The file exposes the VBIOS init table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/mxm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/mxm.h

## Purpose

This file defines the VBIOS mxm table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `mxm` table family. It exports parser helpers such as `mxm_table, mxm_sor_map, mxm_ddc_map`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`, `mxm_table`, `mxm_sor_map`, `mxm_ddc_map`. Important callable entry points include `mxm_table`, `mxm_sor_map`, `mxm_ddc_map`. The file exposes the VBIOS mxm table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/mxm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/npde.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/npde.h

## Purpose

This file defines the VBIOS npde table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `npde` table family. It exports parser helpers such as `nvbios_npdeTe, nvbios_npdeTp`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_npdeT`, `nvkm_bios`, `nvbios_npdeTe`, `nvbios_npdeTp`. Important callable entry points include `nvbios_npdeTe`, `nvbios_npdeTp`. The file exposes the VBIOS npde table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/npde.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/pcir.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/pcir.h

## Purpose

This file defines the VBIOS pcir table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `pcir` table family. It exports parser helpers such as `nvbios_pcirTe, nvbios_pcirTp`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_pcirT`, `nvkm_bios`, `nvbios_pcirTe`, `nvbios_pcirTp`. Important callable entry points include `nvbios_pcirTe`, `nvbios_pcirTp`. The file exposes the VBIOS pcir table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/pcir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/perf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/perf.h

## Purpose

This file defines the VBIOS perf table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `perf` table family. It exports parser helpers such as `nvbios_perf_table, nvbios_perf_entry, nvbios_perfEp, nvbios_perfSe, nvbios_perfSp, nvbios_perf_fan_parse`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`, `nvbios_perfE`, `nvbios_perfS`, `nvbios_perf_fan`, `nvbios_perf_table`, `nvbios_perf_entry`, `nvbios_perfEp`, `nvbios_perfSe`, `nvbios_perfSp`, `nvbios_perf_fan_parse`. Important callable entry points include `nvbios_perf_table`, `nvbios_perf_entry`, `nvbios_perfEp`, `nvbios_perfSe`, `nvbios_perfSp`, `nvbios_perf_fan_parse`. The file exposes the VBIOS perf table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/pll.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/pll.h

## Purpose

This file defines the VBIOS pll table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `pll` table family. It exports parser helpers such as `nvbios_pll_parse`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_pll_vals`, `nvbios_pll_type`, `nvbios_pll`, `nvkm_bios`, `nvbios_pll_parse`. Important callable entry points include `nvbios_pll_parse`. The file exposes the VBIOS pll table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/pmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/pmu.h

## Purpose

This file defines the VBIOS pmu table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `pmu` table family. It exports parser helpers such as `nvbios_pmuTe, nvbios_pmuEe, nvbios_pmuEp, nvbios_pmuRm`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_pmuT`, `nvkm_bios`, `nvbios_pmuE`, `nvbios_pmuR`, `nvbios_pmuTe`, `nvbios_pmuEe`, `nvbios_pmuEp`, `nvbios_pmuRm`. Important callable entry points include `nvbios_pmuTe`, `nvbios_pmuEe`, `nvbios_pmuEp`, `nvbios_pmuRm`. The file exposes the VBIOS pmu table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/power_budget.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/power_budget.h

## Purpose

This file defines the VBIOS power_budget table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `power_budget` table family. It exports parser helpers such as `nvbios_power_budget_header, nvbios_power_budget_entry`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_power_budget_entry`, `nvbios_power_budget`, `nvkm_bios`, `nvbios_power_budget_header`. Important callable entry points include `nvbios_power_budget_header`, `nvbios_power_budget_entry`. The file exposes the VBIOS power_budget table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/power_budget.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/ramcfg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/ramcfg.h

## Purpose

This file defines the VBIOS ramcfg table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `ramcfg` table family. It exports parser helpers such as `nvbios_ramcfg_count, nvbios_ramcfg_index`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_ramcfg`, `nvkm_bios`, `nvkm_subdev`, `nvbios_ramcfg_count`, `nvbios_ramcfg_index`. Important callable entry points include `nvbios_ramcfg_count`, `nvbios_ramcfg_index`. The file exposes the VBIOS ramcfg table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/ramcfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/rammap.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/rammap.h

## Purpose

This file defines the VBIOS rammap table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `rammap` table family. It exports parser helpers such as `nvbios_rammapTe, nvbios_rammapEe, nvbios_rammapEp_from_perf, nvbios_rammapEp, nvbios_rammapEm, nvbios_rammapSe, nvbios_rammapSp_from_perf, nvbios_rammapSp`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`, `nvbios_ramcfg`, `nvbios_rammapTe`, `nvbios_rammapEe`, `nvbios_rammapEp_from_perf`, `nvbios_rammapEp`, `nvbios_rammapEm`, `nvbios_rammapSe`, `nvbios_rammapSp_from_perf`, `nvbios_rammapSp`. Important callable entry points include `nvbios_rammapTe`, `nvbios_rammapEe`, `nvbios_rammapEp_from_perf`, `nvbios_rammapEp`, `nvbios_rammapEm`, `nvbios_rammapSe`, `nvbios_rammapSp_from_perf`, `nvbios_rammapSp`. The file exposes the VBIOS rammap table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/rammap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/therm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/therm.h

## Purpose

This file defines the VBIOS therm table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `therm` table family. It exports parser helpers such as `nvbios_therm_sensor_parse, nvbios_therm_fan_parse`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_therm_threshold`, `nvbios_therm_sensor`, `nvbios_therm_fan_type`, `nvbios_therm_trip_point`, `nvbios_therm_fan_mode`, `nvbios_therm_fan`, `nvbios_therm_domain`, `nvkm_bios`, `nvbios_therm_sensor_parse`, `nvbios_therm_fan_parse`, `NVKM_TEMP_FAN_TRIP_MAX`. Important callable entry points include `nvbios_therm_sensor_parse`, `nvbios_therm_fan_parse`. The file exposes the VBIOS therm table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/therm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/timing.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/timing.h

## Purpose

This file defines the VBIOS timing table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `timing` table family. It exports parser helpers such as `nvbios_timingTe, nvbios_timingEe, nvbios_timingEp`.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bios`, `nvbios_ramcfg`, `nvbios_timingTe`, `nvbios_timingEe`, `nvbios_timingEp`. Important callable entry points include `nvbios_timingTe`, `nvbios_timingEe`, `nvbios_timingEp`. The file exposes the VBIOS timing table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/timing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/vmap.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/vmap.h

## Purpose

This file defines the VBIOS vmap table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `vmap` table family. It exports parser helpers such as `nvbios_vmap_table, nvbios_vmap_parse, nvbios_vmap_entry, nvbios_vmap_entry_parse`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_vmap`, `nvkm_bios`, `nvbios_vmap_entry`, `nvbios_vmap_table`, `nvbios_vmap_parse`, `nvbios_vmap_entry_parse`. Important callable entry points include `nvbios_vmap_table`, `nvbios_vmap_parse`, `nvbios_vmap_entry`, `nvbios_vmap_entry_parse`. The file exposes the VBIOS vmap table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/vmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/volt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/volt.h

## Purpose

This file defines the VBIOS volt table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `volt` table family. It exports parser helpers such as `nvbios_volt_table, nvbios_volt_parse, nvbios_volt_entry, nvbios_volt_entry_parse`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_volt_type`, `nvbios_volt`, `nvkm_bios`, `nvbios_volt_entry`, `nvbios_volt_table`, `nvbios_volt_parse`, `nvbios_volt_entry_parse`. Important callable entry points include `nvbios_volt_table`, `nvbios_volt_parse`, `nvbios_volt_entry`, `nvbios_volt_entry_parse`. The file exposes the VBIOS volt table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/volt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/vpstate.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/vpstate.h

## Purpose

This file defines the VBIOS vpstate table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `vpstate` table family. It exports parser helpers such as `nvbios_vpstate_parse, nvbios_vpstate_entry`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_vpstate_header`, `nvbios_vpstate_entry`, `nvkm_bios`, `nvbios_vpstate_parse`. Important callable entry points include `nvbios_vpstate_parse`, `nvbios_vpstate_entry`. The file exposes the VBIOS vpstate table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/vpstate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/xpio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/xpio.h

## Purpose

This file defines the VBIOS xpio table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `xpio` table family. It exports parser helpers such as `dcb_xpio_table, dcb_xpio_parse`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_xpio`, `nvkm_bios`, `dcb_xpio_table`, `dcb_xpio_parse`, `NVBIOS_XPIO_FLAG_AUX`, `NVBIOS_XPIO_FLAG_AUX0`, `NVBIOS_XPIO_FLAG_AUX1`. Important callable entry points include `dcb_xpio_table`, `dcb_xpio_parse`. The file exposes the VBIOS xpio table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/xpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bus.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bus.h

## Purpose

This file defines the bus subdevice contract for Nouveau/NVKM. It covers bus-level initialization and hwsq hooks used by older chipsets and register programming sequences.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_bus`, `nvkm_bus_func`, `nvkm_subdev`, `nvkm_hwsq`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_hwsq_init`, `nvkm_hwsq_fini`, `nvkm_hwsq_wr32`, `nvkm_hwsq_setf`, `nvkm_hwsq_wait`, `nvkm_hwsq_wait_vblank`, `nvkm_hwsq_nsec`, `nv04_bus_new`. Important callable entry points include `nvkm_hwsq_init`, `nvkm_hwsq_fini`, `nvkm_hwsq_wr32`, `nvkm_hwsq_setf`, `nvkm_hwsq_wait`, `nvkm_hwsq_wait_vblank`, `nvkm_hwsq_nsec`, `nv04_bus_new`, `nv31_bus_new`, `nv50_bus_new`. The visible chip-family constructors are `nv04_bus_new, nv31_bus_new, nv50_bus_new, g94_bus_new, gf100_bus_new`; they bind the generic bus subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/clk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/clk.h

## Purpose

This file defines the clock subdevice contract for Nouveau/NVKM. It covers clock domains, p-states, c-states, voltage coupling, read/calc/prog/tidy hooks, and per-generation clock constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_pll`, `nvkm_pll_vals`, `nv_clk_src`, `nvkm_cstate`, `list_head`, `nvkm_pstate`, `nvkm_pcie_speed`, `nvkm_domain`, `nvkm_clk`, `nvkm_clk_func`, `nvkm_subdev`, `work_struct`, `nvkm_device`, `nvkm_subdev_type`. Important callable entry points include `nvkm_clk_read`, `nvkm_clk_ustate`, `nvkm_clk_astate`, `nvkm_clk_dstate`, `nvkm_clk_tstate`, `nvkm_clk_pwrsrc`, `nv04_clk_new`, `nv40_clk_new`, `nv50_clk_new`, `g84_clk_new`. The file exposes the clock subdevice interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/devinit.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/devinit.h

## Purpose

This file defines the device init subdevice contract for Nouveau/NVKM. It covers pre/post init hooks, PLL programming, memory init, display init, and BIOS-script-driven device bring-up.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_devinit`, `nvkm_devinit_func`, `nvkm_subdev`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_devinit_mmio`, `nvkm_devinit_pll_set`, `nvkm_devinit_meminit`, `nvkm_devinit_post`, `nv04_devinit_new`, `nv05_devinit_new`, `nv10_devinit_new`, `nv1a_devinit_new`, `nv20_devinit_new`. Important callable entry points include `nvkm_devinit_mmio`, `nvkm_devinit_pll_set`, `nvkm_devinit_meminit`, `nvkm_devinit_post`, `nv04_devinit_new`, `nv05_devinit_new`, `nv10_devinit_new`, `nv1a_devinit_new`, `nv20_devinit_new`, `nv50_devinit_new`. The visible chip-family constructors are `nv04_devinit_new, nv05_devinit_new, nv10_devinit_new, nv1a_devinit_new, nv20_devinit_new, nv50_devinit_new, g84_devinit_new, g98_devinit_new, gt215_devinit_new`; they bind the generic device init subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/devinit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fault.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fault.h

## Purpose

This file defines the fault subdevice contract for Nouveau/NVKM. It covers GPU fault-buffer data structures, access/client/reason/hub/gpc metadata, and fault reporting helpers.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_fault`, `nvkm_fault_func`, `nvkm_subdev`, `nvkm_inth`, `nvkm_fault_buffer`, `nvkm_event`, `nvkm_event_ntfy`, `work_struct`, `nvkm_device_oclass`, `nvkm_fault_data`, `nvkm_device`, `nvkm_subdev_type`, `gp100_fault_new`, `gp10b_fault_new`. Important callable entry points include `gp100_fault_new`, `gp10b_fault_new`, `gv100_fault_new`, `tu102_fault_new`. The visible chip-family constructors are `gp100_fault_new, gp10b_fault_new, gv100_fault_new, tu102_fault_new`; they bind the generic fault subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fault.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fb.h

## Purpose

This header defines the framebuffer/RAM subdevice, including VRAM sizing, memory unlock, tiling/compression tag state, sysmem flush resources, VPR scrubber firmware, RAM heap management, RAM type metadata, and memory clock transition state.

## Important APIs, Types, and Functions

Important contracts include `struct nvkm_fb`, `struct nvkm_fb_tile`, `struct nvkm_ram`, `struct nvkm_ram_data`, `enum nvkm_ram_type`, `struct nvkm_ram_func`, `nvkm_fb_vidmem_size`, `nvkm_fb_mem_unlock`, `nvkm_fb_tile_init`, `nvkm_fb_tile_fini`, `nvkm_fb_tile_prog`, `nvkm_ram_wrap`, and `nvkm_ram_get`, plus framebuffer constructors through GB202.

## Control Flow

Framebuffer constructors probe VRAM/RAM type, initialize heap and compression-tag allocators, set tile regions, and provide memory allocation wrappers. RAM callers allocate from heaps with page/contiguity/backing constraints; memory reclocking calculates, programs, tidies, and records transition state.

## State and Persistence Behavior

The subdevice persists RAM size/type/frequency, VRAM allocator nodes, stolen memory, rank/part masks, mode registers, compression tag heap, tile regions, sysmem flush page, and VPR scrubber firmware. Hardware tiling and RAM timing state persists until reprogrammed or reset.

## Dependencies and Integration Points

It integrates BIOS RAM config tables, PMU memory scripts, MMU memory targets, GPU memory allocation, display tiling, and secure VPR scrubbing.

## Risks

Incorrect VRAM size or heap classification can corrupt memory allocations. Compression tag leaks reduce render compression capacity. RAM transition mistakes can hang memory access. Tile programming affects scanout and render layout.

## Test Signals

Use VRAM allocation/free stress, memory clock transitions, compression-tag allocation, tile init/fini/prog, VPR scrubber boot, suspend/resume, and per-generation framebuffer probe tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fsp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fsp.h

## Purpose

This file defines the FSP subdevice contract for Nouveau/NVKM. It covers firmware security processor subdevice declarations and constructors for newer GPUs.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_fsp`, `nvkm_fsp_func`, `nvkm_subdev`, `nvkm_falcon`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_fsp_verify_gsp_fmc`, `nvkm_fsp_boot_gsp_fmc`, `gh100_fsp_new`, `gb100_fsp_new`, `gb202_fsp_new`. Important callable entry points include `nvkm_fsp_verify_gsp_fmc`, `nvkm_fsp_boot_gsp_fmc`, `gh100_fsp_new`, `gb100_fsp_new`, `gb202_fsp_new`. The visible chip-family constructors are `gh100_fsp_new, gb100_fsp_new, gb202_fsp_new`; they bind the generic FSP subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fuse.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fuse.h

## Purpose

This file defines the fuse subdevice contract for Nouveau/NVKM. It covers fuse register access and option query helpers for SKU/topology/security information.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_fuse`, `nvkm_fuse_func`, `nvkm_subdev`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_fuse_read`, `nv50_fuse_new`, `gf100_fuse_new`, `gm107_fuse_new`. Important callable entry points include `nvkm_fuse_read`, `nv50_fuse_new`, `gf100_fuse_new`, `gm107_fuse_new`. The visible chip-family constructors are `nv50_fuse_new, gf100_fuse_new, gm107_fuse_new`; they bind the generic fuse subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fuse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/gpio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/gpio.h

## Purpose

This file defines the GPIO subdevice contract for Nouveau/NVKM. It covers GPIO line descriptors, IRQ events, get/set/find operations, reset handling, and per-generation constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_gpio_ntfy_req`, `nvkm_gpio_ntfy_rep`, `nvkm_gpio`, `nvkm_gpio_func`, `nvkm_subdev`, `nvkm_event`, `dcb_gpio_func`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_gpio_reset`, `nvkm_gpio_find`, `nvkm_gpio_set`, `nvkm_gpio_get`, `nv10_gpio_new`. Important callable entry points include `nvkm_gpio_reset`, `nvkm_gpio_find`, `nvkm_gpio_set`, `nvkm_gpio_get`, `nv10_gpio_new`, `nv50_gpio_new`, `g94_gpio_new`, `gf119_gpio_new`, `gk104_gpio_new`, `ga102_gpio_new`. The visible chip-family constructors are `nv10_gpio_new, nv50_gpio_new, g94_gpio_new, gf119_gpio_new, gk104_gpio_new`; they bind the generic GPIO subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/gsp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/gsp.h

## Purpose

This header defines the GPU System Processor subdevice, including firmware packages, boot memory, WPR/FB layout, shared command/message queues, RPC reply policy, RM object wrappers, registry state, interrupt routing, suspend/resume memory, and debugfs logging buffers.

## Important APIs, Types, and Functions

Important elements include `struct nvkm_gsp`, `struct nvkm_gsp_mem`, `struct nvkm_gsp_radix3`, `enum nvkm_gsp_rpc_reply_policy`, `struct nvkm_gsp_client`, `struct nvkm_gsp_device`, `struct nvkm_gsp_object`, `struct nvkm_gsp_event`, `nvkm_gsp_mem_ctor`, `nvkm_gsp_mem_dtor`, `nvkm_gsp_sg`, and `nvkm_gsp_sg_free`.

## Control Flow

GSP initialization allocates DMA memory and scatter-gather/radix3 page tables, loads booter/FMC/boot/RM firmware, describes framebuffer/WPR regions, starts Falcon/GSP firmware, then communicates through shared command and message queues. RPC callers choose nowait, no-sequence, receive, or poll reply handling. RM object wrappers mirror GSP-owned handles for display, FIFO, VMM, and other services.

## State and Persistence Behavior

State is extensive: firmware references, DMA buffers, WPR metadata, BIOS/heap/region layout, suspend-resume buffers, shared queue pointers/counters/sequences, running flag, internal clients/devices, interrupt mappings, BAR PDB addresses, GR topology, registry RPC data, and optional debugfs dentries. Most state persists while GSP-RM is running and must be rebuilt after full firmware reset.

## Dependencies and Integration Points

It depends on Falcon firmware loading, NVKM subdev lifecycle, Linux firmware/DMA/SG/debugfs APIs, RM generated headers, display/FIFO/MMU clients, and device interrupt routing.

## Risks

DMA buffer lifetime and alignment are critical because firmware dereferences these structures. RPC sequence policy mistakes can deadlock callers or drop replies. GSP/non-GSP paths must preserve the same high-level NVKM contracts despite different ownership of hardware programming.

## Test Signals

Validate GSP boot/unload, DMA/radix3 allocation cleanup, RPC timeout/reply policies, event notification delivery, debugfs log exposure, suspend/resume memory handoff, and fallback on firmware load failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/gsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/i2c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/i2c.h

## Purpose

This file defines the I2C subdevice contract for Nouveau/NVKM. It covers I2C bus and AUX pad/port descriptors, DCB integration, transfer hooks, and per-generation constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_i2c_bus_probe`, `i2c_board_info`, `nvkm_i2c_bus`, `nvkm_i2c_bus_func`, `nvkm_i2c_pad`, `mutex`, `list_head`, `i2c_adapter`, `nvkm_i2c_aux`, `nvkm_i2c_aux_func`, `nvkm_i2c`, `nvkm_i2c_func`, `nvkm_subdev`, `nvkm_event`. Important callable entry points include `nvkm_i2c_bus_acquire`, `nvkm_i2c_bus_release`, `nvkm_i2c_bus_probe`, `nvkm_i2c_aux_monitor`, `nvkm_i2c_aux_acquire`, `nvkm_i2c_aux_release`, `nvkm_i2c_aux_xfer`, `nvkm_i2c_aux_lnk_ctl`, `nv04_i2c_new`, `nv4e_i2c_new`. The file exposes the I2C subdevice interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/iccsense.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/iccsense.h

## Purpose

This file defines the ICC sense subdevice contract for Nouveau/NVKM. It covers current-sense rail descriptors and power-sensor integration built from BIOS tables.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_iccsense`, `nvkm_subdev`, `list_head`, `nvkm_device`, `nvkm_subdev_type`, `gf100_iccsense_new`, `nvkm_iccsense_read_all`. Important callable entry points include `gf100_iccsense_new`, `nvkm_iccsense_read_all`. The visible chip-family constructors are `gf100_iccsense_new`; they bind the generic ICC sense subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/iccsense.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/instmem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/instmem.h

## Purpose

This file defines the instance memory subdevice contract for Nouveau/NVKM. It covers GPU instance-memory allocation/wrapping for channel and engine context objects.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_memory`, `nvkm_instmem`, `nvkm_instmem_func`, `nvkm_subdev`, `list_head`, `mutex`, `nvkm_ramht`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_instmem_rd32`, `nvkm_instmem_wr32`, `nvkm_instobj_new`, `nvkm_instobj_wrap`, `nv04_instmem_new`. Important callable entry points include `nvkm_instmem_rd32`, `nvkm_instmem_wr32`, `nvkm_instobj_new`, `nvkm_instobj_wrap`, `nv04_instmem_new`, `nv40_instmem_new`, `nv50_instmem_new`, `gk20a_instmem_new`, `gh100_instmem_new`. The visible chip-family constructors are `nvkm_instobj_new, nv04_instmem_new, nv40_instmem_new, nv50_instmem_new, gk20a_instmem_new, gh100_instmem_new`; they bind the generic instance memory subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/instmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/ltc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/ltc.h

## Purpose

This file defines the LTC subdevice contract for Nouveau/NVKM. It covers L2 cache/slice topology, compression tag clearing, invalidation/flush helpers, and per-generation constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_ltc`, `nvkm_ltc_func`, `nvkm_subdev`, `mutex`, `nvkm_memory`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_ltc_tags_clear`, `nvkm_ltc_zbc_color_get`, `nvkm_ltc_zbc_depth_get`, `nvkm_ltc_zbc_stencil_get`, `nvkm_ltc_invalidate`, `nvkm_ltc_flush`, `gf100_ltc_new`. Important callable entry points include `nvkm_ltc_tags_clear`, `nvkm_ltc_zbc_color_get`, `nvkm_ltc_zbc_depth_get`, `nvkm_ltc_zbc_stencil_get`, `nvkm_ltc_invalidate`, `nvkm_ltc_flush`, `gf100_ltc_new`, `gk104_ltc_new`, `gm107_ltc_new`, `gm200_ltc_new`. The visible chip-family constructors are `gf100_ltc_new, gk104_ltc_new, gm107_ltc_new, gm200_ltc_new, gp100_ltc_new`; they bind the generic LTC subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/ltc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/mc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/mc.h

## Purpose

This file defines the master control subdevice contract for Nouveau/NVKM. It covers engine enable/disable/reset/intr-mask helpers and chipset-specific master-control constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_mc`, `nvkm_mc_func`, `nvkm_subdev`, `nvkm_intr`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_mc_enable`, `nvkm_mc_disable`, `nvkm_mc_enabled`, `nvkm_mc_reset`, `nvkm_mc_intr_mask`, `nvkm_mc_unk260`, `nv04_mc_new`, `nv11_mc_new`. Important callable entry points include `nvkm_mc_enable`, `nvkm_mc_disable`, `nvkm_mc_enabled`, `nvkm_mc_reset`, `nvkm_mc_intr_mask`, `nvkm_mc_unk260`, `nv04_mc_new`, `nv11_mc_new`, `nv17_mc_new`, `nv44_mc_new`. The visible chip-family constructors are `nv04_mc_new, nv11_mc_new, nv17_mc_new, nv44_mc_new, nv50_mc_new, g84_mc_new`; they bind the generic master control subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/mmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/mmu.h

## Purpose

This header defines the MMU and virtual-memory manager interfaces: VMA allocation state, VMM address-space lifetime, page-table joins, mapping descriptors, user memory/VMM lookup, memory heap/type capabilities, and generation-specific MMU constructors.

## Important APIs, Types, and Functions

Important types include `struct nvkm_vma`, `struct nvkm_vmm`, `struct nvkm_vmm_map`, and `struct nvkm_mmu`. Important APIs are `nvkm_vmm_new`, `nvkm_vmm_ref`, `nvkm_vmm_unref`, `nvkm_vmm_boot`, `nvkm_vmm_join`, `nvkm_vmm_part`, `nvkm_vmm_get`, `nvkm_vmm_put`, `nvkm_vmm_map`, `nvkm_vmm_unmap`, `nvkm_umem_search`, and `nvkm_uvmm_search`.

## Control Flow

Callers create a VMM over an address range, optionally bootstrap/join backing page-directory memory, allocate VMAs from managed free trees, map NVKM memory or scatter/PFN sources into a VMA, and unmap/put regions when no longer needed. MMU constructors publish heap/type capabilities and invalidation synchronization used by engines.

## State and Persistence Behavior

VMAs persist address, size, page selection/ref state, sparse/busy/mapped/no-compression flags, mapped memory, and compression tags. VMMs persist managed ranges, free/used trees, page directory roots, engine refs, null page, replay flag, and optional GSP RM handles. MMU state persists DMA width, memory heaps/types, default VMM, PTC/PTP lists, and invalidation mutex.

## Dependencies and Integration Points

It integrates with memory objects, GPU objects, BAR mappings, FIFO/GR TLB invalidation, GSP RM VMM objects, user NVIF handles, and all GPU memory allocation paths.

## Risks

VMA split/part/mapref state is subtle and can leak page-table refs or expose stale mappings. Compression-tag mismatch corrupts compressed surfaces. Missing invalidation synchronization causes GPU faults after remap. Sparse mappings must not be treated as resident memory.

## Test Signals

Exercise VMM creation/destruction, VMA allocation splitting, map/unmap with memory/SG/PFN sources, compression tags, sparse mappings, GSP external VMM handles, engine ref accounting, and fault replay paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/mxm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/mxm.h

## Purpose

This file defines the MXM subdevice contract for Nouveau/NVKM. It covers MXM board-information subdevice constructor declarations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_subdev_type`, `nvkm_subdev`, `nv50_mxm_new`. Important callable entry points include `nv50_mxm_new`. The visible chip-family constructors are `nv50_mxm_new`; they bind the generic MXM subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/mxm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/pci.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/pci.h

## Purpose

This file defines the PCI subdevice contract for Nouveau/NVKM. It covers PCIe speed/width state, config-space helpers, ROM shadow control, MSI rearm, and link-speed programming.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_pcie_speed`, `nvkm_pci`, `nvkm_pci_func`, `nvkm_subdev`, `pci_dev`, `agp_bridge_data`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_pci_rd32`, `nvkm_pci_wr08`, `nvkm_pci_wr32`, `nvkm_pci_mask`, `nvkm_pci_rom_shadow`, `nvkm_pci_msi_rearm`. Important callable entry points include `nvkm_pci_rd32`, `nvkm_pci_wr08`, `nvkm_pci_wr32`, `nvkm_pci_mask`, `nvkm_pci_rom_shadow`, `nvkm_pci_msi_rearm`, `nv04_pci_new`, `nv40_pci_new`, `nv46_pci_new`, `nv4c_pci_new`. The visible chip-family constructors are `nv04_pci_new, nv40_pci_new, nv46_pci_new, nv4c_pci_new`; they bind the generic PCI subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/pmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/pmu.h

## Purpose

This file defines the PMU subdevice contract for Nouveau/NVKM. It covers Falcon-backed power-management controller messaging, fan/power-gating hooks, and memory-script command construction.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_pmu`, `nvkm_pmu_func`, `nvkm_subdev`, `nvkm_falcon`, `nvkm_falcon_qmgr`, `nvkm_falcon_cmdq`, `nvkm_falcon_msgq`, `completion`, `mutex`, `work_struct`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_memx`, `nvkm_pmu_send`. Important callable entry points include `nvkm_pmu_send`, `nvkm_pmu_pgob`, `nvkm_pmu_fan_controlled`, `gt215_pmu_new`, `gf100_pmu_new`, `gf119_pmu_new`, `gk104_pmu_new`, `gk110_pmu_new`, `gk208_pmu_new`, `gk20a_pmu_new`. The visible chip-family constructors are `gt215_pmu_new, gf100_pmu_new`; they bind the generic PMU subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/privring.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/privring.h

## Purpose

This file defines the privring subdevice contract for Nouveau/NVKM. It covers private-ring constructor declarations for register-ring bring-up and recovery.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_subdev_type`, `nvkm_subdev`, `gf100_privring_new`, `gf117_privring_new`, `gk104_privring_new`, `gk20a_privring_new`, `gm200_privring_new`, `gp10b_privring_new`. Important callable entry points include `gf100_privring_new`, `gf117_privring_new`, `gk104_privring_new`, `gk20a_privring_new`, `gm200_privring_new`, `gp10b_privring_new`. The visible chip-family constructors are `gf100_privring_new, gf117_privring_new, gk104_privring_new, gk20a_privring_new, gm200_privring_new, gp10b_privring_new`; they bind the generic privring subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/privring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/therm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/therm.h

## Purpose

This file defines the thermal subdevice contract for Nouveau/NVKM. It covers thermal thresholds, fan modes, sensor attributes, clock-gating packs, fan PWM/Tach operations, and thermal constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_therm_thrs_direction`, `nvkm_therm_thrs_state`, `nvkm_therm_thrs`, `nvkm_therm_fan_mode`, `nvkm_therm_attr_type`, `nvkm_therm_clkgate_init`, `nvkm_therm_clkgate_pack`, `nvkm_therm`, `nvkm_therm_func`, `nvkm_subdev`, `nvkm_alarm`, `nvbios_therm_trip_point`, `nvbios_therm_sensor`, `nvkm_fan`. Important callable entry points include `nvkm_therm_temp_get`, `nvkm_therm_fan_sense`, `nvkm_therm_cstate`, `nvkm_therm_clkgate_init`, `nvkm_therm_clkgate_enable`, `nvkm_therm_clkgate_fini`, `nv40_therm_new`, `nv50_therm_new`, `g84_therm_new`, `gt215_therm_new`. The file exposes the thermal subdevice interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/therm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/timer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/timer.h

## Purpose

This file defines the timer subdevice contract for Nouveau/NVKM. It covers device timer reads, alarm scheduling, wait-test helpers, and polling macros for MMIO waits.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_alarm`, `list_head`, `nvkm_timer`, `nvkm_timer_func`, `nvkm_subdev`, `nvkm_timer_wait`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_timer_read`, `nvkm_timer_alarm`, `nvkm_timer_wait_init`, `nvkm_timer_wait_test`, `nv04_timer_new`, `nv40_timer_new`. Important callable entry points include `nvkm_alarm_init`, `nvkm_timer_read`, `nvkm_timer_alarm`, `nvkm_timer_wait_init`, `nvkm_timer_wait_test`, `nv04_timer_new`, `nv40_timer_new`, `nv41_timer_new`, `gk20a_timer_new`. The visible chip-family constructors are `nv04_timer_new, nv40_timer_new, nv41_timer_new, gk20a_timer_new`; they bind the generic timer subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/top.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/top.h

## Purpose

This file defines the TOP discovery subdevice contract for Nouveau/NVKM. It covers topology parsing, block address/reset/intr/fault lookup, and per-generation TOP constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_top`, `nvkm_top_func`, `nvkm_subdev`, `list_head`, `nvkm_top_device`, `nvkm_subdev_type`, `nvkm_device`, `nvkm_top_parse`, `nvkm_top_addr`, `nvkm_top_reset`, `nvkm_top_intr_mask`, `nvkm_top_fault_id`, `gk104_top_new`, `ga100_top_new`. Important callable entry points include `nvkm_top_parse`, `nvkm_top_addr`, `nvkm_top_reset`, `nvkm_top_intr_mask`, `nvkm_top_fault_id`, `gk104_top_new`, `ga100_top_new`. The visible chip-family constructors are `gk104_top_new, ga100_top_new`; they bind the generic TOP discovery subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/top.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/vfn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/vfn.h

## Purpose

This file defines the virtual function subdevice contract for Nouveau/NVKM. It covers SR-IOV/virtual-function state, function IDs, and per-generation constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_vfn`, `nvkm_vfn_func`, `nvkm_subdev`, `nvkm_intr`, `nvkm_device_oclass`, `nvkm_device`, `nvkm_subdev_type`, `gv100_vfn_new`, `tu102_vfn_new`, `ga100_vfn_new`. Important callable entry points include `gv100_vfn_new`, `tu102_vfn_new`, `ga100_vfn_new`. The visible chip-family constructors are `gv100_vfn_new, tu102_vfn_new, ga100_vfn_new`; they bind the generic virtual function subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/vfn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/vga.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/vga.h

## Purpose

This file defines the VGA helper interface contract for Nouveau/NVKM. It covers VGA port/SEQ/GRA/CRT/attribute helpers, VGA lock handling, and ownership accessors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_device`, `nvkm_rdport`, `nvkm_wrport`, `nvkm_rdvgas`, `nvkm_wrvgas`, `nvkm_rdvgag`, `nvkm_wrvgag`, `nvkm_rdvgac`, `nvkm_wrvgac`, `nvkm_rdvgai`, `nvkm_wrvgai`, `nvkm_lockvgac`, `nvkm_rdvgaowner`, `nvkm_wrvgaowner`. Important callable entry points include `nvkm_rdport`, `nvkm_wrport`, `nvkm_rdvgas`, `nvkm_wrvgas`, `nvkm_rdvgag`, `nvkm_wrvgag`, `nvkm_rdvgac`, `nvkm_wrvgac`, `nvkm_rdvgai`, `nvkm_wrvgai`. The file exposes the VGA helper interface interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/vga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/volt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/volt.h

## Purpose

This file defines the voltage subdevice contract for Nouveau/NVKM. It covers voltage VID tables, range maps, get/set operations, speedo readings, and per-generation voltage constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_volt`, `nvkm_volt_func`, `nvkm_subdev`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_volt_map`, `nvkm_volt_map_min`, `nvkm_volt_get`, `nvkm_volt_set_id`, `nv40_volt_new`, `gf100_volt_new`, `gf117_volt_new`, `gk104_volt_new`, `gk20a_volt_new`. Important callable entry points include `nvkm_volt_map`, `nvkm_volt_map_min`, `nvkm_volt_get`, `nvkm_volt_set_id`, `nv40_volt_new`, `gf100_volt_new`, `gf117_volt_new`, `gk104_volt_new`, `gk20a_volt_new`, `gm20b_volt_new`. The visible chip-family constructors are `nv40_volt_new, gf100_volt_new, gf117_volt_new, gk104_volt_new, gk20a_volt_new, gm20b_volt_new`; they bind the generic voltage subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/volt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvrm/nvtypes.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvrm/nvtypes.h

## Purpose

This header provides NVIDIA RM-compatible scalar typedefs and alignment macros used by Nouveau's generated or imported GSP/RM interface structures.

## Important APIs, Types, and Functions

Key declarations are `NV_ALIGN_BYTES`, `NV_DECLARE_ALIGNED`, `NvV32`, `NvU8`, `NvU16`, `NvU32`, `NvU64`, `NvP64`, `NvBool`, `NvHandle`, `NvLength`, `RmPhysAddr`, `NV_STATUS`, and `rpc_generic_union`.

## Control Flow

There is no executable flow. The typedefs allow RM/GSP protocol headers to express fixed-width ABI fields with names matching NVIDIA's firmware interface.

## State and Persistence Behavior

The header stores no state. It affects binary layout and ABI compatibility for structs that may be shared with firmware or RM-style RPC payloads.

## Dependencies and Integration Points

It integrates generated GSP/RM headers with Linux fixed-width integer types and compiler alignment attributes.

## Risks

Changing typedef widths or alignment macros would break firmware ABI layouts. Pointer-like `NvP64` fields must remain explicit 64-bit protocol addresses rather than native kernel pointers when used in wire structures.

## Test Signals

Compile generated RM headers, assert structure sizes/offsets for GSP RPC payloads, and boot GSP firmware that consumes aligned protocol structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvrm/nvtypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_abi16.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_abi16.c

## Purpose

This file implements Nouveau's legacy ABI16 DRM/NVIF compatibility layer. It preserves old userspace ioctls for parameters, Z-cull information, channel allocation/free, engine object allocation, notifier allocation, GPU object freeing, and a restricted subset of the old `DRM_NOUVEAU_NVIF` object API.

## Important APIs, Types, and Functions

Important entry points are `nouveau_abi16_get`, `nouveau_abi16_put`, `nouveau_abi16_fini`, `nouveau_abi16_swclass`, `nouveau_abi16_ioctl_getparam`, `nouveau_abi16_ioctl_get_zcull_info`, `nouveau_abi16_ioctl_channel_alloc`, `nouveau_abi16_ioctl_channel_free`, `nouveau_abi16_ioctl_grobj_alloc`, `nouveau_abi16_ioctl_notifierobj_alloc`, `nouveau_abi16_ioctl_gpuobj_free`, and `nouveau_abi16_ioctl`. Internal tracking uses `struct nouveau_abi16_obj`, `struct nouveau_abi16_chan`, and `struct nouveau_abi16_ntfy`.

## Control Flow

The `get` helper lazily allocates ABI16 state under the client mutex; `put` releases that mutex. Channel allocation disables late UVMM mixing, selects a runlist/engine, creates a Nouveau channel, optionally creates a scheduler for VM_BIND clients, applies CE compatibility workarounds, allocates/pins a notifier buffer, maps it for Tesla+, creates a GEM handle, and initializes an `nvkm_mm` notifier heap. Object allocation maps legacy class aliases to available NVIF classes before constructing objects under the channel user object. Notifier allocation suballocates from the notifier heap and builds an old `NV_DMA_IN_MEMORY` object against VM, AGP, or buffer offsets. The restricted NVIF ioctl path copies user data, validates route/version, dispatches sclass/new/del/mthd, and copies results back.

## State and Persistence Behavior

Per-file state lives on `nouveau_cli->abi16`: lists of legacy channels and tracked NVIF objects. Each channel owns a Nouveau channel, optional CE workaround object, notifier BO/VMA, notifier heap, scheduler, and notifier objects. Cleanup idles channels, destroys scheduler state, frees notifiers, unpins buffers, tears down NVIF objects, and clears `cli->abi16`.

## Dependencies and Integration Points

It depends on DRM ioctl copying, NVIF object/class/device APIs, Nouveau channel/GEM/VMA/scheduler helpers, TTM memory usage reporting, NVKM GR/MM range helpers, and legacy UAPI structures from `drm_nouveau_drm.h`.

## Risks

The layer intentionally allows old userspace behavior, so compatibility hacks are easy to regress. Mutex ownership is coupled to `nouveau_abi16_get/put`; early returns must release it. User-provided handles/classes need strict validation. Notifier heap offsets differ across VM, AGP, and pre-Tesla paths. UVMM and ABI16 UAPIs must not be mixed after initialization.

## Test Signals

Run legacy Mesa/DDX channel creation, getparam coverage, Z-cull ioctl on supported/unsupported GR, object class alias allocation, notifier allocation/free on pre-Fermi and Tesla paths, restricted NVIF new/sclass/mthd/del, malformed ioctl size/version/route tests, and client teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_abi16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_abi16.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_abi16.h

## Purpose

This header declares the legacy ABI16 compatibility structures and ioctl entry points implemented by `nouveau_abi16.c`.

## Important APIs, Types, and Functions

It defines `ABI16_IOCTL_ARGS`, `struct nouveau_abi16_ntfy`, `struct nouveau_abi16_chan`, `struct nouveau_abi16`, `struct drm_nouveau_grobj_alloc`, `struct drm_nouveau_setparam`, domain flags `NOUVEAU_GEM_DOMAIN_VRAM/GART`, legacy ioctl numbers, and prototypes for getparam, Z-cull, channel/object/notifier operations, `nouveau_abi16_get`, `nouveau_abi16_put`, `nouveau_abi16_fini`, `nouveau_abi16_swclass`, and `nouveau_abi16_ioctl`.

## Control Flow

The header has no direct execution; DRM ioctl tables and Nouveau client teardown paths include it to dispatch old UAPI requests into the ABI16 implementation.

## State and Persistence Behavior

The structures define per-client ABI16 state: channel lists, tracked NVIF objects, per-channel notifier heaps, notifier BO/VMA, optional scheduler, and notifier object nodes.

## Dependencies and Integration Points

It integrates legacy DRM Nouveau UAPI definitions with Nouveau's modern `nouveau_cli`, `nouveau_channel`, `nouveau_bo`, `nouveau_vma`, NVIF object, and NVKM MM types.

## Risks

Structure layout and ioctl numbers are user ABI and must not drift. Locking expectations around `nouveau_abi16_get/put` are implicit and must be followed by callers.

## Test Signals

Build old-UAPI ioctl dispatch, run legacy userspace allocation/free paths, and verify teardown frees all ABI16 channels/notifiers/objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_abi16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_acpi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_acpi.c

## Purpose

This file handles Nouveau's ACPI integration for hybrid graphics. It detects legacy DSM and Optimus DSM methods, registers a VGA switcheroo handler, programs mux/power DSM calls, prepares Optimus powerdown flags, obtains ACPI panel EDID, and delegates ACPI video backlight registration decisions.

## Important APIs, Types, and Functions

Public functions are `nouveau_is_optimus`, `nouveau_is_v1_dsm`, `nouveau_register_dsm_handler`, `nouveau_unregister_dsm_handler`, `nouveau_switcheroo_optimus_dsm`, `nouveau_acpi_edid`, `nouveau_acpi_video_backlight_use_native`, and `nouveau_acpi_video_register_backlight`. Internal helpers include `nouveau_optimus_dsm`, `nouveau_dsm_get_optimus_functions`, `nouveau_dsm`, `nouveau_dsm_switch_mux`, `nouveau_dsm_set_discrete_state`, `nouveau_dsm_pci_probe`, and `nouveau_dsm_detect`.

## Control Flow

Detection scans display-class PCI devices, checks NVIDIA ACPI handles for the legacy and Optimus DSM GUIDs, records whether mux/power/flags/PR3 support exists, and registers switcheroo when a usable method is found. Switcheroo calls route mux changes to MXM WMI and DSM LED functions and route discrete power changes to DSM power functions. Optimus powerdown first sets flags when supported, then requests PS3 powerdown through the capabilities DSM unless PR3 resources mean DSM should be skipped. EDID access is limited to LVDS/eDP and uses ACPI video.

## State and Persistence Behavior

Static `nouveau_dsm_priv` records DSM/Optimus detection, flags support, PR3 skip behavior, and the ACPI handle. This persists across device registration until module unload; the switcheroo handler is registered only when detection succeeds.

## Dependencies and Integration Points

It depends on ACPI DSM evaluation, PCI topology, MXM WMI, VGA switcheroo, ACPI video EDID/backlight helpers, and DRM connector types. The header provides stubs when ACPI/X86 or switcheroo support is absent.

## Risks

Vendor BIOS DSM behavior is inconsistent; function-0 probing requires a private Optimus DSM implementation. Incorrect PR3/DSM selection can power off hardware incorrectly. PCI scanning heuristics can misclassify integrated/discrete devices. DSM failures are often logged but not fatal.

## Test Signals

Test Optimus and legacy mux laptops, PR3-capable systems, systems without DSM, ACPI EDID on LVDS/eDP, switcheroo on/off and mux switching, suspend/resume power transitions, and builds without ACPI/X86/VGA_SWITCHEROO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_acpi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_acpi.h

## Purpose

This header declares Nouveau's ACPI helper API and provides no-op/static fallback implementations when ACPI-on-x86 support is not compiled in.

## Important APIs, Types, and Functions

It defines `ROM_BIOS_PAGE` and declares or stubs `nouveau_is_optimus`, `nouveau_is_v1_dsm`, `nouveau_register_dsm_handler`, `nouveau_unregister_dsm_handler`, `nouveau_switcheroo_optimus_dsm`, `nouveau_acpi_edid`, `nouveau_acpi_video_backlight_use_native`, and `nouveau_acpi_video_register_backlight`.

## Control Flow

Including code can call the helpers unconditionally. On supported builds calls dispatch to `nouveau_acpi.c`; otherwise detection returns false, EDID returns `NULL`, native backlight preference returns true, and registration hooks are empty.

## State and Persistence Behavior

The header itself stores no state. Runtime ACPI detection state is private to the implementation file.

## Dependencies and Integration Points

It is used by Nouveau device registration, switcheroo/power-management paths, EDID retrieval, and backlight setup.

## Risks

Fallback semantics must remain conservative. A wrong `nouveau_acpi_video_backlight_use_native` default would suppress the driver's native backlight on non-ACPI builds.

## Test Signals

Build with and without `CONFIG_ACPI`/`CONFIG_X86`, test Optimus detection consumers, and validate backlight/EDID fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_backlight.c

## Purpose

This file registers and manages Nouveau's native backlight devices for internal LVDS/eDP panels. It supports NV40 register brightness, NV50+ output brightness hooks, eDP AUX/DPCD brightness, Apple GMUX avoidance, ACPI-video fallback, and unique `nv_backlight` naming.

## Important APIs, Types, and Functions

Important functions are `nouveau_backlight_init`, `nouveau_backlight_fini`, `nouveau_backlight_ctor`, `nouveau_backlight_dtor`, `nouveau_get_backlight_name`, `nv40_get_intensity`, `nv40_set_intensity`, `nv40_backlight_init`, `nv50_edp_get_brightness`, `nv50_edp_set_brightness`, `nv50_get_intensity`, `nv50_set_intensity`, and `nv50_backlight_init`. Backlight ops are `nv40_bl_ops`, `nv50_edp_bl_ops`, and `nv50_bl_ops`.

## Control Flow

Initialization skips Apple GMUX, finds an LVDS or eDP encoder, allocates `struct nouveau_backlight`, selects the NV40 or NV50+ backend by GPU family, optionally probes eDP DPCD backlight support, checks ACPI native-backlight preference, reserves a unique IDA-backed name, registers a raw backlight device, stores it on the connector, initializes brightness if needed, and updates status. eDP brightness callbacks take modeset locks and only touch AUX backlight state while the CRTC is active. Teardown unregisters the backlight, frees the ID, clears connector state, and frees memory.

## State and Persistence Behavior

Static `bl_ida` tracks unique backlight names. Per-connector `nouveau_backlight` state stores the registered device, ID, DPCD info, and whether DPCD brightness is used. Hardware brightness persists in NV40 PMC registers, NVIF output state, or panel DPCD registers depending on backend.

## Dependencies and Integration Points

It depends on Linux backlight/IDA APIs, DRM connector/probe/modeset locking, DP AUX/eDP backlight helpers, Nouveau encoder/connector/outp NVIF helpers, ACPI video policy, and Apple GMUX detection.

## Risks

Modeset locking must handle `-EDEADLK` correctly. Registration must not create duplicate native and ACPI backlights. eDP DPCD support probing happens after connector registration and may miss early panel state. Backlight ID cleanup must match successful ID allocation. Ampere support is marked unconfirmed.

## Test Signals

Test NV40 register brightness, NV50 LVDS/eDP brightness, DPCD backlight panels, ACPI fallback, Apple GMUX systems, suspend/resume brightness restoration, connector disconnect/teardown, and deadlock-backoff paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_backlight.c -->
