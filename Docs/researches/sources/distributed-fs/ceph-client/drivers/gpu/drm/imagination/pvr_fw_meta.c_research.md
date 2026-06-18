# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_meta.c

## Purpose
Implements the META firmware-processor backend: slave-port register reads, wrapper setup, LDR firmware parsing, bootloader configuration generation, segment MMU/cache setup, firmware address conversion, VM mapping, and META IRQ handling.

## Important APIs, types, and functions
- `pvr_meta_cr_read32()` reads META registers through the slave port with ready/idle polling.
- `pvr_meta_wrapper_init()` programs META boot mode and Garten wrapper fence settings.
- LDR parsing helpers `meta_ldr_cmd_loadmem()`, `meta_ldr_cmd_zeromem()`, `meta_ldr_cmd_config()`, and `process_ldr_command_stream()` populate code/data/core sections and boot configuration.
- Boot configuration helpers `configure_seg_id()`, `configure_seg_mmu()`, and `configure_meta_caches()` append register/value pairs to the bootloader argument area.
- `pvr_meta_fw_process()`, `pvr_meta_init()`, `pvr_meta_get_fw_addr_with_offset()`, `pvr_meta_vm_map()`, `pvr_meta_vm_unmap()`, `pvr_meta_irq_pending()`, and `pvr_meta_irq_clear()` implement `pvr_fw_defs_meta`.

## Control flow
META init declares a 32 MiB firmware heap. Processing starts by writing privileged JTAG access, then configures the segment MMU for the FW data section, walks the META LDR command stream, appends cache setup, terminates the boot argument list, and optionally supplies coremem code address/size. LDR `LOADMEM` copies firmware payloads into the host section backing selected by `pvr_fw_find_mmu_segment()`, `ZEROMEM` clears non-coremem ranges, and `CONFIG` converts firmware register-write commands into bootloader arguments.

Wrapper initialization sets META master boot mode, routes Garten idle to META, and configures wrapper fence PC/DM fields. Firmware address conversion adds the META data segment base and sets uncached bits for uncached FW objects. VM mapping uses the kernel VM context at the reserved firmware heap address.

## State and persistence
META-specific persistent state is mostly encoded in bootloader arguments written into the FW code allocation and in the common firmware heap metadata. No processor-private heap object is allocated in this file. FW object mappings persist in the kernel VM context until common FW object teardown.

## Dependencies and integration points
Depends on Rogue META register definitions, LDR block structures, feature `meta_coremem_size`, common firmware layout helpers, kernel VM mapping, and common start/stop code. `pvr_fw_start()` calls the wrapper callback; `pvr_fw_stop()` uses `pvr_meta_cr_read32()` to decide whether debugger halt state permits skipping Garten idle polling.

## Risks
The LDR parser is firmware input parsing and relies on bounds checks around nested L1/L2 blocks; malformed lengths or offsets return `-EINVAL`. The `switch` syntax is unusual but compiles as a switch over `l1_data->cmd & mask`; future edits could easily break it. Segment and cache register sequences are boot-critical, and address cacheability is encoded in firmware-visible addresses.

## Test signals
Test with valid META LDR firmware, malformed LDR next pointers and block lengths, missing FW data layout entries, coremem present/absent, slave-port timeout paths, META IRQ status/clear, and boot failures after wrapper/segment/cache changes.
