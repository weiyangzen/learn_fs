# subset-b-005403 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/device_access/device_access.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/device_access/device_access.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/device_access/device_access.h` defines the public physical device access ABI used by CSS code to read and write device SRAM/register space. It abstracts the system-global base address from local `hrt_address` offsets and exposes aligned scalar and bulk transfers without assuming host pointer size matches the simulated or target CSS address width.

## Important APIs, Types, and Functions

Important APIs are `device_set_base_address()` and `device_get_base_address()` for managing the subsystem base offset, `ia_css_device_load_uint8/16/32/64()` for aligned scalar reads, `ia_css_device_store_uint8/16/32/64()` for aligned scalar writes, and byte-array `ia_css_device_load()` / `ia_css_device_store()` for bulk transfers. `sys_address` is typedefed to `hrt_address` so the ABI stays integer-address based rather than host-pointer based.

## Control Flow

The header itself has no implementation flow, but it defines the expected access sequence for callers and backends: initialize the CSS/device base address, compute local register or SRAM offsets as `hrt_address`, then perform typed scalar or byte-array loads/stores. Implementations must add the configured base address before touching the underlying MMIO, emulated memory, or device-access callback backend.

## State and Persistence Behavior

The header owns no storage, but it defines one important process-wide state concept: the configured device base address. The actual base value and device memory/register contents are stored by the implementation. Store operations mutate live hardware or simulated device state and persist until overwritten, reset, or the backing environment is torn down.

## Dependencies and Integration Points

It depends on `type_support.h` and `system_local.h` for fixed-width values and `hrt_address`. It integrates with `ia_css_device_access.c`, the `ia_css_env` hardware-access callback table, and nearly every host-side CSS component wrapper that needs register or memory access.

## Risks and Edge Cases

The key risks are address-width mismatch, missing base-address initialization, endian/alignment assumptions in scalar loads, and unchecked bulk transfer sizes. Because this ABI deliberately avoids host pointers, implementations must not truncate `hrt_address` values when running simulation or 64-bit host builds.

## Test Signals

Compile tests should include this header from both low-level device code and CSS component wrappers. Unit tests with a fake backend should verify base-address addition, exact scalar widths, endian behavior, aligned access expectations, bulk load/store byte counts, and invalid or uninitialized backend handling in the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/device_access/device_access.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/dma.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/dma.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/dma.h` is a thin cross-cell include wrapper for the DMA device DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/event_fifo.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/event_fifo.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/event_fifo.h` is a thin cross-cell include wrapper for the event FIFO DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/event_fifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/fifo_monitor.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/fifo_monitor.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/fifo_monitor.h` is a thin cross-cell include wrapper for the FIFO monitor DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/fifo_monitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/gdc_device.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/gdc_device.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/gdc_device.h` is a thin cross-cell include wrapper for the geometric distortion correction device DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/gdc_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/gp_device.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/gp_device.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/gp_device.h` is a thin cross-cell include wrapper for the general-purpose device DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/gp_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/gp_timer.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/gp_timer.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/gp_timer.h` is a thin cross-cell include wrapper for the general-purpose timer DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/gp_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/hmem.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/hmem.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/hmem.h` is a thin cross-cell include wrapper for the host memory device DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/hmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/csi_rx_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/csi_rx_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/csi_rx_public.h` declares the host-visible public interface for the CSI-2 receiver front-end/back-end controller within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are csi_rx_fe_ctrl_get_state(), csi_rx_fe_ctrl_dump_state(), csi_rx_fe_ctrl_get_dlane_state(), csi_rx_be_ctrl_get_state(), csi_rx_be_ctrl_dump_state(), and FE/BE register load/store helpers. These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/csi_rx_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/debug_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/debug_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/debug_public.h` declares the host-visible public interface for the SP/ISP debug trace queue within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are debug_data_t/debug_data_ddr_t forward declarations, debug_data_ptr/debug_buffer addresses, debug_dequeue(), debug_synch_queue*(), and debug_buffer_* initialization/mode calls. These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/debug_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/dma_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/dma_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/dma_public.h` declares the host-visible public interface for the CSS DMA register interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are dma_reg_store(), dma_reg_load(), and dma_set_max_burst_size(). These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/dma_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/event_fifo_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/event_fifo_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/event_fifo_public.h` declares the host-visible public interface for the event FIFO token interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are event_wait_for(), cnd_event_wait_for(), event_receive_token(), event_send_token(), is_event_pending(), and can_event_send_token(). These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/event_fifo_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/fifo_monitor_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/fifo_monitor_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/fifo_monitor_public.h` declares the host-visible public interface for the input FIFO monitor and switch interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are fifo_switch_set/get(), fifo_monitor_get_state(), fifo_channel_get_state(), fifo_switch_get_state(), and fifo_monitor register load/store. These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/fifo_monitor_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/gdc_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/gdc_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/gdc_public.h` declares the host-visible public interface for the GDC LUT helper interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are gdc_lut_store(), gdc_lut_convert_to_isp_format(), and gdc_get_unity(). These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/gdc_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/gp_device_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/gp_device_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/gp_device_public.h` declares the host-visible public interface for the general-purpose device register interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are gp_device_get_state(), gp_device_reg_store(), and gp_device_reg_load(). These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/gp_device_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/gp_timer_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/gp_timer_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/gp_timer_public.h` declares the host-visible public interface for the general-purpose timer interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are gp_timer_init() and gp_timer_read(). These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/gp_timer_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/hmem_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/hmem_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/hmem_public.h` declares the host-visible public interface for the HMEM sizing interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are sizeof_hmem(). These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/hmem_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/input_formatter_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/input_formatter_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/input_formatter_public.h` declares the host-visible public interface for the input formatter register/state interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are input_formatter_rst(), input_formatter_set_fifo_blocking_mode(), input_formatter_get_alignment(), switch/state readers, and register load/store. These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/input_formatter_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/irq_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/irq_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/irq_public.h` declares the host-visible public interface for the CSS IRQ and virtual IRQ register interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are irq_reg_load/store(), irq_enable_channel(), irq_enable_pulse(), irq_disable_channel(), irq_clear_all(), irq_get_channel_id(), irq_raise(), and virtual IRQ helpers. These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/irq_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isp_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isp_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isp_public.h` declares the host-visible public interface for the ISP control and DMEM interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are ISP control register helpers, DMEM load/store helpers, ready/sleeping probes, start/wake controls, and interrupt enable helpers. These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isp_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isys_dma_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isys_dma_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isys_dma_public.h` declares the host-visible public interface for the ISYS 2401 DMA interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are isys2401_dma_reg_store(), isys2401_dma_reg_load(), and isys2401_dma_set_max_burst_size(). These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isys_dma_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isys_irq_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isys_irq_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isys_irq_public.h` declares the host-visible public interface for the ISYS IRQ controller interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are isys_irqc_state_get(), isys_irqc_state_dump(), isys_irqc_reg_store/load(), and isys_irqc_status_enable(). These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isys_irq_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isys_stream2mmio_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isys_stream2mmio_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isys_stream2mmio_public.h` declares the host-visible public interface for the ISYS stream-to-MMIO interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are stream2mmio_get_state(), stream2mmio_get_sid_state(), stream2mmio_reg_load/store(), stream2mmio_print_sid_state(), and stream2mmio_dump_state(). These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/isys_stream2mmio_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/mmu_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/mmu_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/mmu_public.h` declares the host-visible public interface for the CSS MMU register/cache interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are mmu_set/get_page_table_base_index(), mmu_invalidate_cache(), mmu_invalidate_cache_all(), and MMU register load/store. These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/mmu_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/pixelgen_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/pixelgen_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/pixelgen_public.h` declares the host-visible public interface for the pixel generator state/register interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are pixelgen_ctrl_get_state(), pixelgen_ctrl_dump_state(), and pixel generator register load/store. These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/pixelgen_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/sp_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/sp_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/sp_public.h` declares the host-visible public interface for the SP control and DMEM interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are SP control register helpers, SP DMEM load/store helpers for byte/word/dword data, start/ready/sleep controls, and interrupt enable helpers. These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/sp_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/tag_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/tag_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/tag_public.h` declares the host-visible public interface for the CSS tag descriptor interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are sh_css_create_tag_descr() and sh_css_encode_tag_descr(). These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/tag_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/timed_ctrl_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/timed_ctrl_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/timed_ctrl_public.h` declares the host-visible public interface for the timed controller command interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are timed_ctrl_reg_store(), timed_ctrl_snd_commnd(), timed_ctrl_snd_sp_commnd(), and timed_ctrl_snd_gpio_commnd(). These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/timed_ctrl_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/vamem_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/vamem_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/vamem_public.h` declares the host-visible public interface for the VAMEM public placeholder within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are public include guard only; VAMEM operations are supplied by selected private/global/local headers elsewhere. These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/vamem_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/vmem_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/vmem_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/vmem_public.h` declares the host-visible public interface for the VMEM public placeholder within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are public include guard only; VMEM operations are supplied by selected private/global/local headers elsewhere. These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/vmem_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/input_formatter.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/input_formatter.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/input_formatter.h` is a thin cross-cell include wrapper for the input formatter DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/input_formatter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/input_system.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/input_system.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/input_system.h` is a thin cross-cell include wrapper for the input system DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/input_system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/irq.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/irq.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/irq.h` is a thin cross-cell include wrapper for the IRQ DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/isp.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/isp.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/isp.h` is a thin cross-cell include wrapper for the ISP cell DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/isp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/isys_irq.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/isys_irq.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/isys_irq.h` is a thin cross-cell include wrapper for the input-system IRQ wrapper. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/isys_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/isys_stream2mmio.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/isys_stream2mmio.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/isys_stream2mmio.h` is a thin cross-cell include wrapper for the input-system stream-to-MMIO DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/isys_stream2mmio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/math_support.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/math_support.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/math_support.h` provides small arithmetic helper macros for ceiling division/multiplication, shift alignment, and modular add support. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: small arithmetic helper macros for ceiling division/multiplication, shift alignment, and modular add support.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/math_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/misc_support.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/misc_support.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/misc_support.h` provides miscellaneous portability helpers such as NOT_USED and alignment byte calculations. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: miscellaneous portability helpers such as NOT_USED and alignment byte calculations.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/misc_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/mmu_device.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/mmu_device.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/mmu_device.h` provides MMU device include wrapper that brings in system-local MMU constants and implementation-specific interfaces. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: MMU device include wrapper that brings in system-local MMU constants and implementation-specific interfaces.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/mmu_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/pixelgen.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/pixelgen.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/pixelgen.h` is a thin cross-cell include wrapper for the pixel generator DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/pixelgen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/platform_support.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/platform_support.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/platform_support.h` provides platform portability definitions such as fixed integer limits and CSS_ALIGN. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: platform portability definitions such as fixed integer limits and CSS_ALIGN.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/platform_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/print_support.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/print_support.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/print_support.h` provides print/log abstraction macros mapping CSS warnings, errors, debug, and generic output to the selected platform backend. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: print/log abstraction macros mapping CSS warnings, errors, debug, and generic output to the selected platform backend.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/print_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/queue.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/queue.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/queue.h` is a thin cross-cell include wrapper for the queue DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/resource.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/resource.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/resource.h` is a thin cross-cell include wrapper for the resource manager DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/sp.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/sp.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/sp.h` is a thin cross-cell include wrapper for the SP cell DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/sp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/tag.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/tag.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/tag.h` is a thin cross-cell include wrapper for the frame tag DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/tag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/timed_ctrl.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/timed_ctrl.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/timed_ctrl.h` is a thin cross-cell include wrapper for the timed-control DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/timed_ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/type_support.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/type_support.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/type_support.h` provides shared CSS integer/bit-width definitions, host address flags, and compatibility includes. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: shared CSS integer/bit-width definitions, host address flags, and compatibility includes.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/type_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/vamem.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/vamem.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/vamem.h` provides VAMEM include wrapper for variable/access memory local/global/private support. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: VAMEM include wrapper for variable/access memory local/global/private support.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/vamem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/vmem.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/vmem.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/vmem.h` is a thin cross-cell include wrapper for the vector memory DLI bridge. It selects the public declaration header or the private inline implementation depending on the component-specific `__INLINE_*__` macro, while always importing `system_local.h` and the component local header first.

## Important APIs, Types, and Functions

The file does not define functions directly. Its important interface is the storage-class macro pair, for example `STORAGE_CLASS_*_H` and `STORAGE_CLASS_*_C`, followed by inclusion of the matching `*_public.h` or `*_private.h`. This pattern lets host, SP, ISP, and simulation builds expose the same names as either external functions or static inline code.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is the key behavior: normal builds include the public declarations, while inline builds include the private implementation after redefining storage-class macros.

## State and Persistence Behavior

No state is owned here. Any state is in the selected local/private/public component files or in hardware registers addressed through those APIs.

## Dependencies and Integration Points

It depends on `system_local.h` for platform addresses/IDs and a component `*_local.h` for device-specific constants. It integrates with the broader AtomISP CSS include hierarchy by normalizing public/private inclusion across cells.

## Risks and Edge Cases

The main risk is include-path or macro skew: a wrong `__INLINE_*__` setting can change linkage semantics, produce duplicate definitions, or hide prototypes. Because the wrapper is shared across cell builds, local header drift can break host and firmware compilation differently.

## Test Signals

Useful signals are compile-only coverage in host and inline configurations, preprocessing checks that the expected public/private header is selected, and link tests that no duplicate or missing component symbols appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/vmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/queue_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/queue_local.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/queue_local.h` provides local queue include guard used to select queue definitions from the build include path. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: local queue include guard used to select queue definitions from the build include path.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/queue_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/queue_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/queue_private.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/queue_private.h` provides private queue include guard for inline/private queue implementation inclusion. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: private queue include guard for inline/private queue implementation inclusion.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/queue_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/tag.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/tag.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/tag.c` provides shared low-level CSS support definitions. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: sh_css_create_tag_descr() and sh_css_encode_tag_descr().

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/tag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/tag_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/tag_local.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/tag_local.h` provides local tag constants including SH_CSS_MINIMUM_TAG_ID. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: local tag constants including SH_CSS_MINIMUM_TAG_ID.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/tag_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/tag_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/tag_private.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/tag_private.h` provides private tag include guard for inline/private tag implementation inclusion. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: private tag include guard for inline/private tag implementation inclusion.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/host/tag_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/queue_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/queue_global.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/queue_global.h` provides global queue include guard for system-wide queue constants. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: global queue include guard for system-wide queue constants.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/queue_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/sw_event_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/sw_event_global.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/sw_event_global.h` provides software event global enums for PSYS/ISYS event IDs and payload count constants. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: software event global enums for PSYS/ISYS event IDs and payload count constants.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/sw_event_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/tag_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/tag_global.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/tag_global.h` provides tag encoding constants and struct sh_css_tag_descr. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: tag encoding constants and struct sh_css_tag_descr.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_shared/tag_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_streaming_to_mipi_types_hrt.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_streaming_to_mipi_types_hrt.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_streaming_to_mipi_types_hrt.h` provides bit-position and mask helpers for packing streaming-to-MIPI channel, format, and data fields. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: bit-position and mask helpers for packing streaming-to-MIPI channel, format, and data fields.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_streaming_to_mipi_types_hrt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_types.h` provides Hive/HRT base scalar widths, boolean constants, byte-size macros, and register size definitions. It is part of the low-level CSS portability and shared ABI layer used by host, SP, ISP, or generated firmware support code.

## Important APIs, Types, and Functions

Important declarations are the macros, constants, enums, or small structs visible in the header. For this file, the inspected symbols include: Hive/HRT base scalar widths, boolean constants, byte-size macros, and register size definitions.

## Control Flow

There is no runtime control flow unless the file provides macro expressions. Its effect is compile-time: it defines constants, masks, type layouts, or include guards consumed by generated CSS code and low-level device wrappers.

## State and Persistence Behavior

No live state is stored here. The important persistence behavior is ABI stability: constants, bit positions, struct layouts, and type widths must remain compatible with firmware, generated binaries, and hardware register encodings.

## Dependencies and Integration Points

Dependencies are intentionally small and usually limited to local CSS type support or generated system headers. Integration is broad because these definitions are pulled into many component wrappers and generated parameter/configuration paths.

## Risks and Edge Cases

Changing bit widths, masks, include guards, or layout structs can silently break firmware/host ABI compatibility. Macro-only helpers also lack type checking, so integer overflow and signedness should be reviewed when sizes or shifts change.

## Test Signals

Compile coverage across host and firmware-style include paths is the baseline. ABI-oriented tests should validate expected sizeof/offset values, packed bit encodings, and generated code preprocessing where these constants are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm.c` is the public HMM entry layer for AtomISP ISP memory management. It exposes allocation, free, load/store, memset, cache flush, physical address lookup, user mmap, and kernel vmap operations for ISP virtual addresses backed by `hmm_bo.c` buffer objects.

## Important APIs, Types, and Functions

Important APIs are hmm_init(), hmm_cleanup(), hmm_alloc(), hmm_create_from_vmalloc_buf(), hmm_free(), hmm_load(), hmm_flush(), hmm_store(), hmm_set(), hmm_virt_to_phys(), hmm_mmap(), hmm_vmap(), hmm_flush_vmap(), and hmm_vunmap(). The file also owns the global `bo_device`, `dummy_ptr`, and `hmm_initialized` variables.

## Control Flow

Initialization calls `hmm_bo_device_init()` with the Merrifield ISP MMU client and ISP virtual address range, marks the subsystem initialized, and allocates a dummy first page because address zero is treated as invalid. Allocation lazily initializes HMM if needed, rounds bytes to pages, allocates a BO, allocates private or vmalloc-backed pages, and binds them into the ISP MMU. Free performs lookup by BO start, unbinds, frees pages, and drops the BO reference. Load/store/set operations locate the BO containing the ISP pointer, prefer an existing or temporary vmap, otherwise walk page-by-page with `kmap_local_page()`, and flush cache lines for CPU/ISP coherency.

## State and Persistence Behavior

State persists in the global `bo_device` rbtree/list allocator, per-BO page arrays and MMU mappings, vmap status bits, and the dummy allocation. There is no file-backed persistence; the durable side effect is live ISP MMU mappings and page cacheability until cleanup/free.

## Dependencies and Integration Points

It depends on Linux page/vmap/kmap/cacheflush APIs, AtomISP logging through `atomisp_dev`, `hmm_bo` primitives, and the ISP MMU implementation from `sh_mmu_mrfld`. It integrates with CSS memory-manager callers that exchange `ia_css_ptr` ISP virtual addresses.

## Risks and Edge Cases

Range validation checks that an address belongs to a BO but most operations do not verify that `bytes` stays inside the BO, so cross-BO or out-of-range copy lengths are a review risk. `hmm_init()` sets `hmm_initialized` even if device init fails. Cache flushing and cached/uncached vmap transitions are subtle, and `hmm_virt_to_phys()` returns `-1` in a physical-address type on failure.

## Test Signals

Exercise init/cleanup, lazy init, zero/one/multi-page allocations, vmalloc-backed allocations, load/store/set across page boundaries, vmap cached and uncached paths, kmap fallback, mmap open/close reference counts, invalid pointers, oversized copy lengths, and MMU bind failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm_bo.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm_bo.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm_bo.c` implements the HMM buffer-object allocator behind AtomISP ISP memory management. It manages ISP virtual address ranges, free/allocated rbtrees, whole-range list ordering, physical page backing, MMU mapping, vmap/mmap exposure, and kref lifetime.

## Important APIs, Types, and Functions

Important APIs are hmm_bo_device_init/exit(), hmm_bo_alloc/release(), search helpers, page allocation/free, MMU bind/unbind, vmap/vunmap/flush, kref helpers, and hmm_bo_mmap(). Internal helpers handle BO initialization, free-tree search, address lookup, split/merge, and removal from size-bucket chains.

## Control Flow

Device init creates the ISP MMU client, sets the virtual range, creates a BO slab cache, seeds one free BO covering the whole range, and inserts it into the free rbtree. Allocation searches the free rbtree by page count, splits larger blocks, inserts allocated blocks by start address, and later page allocation fills either private uncacheable pages or pages derived from a vmalloc buffer. Binding maps each page into the ISP MMU and flushes the TLB range. Release unmaps, frees pages/vmaps as needed, erases the allocated rbtree node, merges adjacent free list neighbors, and reinserts the merged block into the free tree.

## State and Persistence Behavior

Persistent runtime state lives in `struct hmm_bo_device`: MMU client, slab cache, free and allocated rbtrees, the ordered `entire_bo_list`, locks, range start/size, and init flag. Each BO stores start/end, page count, status bits, page array, type, vmap pointer, mmap count, kref, and neighbor links for equal-sized free blocks.

## Dependencies and Integration Points

It depends on Linux rbtrees, lists, mutex/spinlock/kref, page allocation, vmalloc-to-page, cacheability changes, vmap/vunmap, remap_pfn_range, and AtomISP ISP MMU map/unmap/flush hooks. `hmm.c` is its main consumer.

## Risks and Edge Cases

There are several allocator-sensitive edge cases: device init leaks/destroys inconsistently if BO allocation fails after cache creation; `__bo_search_and_remove_from_free_rbtree()` assumes a non-empty root; mmaped BO release intentionally does nothing, so leaked refs can pin address space; freeing private pages always calls `set_pages_array_wb()` and must match successful uncacheable setup; and all byte-range users must avoid crossing BO limits. Concurrency depends on correct rbtree/list lock pairing and BO mutex ordering.

## Test Signals

Use allocation fragmentation tests with split/merge verification, equal-size free-chain tests, page allocation failure injection, MMU map failure rollback, bind/unbind TLB flush checks, vmalloc-backed BO tests, cached/uncached vmap transitions, mmap size mismatch and close/open refcount tests, and cleanup with outstanding mapped or bound BOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm_bo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css.h` is top-level public CSS API umbrella header that includes control, stream, pipe, firmware, buffer, frame, event, IRQ, DVS, metadata, and environment contracts. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are the enums, structs, and prototypes declared in the file. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_3a.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_3a.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_3a.h` is 3A statistics ABI header for ISP-produced auto exposure/white-balance/focus statistics and host-side translation/allocation helpers. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are ia_css_isp_3a_statistics, ia_css_3a_statistics, map structures, static size assertions, statistics translate/get functions, and allocation/free helpers. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_3a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_acc_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_acc_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_acc_types.h` is acceleration and firmware metadata ABI used to describe SP/ISP blobs, binary capabilities, memory sections, parameters, and runtime placement. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are acceleration, cell, and firmware enums plus blob, binary capability, memory offset, parameter, and SP sleep-mode metadata structures. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_acc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_buffer.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_buffer.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_buffer.h` is CSS buffer queue contract tying buffer categories to frame/metadata/3A/DVS payload pointers. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are enum ia_css_buffer_type, struct ia_css_buffer, and ia_css_dequeue_param_buffers(). These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_control.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_control.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_control.h` is CSS lifecycle control API for initialization, SP startup/shutdown, and status probing. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are ia_css_init(), ia_css_uninit(), ia_css_enable_isys_event_queue(), SP/ISP status probes, and ia_css_start_sp()/ia_css_stop_sp(). These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_device_access.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_device_access.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_device_access.c` implements CSS device load/store access by forwarding through the environment-provided hardware access callback table initialized by `ia_css_device_access_init()`.

## Important APIs, Types, and Functions

Important APIs are ia_css_device_access_init(), scalar device loads/stores, and bulk ia_css_device_load()/ia_css_device_store(). They support 8/16/32/64-bit scalar accesses and arbitrary byte-array transfers.

## Control Flow

Initialization stores a pointer to `env->hw_access`. Each scalar load/store calls the corresponding callback with the requested `hrt_address`; bulk load/store pass address, host buffer, and size through the environment table. The implementation is intentionally a thin dispatch layer so the same CSS code can run against PCI MMIO, simulation, or test backends.

## State and Persistence Behavior

The file persists only the selected hardware access environment pointer. The actual device state lives behind the callback implementation in registers or memory. Store calls mutate hardware/device state immediately according to backend semantics.

## Dependencies and Integration Points

It depends on `ia_css_env.h` for callback shapes and on the low-level system address types. It integrates with `device_access.h` and all component public/private headers that need register or memory access.

## Risks and Edge Cases

A missing or partially initialized environment pointer will crash or misroute every access. The layer performs no alignment, bounds, endian, or NULL-buffer checks; those responsibilities sit with callers and backend callbacks.

## Test Signals

Initialize with a fake `ia_css_hw_access_env`, verify every scalar and bulk call forwards exact address/data/size values, then test NULL or incomplete environment handling at higher initialization layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_device_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_device_access.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_device_access.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_device_access.h` is public declaration header for initializing and using CSS device memory/register access callbacks. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are ia_css_device_access_init() and scalar/bulk device load/store prototypes. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_device_access.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_dvs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_dvs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_dvs.h` is digital video stabilization statistics/coefficient ABI and allocation/translation helper declarations. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are DVS/DVS2 statistics types, ISP/host unions, map structures, get/translate functions, allocation/free helpers, and 6-axis config allocation. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_dvs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_env.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_env.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_env.h` is host environment callback table for CPU memory, CSS device access, and print integration. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are ia_css_mem_attr, ia_css_cpu_mem_env, ia_css_hw_access_env, ia_css_print_env, and aggregate ia_css_env callback table. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_err.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_err.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_err.h` is small warning-code header shared by firmware warning events and host diagnostics. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are enum ia_css_fw_warning values used in CSS event reporting. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_event_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_event_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_event_public.h` is public CSS event ABI for PSYS/ISYS queues, frame/statistics/timer/FW warning events, and event masks. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are enum ia_css_event_type masks, IA_CSS_EVENT_TYPE_ALL, struct ia_css_event, ia_css_dequeue_psys_event(), and ia_css_dequeue_isys_event(). These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_event_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_firmware.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_firmware.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_firmware.h` is firmware loading API and firmware image descriptor used by CSS startup. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are struct ia_css_fw, ia_css_load_firmware(), and ia_css_unload_firmware(). These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_frac.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_frac.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_frac.h` is fixed-point fractional support header used by CSS parameter/configuration code. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are fixed-point fractional type support constants/macros used by CSS configuration code. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_frac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_frame_format.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_frame_format.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_frame_format.h` is CSS frame format enumeration defining the pixel layouts supported by CSS buffers and binaries. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are enum ia_css_frame_format and frame/output format count constants. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_frame_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_frame_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_frame_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_frame_public.h` is public frame allocation and frame layout ABI for CSS image buffers. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are frame plane unions, crop/frame info structures, struct ia_css_frame, and frame allocate/init/free/get_info helpers. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_frame_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_host_data.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_host_data.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_host_data.h` is small owned host-data buffer ABI used to pass opaque host payloads through CSS code. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are struct ia_css_host_data and ia_css_host_data_allocate()/ia_css_host_data_free(). These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_host_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_input_port.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_input_port.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_input_port.h` is CSI-2 input port configuration ABI including port selection, lane counts, timeouts, rxcount, and compression settings. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are CSI-2 port macros, compression type structures, and struct ia_css_input_port fields for port, lanes, timeouts, rxcount, and compression. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_input_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_irq.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_irq.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_irq.h` is public interrupt ABI translating hardware/software CSS IRQ bits and CSI receiver error status into host-visible masks. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are IRQ type/info masks, RX error masks, struct ia_css_irq, translate/get/clear helpers, and ia_css_irq_enable(). These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_configs.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_configs.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_configs.c` is generated ISP configuration writer implementation that copies host kernel configuration structs into binary DMEM parameter memory. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are ia_css_configure_iterator/copy_output/crop/fpn/dvs/qplane/output/raw/tnr/ref/vf functions. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_configs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_configs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_configs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_configs.h` is generated ISP configuration ID/offset/prototype header for kernel configuration blocks stored in binary DMEM. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are enum ia_css_configuration_ids, struct ia_css_config_memory_offsets, and generated ia_css_configure_* prototypes. These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_configs.h -->
