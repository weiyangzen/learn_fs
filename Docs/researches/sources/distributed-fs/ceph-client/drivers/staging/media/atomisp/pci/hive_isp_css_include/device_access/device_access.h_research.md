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
