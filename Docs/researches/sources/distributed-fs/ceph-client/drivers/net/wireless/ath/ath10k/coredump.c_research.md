# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/coredump.c

## Purpose

`coredump.c` implements ath10k firmware crash dump packaging for the Linux devcoredump facility. It maps supported hardware revisions to safe memory regions, sizes optional RAM dumps, allocates crash storage, builds the user-space dump file format, and submits dump buffers when recovery collects crash data.

## Important APIs, Data, and Functions

The file is dominated by static memory layout data. Register section arrays describe safe subranges for QCA6174 variants and IPQ4019/QCA4019 where some registers are intentionally skipped because they can reset state, require PCIe-active access, or cause bus hangs. Region arrays describe DRAM, AXI, IRAM, SRAM, IOREG, and MSA ranges for QCA6174, QCA9377, QCA988X, QCA99X0, QCA9984/QCA9888, QCA4019, and WCN3990. `hw_mem_layouts[]` binds hardware id, hardware revision, and bus to a region table.

`ath10k_coredump_get_mem_layout()` returns a layout only when the global `ath10k_coredump_mask` includes `ATH10K_FW_CRASH_DUMP_RAM_DATA`; `_ath10k_coredump_get_mem_layout()` bypasses the mask and is used by IRAM recovery code in `core.c`. `ath10k_coredump_get_ramdump_size()` sums all region lengths plus one `struct ath10k_dump_ram_data_hdr` per region and aligns the result to 16 bytes.

`ath10k_coredump_new()` initializes per-crash GUID and timestamp under `dump_mutex`. `ath10k_coredump_build()` creates the devcoredump file, writes metadata from `struct ath10k`, and appends selected TLVs for register dump, copy-engine data, and RAM dump. `ath10k_coredump_submit()` passes the final vmalloc buffer to `dev_coredumpv()`. `ath10k_coredump_create()`, `ath10k_coredump_register()`, `ath10k_coredump_unregister()`, and `ath10k_coredump_destroy()` manage persistent crash-data storage.

## Control Flow

Core object creation calls `ath10k_coredump_create()` to allocate `ar->coredump.fw_crash_data` unless coredumps are disabled by mask. After firmware/mac registration has discovered the target version, `ath10k_coredump_register()` allocates the optional RAM dump buffer if the RAM-data bit is enabled and a matching layout exists.

On crash, bus-specific handlers call `ath10k_coredump_new()` and then populate register, CE, and RAM fields. This file does not perform bus reads itself; PCI, SDIO, SNOC, and CE code fill `fw_crash_data`. During recovery, `ath10k_core_restart()` calls `ath10k_coredump_submit()`, which builds a single binary dump with fixed header metadata and requested TLVs.

## State and Persistence

Persistent in-memory state is one `struct ath10k_fw_crash_data` per device, allocated for the device lifetime. The RAM dump buffer may be large and is allocated at registration based on hardware layout. Per-crash mutable fields include GUID, timestamp, register snapshot, CE snapshot, and RAM buffer contents. The devcoredump subsystem owns the submitted buffer after `dev_coredumpv()`.

The user-visible persistence contract is the binary dump file ABI: `df_magic`, version, ath10k/device/firmware/kernel metadata, and TLV records. Endianness is normalized through little-endian fields.

## Dependencies and Integration Points

The file depends on `CONFIG_DEV_COREDUMP`, `linux/devcoredump.h`, `init_utsname()`, ath10k hardware constants, `core.h` crash structures, `debug.h` logging, and the global `ath10k_coredump_mask` defined in `core.c`. Bus crash handlers integrate by using the exported `ath10k_coredump_new()` and memory-layout helpers. `core.c` also uses `_ath10k_coredump_get_mem_layout()` for IRAM backup even when RAM dumps are disabled.

## Risks

The memory layout tables are user-space ABI-adjacent and hardware-sensitive. Incorrect ranges can hang the bus, miss critical crash data, or read invalid target memory. `ath10k_coredump_destroy()` assumes `fw_crash_data` is non-NULL; callers must preserve create/destroy ordering, especially when coredump mask disables allocation. `ath10k_coredump_unregister()` frees `ramdump_buf` without clearing the pointer, while destroy frees and clears if still present; normal lifecycle must not call unregister/destroy in an order that double-frees. Dump size calculations rely on region lengths and preallocated `ramdump_buf_len` matching bus fill logic.

## Test Signals

Important signals are correct layout selection for each bus/hardware tuple, no layout for unsupported hardware, successful RAM buffer allocation only when mask enables RAM data, valid devcoredump output with `ATH10K-FW-DUMP` magic, correctly sized TLVs matching mask bits, crash recovery submitting dumps after simulated firmware crashes, and no bus hangs while PCI/SDIO/SNOC dump readers honor section tables.
