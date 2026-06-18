# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/coredump.h

## Purpose

`coredump.h` defines the ath10k firmware crash dump ABI and the compile-time interface between core recovery, bus crash collectors, and devcoredump packaging. It describes dump TLVs, file header format, RAM-region descriptors, memory layout tables, and inline no-op stubs when `CONFIG_DEV_COREDUMP` is disabled.

## Important APIs and Types

`ATH10K_FW_CRASH_DUMP_VERSION` is the binary file version. `enum ath10k_fw_crash_dump_type` defines TLV payloads for register dumps, CE data, and RAM data. `struct ath10k_tlv_dump_data` is the generic TLV envelope. `struct ath10k_dump_file_data` is the top-level file header containing magic, length, version, GUID, chip/bus/target/firmware/radio metadata, kernel version, timestamp, reserved space, and variable TLV data.

`struct ath10k_dump_ram_data_hdr` prefixes each dumped memory region with region type, start, and payload length. `enum ath10k_mem_region_type` is marked as user-space ABI and covers REG, DRAM, AXI, IRAM1, IRAM2, IOSRAM, IOREG, and MSA. `ATH10K_MAGIC_NOT_COPIED` is the fill byte for holes in partially copied regions.

`struct ath10k_mem_section`, `struct ath10k_mem_region`, and `struct ath10k_hw_mem_layout` describe safe readable regions per hardware version and bus. Sections must be strictly ordered because bus dump processing depends on range order.

The real API under `CONFIG_DEV_COREDUMP` exposes submit, new crash data, create/register/unregister/destroy, and memory layout lookup functions. The disabled-config branch supplies stubs so callers do not need extensive ifdefs.

## Control Flow and State

The header establishes a two-phase lifecycle: allocate generic crash data during core object creation, then register/allocate layout-dependent RAM storage after hardware target information is available. Crash collectors call `ath10k_coredump_new()` under `dump_mutex` to stamp GUID/time and then fill the shared `struct ath10k_fw_crash_data` declared in `core.h`. Recovery later calls `ath10k_coredump_submit()`.

The layout lookup split is deliberate: `ath10k_coredump_get_mem_layout()` respects the global mask, while `_ath10k_coredump_get_mem_layout()` returns layouts independent of mask for non-dump features such as IRAM recovery.

## Dependencies and Integration Points

The header includes `core.h` and exports `ath10k_coredump_mask`, tying dump behavior to the module parameter in `core.c`. Bus implementations consume the memory-region types and section metadata to know what to read. User-space dump decoders depend on the struct layout, magic, version, TLV ids, region type enum values, little-endian fields, and the not-copied fill marker.

## Risks

Because several structs are dump-file ABI, changing field order, sizes, enum values, packing, or magic strings can break existing analyzers. Section ordering requirements are documented but not enforced by the type system. Inline stubs must stay semantically safe for callers that expect allocation or layout lookup to be optional. The stub `ath10k_coredump_new()` returns NULL, so bus crash code must continue to tolerate disabled devcoredump builds.

## Test Signals

Build coverage with `CONFIG_DEV_COREDUMP=y` and disabled is essential. Dump parser tests should validate magic, version, TLV sequence, little-endian metadata, and RAM region headers. Runtime tests should cover mask combinations for register-only, CE-only, RAM-enabled, and disabled dumps, plus hardware without a matching layout.
