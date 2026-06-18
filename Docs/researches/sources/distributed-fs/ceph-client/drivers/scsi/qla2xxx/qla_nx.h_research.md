# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx.h

## Purpose

`qla_nx.h` is the hardware contract header for the qla2xxx NX/82xx generation. It defines CRB address windows, on-chip address spaces, firmware/device state registers, IDC/coexistence fields, flash/ROM layout constants, interrupt register mappings, request/response sizing, small DMA scatter-gather helper types, and minidump template entry layouts. It does not implement runtime behavior; it supplies the symbolic register map and binary structure definitions used by `qla_nx.c`, `qla_nx2.c`, mailbox code, init code, and OS glue.

## Important APIs, Types, and Constants

- Phantom/firmware initialization states: `PHAN_INITIALIZE_FAILED`, `PHAN_INITIALIZE_COMPLETE`, `PHAN_INITIALIZE_ACK`, and `PHAN_PEG_RCV_INITIALIZED` are used when polling firmware PEG readiness.
- CRB address helpers: `QLA82XX_CRB_BASE`, `QLA82XX_REG()`, the many `QLA82XX_HW_*_CRB_AGT_ADR` and `QLA82XX_HW_PX_MAP_CRB_*` values, and `QLA82XX_PCI_CRB_WINDOW()` translate logical hardware agents into PCI CRB address windows.
- Driver coexistence/IDC registers: `QLA82XX_CRB_DRV_ACTIVE`, `QLA82XX_CRB_DEV_STATE`, `QLA82XX_CRB_DRV_STATE`, `QLA82XX_CRB_DRV_SCRATCH`, `QLA82XX_CRB_DEV_PART_INFO`, and `QLA82XX_CRB_DRV_IDC_VERSION` provide shared firmware/driver coordination state.
- Device state enum: `QLA8XXX_DEV_UNKNOWN`, `QLA8XXX_DEV_COLD`, `QLA8XXX_DEV_INITIALIZING`, `QLA8XXX_DEV_READY`, `QLA8XXX_DEV_NEED_RESET`, `QLA8XXX_DEV_NEED_QUIESCENT`, `QLA8XXX_DEV_FAILED`, and `QLA8XXX_DEV_QUIESCENT` are the shared state-machine values used by both 82xx and 8044 paths.
- IDC and firmware metadata: `QLA82XX_IDC_VERSION`, ROM init/reset timeouts, lock IDs, firmware version registers, and semaphore registers define how functions coordinate flash/CRB access.
- Interrupt contract: `struct qla82xx_legacy_intr_set`, `QLA82XX_LEGACY_INTR_CONFIG`, `ISR_*` register macros, and `PCIX_INT_VECTOR_BIT_F*` describe per-function legacy interrupt routing.
- Flash/ROM layout: bootloader, firmware, VPD, flash layout offsets, M25P SPI opcodes, unified ROM-image descriptors `struct qla82xx_uri_table_desc` and `struct qla82xx_uri_data_desc`, and image type constants identify firmware images in flash.
- Queue/IO helper types: `struct device_reg_82xx`, `struct fcp_cmnd`, `struct dsd_dma`, `struct ct6_dsd`, and queue size constants define hardware register overlay and CT6 DSD/FCP command metadata.
- Minidump template types: `struct qla82xx_md_template_hdr`, `qla82xx_md_entry_hdr_t`, and specialized entries for CRB, cache, OCM, memory, ROM, mux, and queue captures define the firmware dump binary format.
- Temperature macros and enum: `qla82xx_get_temp_val()`, `qla82xx_get_temp_state()`, `qla82xx_encode_temp()`, and `QLA82XX_TEMP_*` encode ASIC temperature state into a CRB word.

## Control Flow

There is no executable control flow in this header. Control flow is implicit in the contracts it defines:

- Firmware startup code polls `CRB_CMDPEG_STATE`/`CRB_RCVPEG_STATE` for `PHAN_INITIALIZE_COMPLETE`.
- IDC reset and quiesce handlers branch on the `QLA8XXX_DEV_*` values.
- Interrupt handlers use per-function ISR target/status/mask macros and `QLA82XX_LEGACY_INTR_CONFIG` to select the correct register set.
- Flash, ROM, and minidump routines use the packed descriptors to parse firmware-provided tables and execute capture entries.

## State and Persistence Behavior

This header names both volatile MMIO/CRB state and persistent flash layout. Volatile state includes driver-active masks, driver-state acknowledgements, device state, firmware heartbeat/alive counters, PEG halt status, CRB window locks, and temperature state. Persistent state includes flash layout regions, unified ROM image descriptors, bootloader/firmware/VPD offsets, and board info magic values. The packed minidump structs also describe persistent-in-memory dump records produced after firmware failure.

## Dependencies

- Includes `<scsi/scsi.h>` for `struct scsi_lun`.
- Assumes kernel integer, endian, DMA, list, and bit macros/types supplied by surrounding qla2xxx headers before or after inclusion, including `__le16`, `__le32`, `dma_addr_t`, `struct list_head`, `BIT_*`, and `__packed`.
- Shares definitions with `qla_nx2.h`; the 8044 implementation reuses 82xx state values, minidump opcodes, MIU test-agent constants, temperature helpers, and legacy interrupt register offsets.

## Integration Points

- Included from `qla_def.h`, making these definitions visible to the qla2xxx driver.
- Used by `qla_nx.c` for 82xx initialization, firmware control, minidump handling, IDC, and legacy interrupt setup.
- Used indirectly by `qla_nx2.c` for shared device states, firmware PEG state values, MIU test-agent registers, minidump opcodes, temperature helpers, and legacy interrupt offsets.
- Referenced by mailbox/init/OS glue through exported qla82xx/qla8044 operations in `qla_gbl.h` and `qla_os.c`.

## Risks and Edge Cases

- The file encodes large hardware address maps as preprocessor macros; a wrong constant silently redirects MMIO to the wrong hardware block.
- Several CRB window aliases and repeated definitions, such as the duplicate `QLA82XX_CRB_PEG_MD_3`, depend on preprocessor replacement behavior and should be treated carefully during cleanup.
- Packed minidump and ROM descriptor structures are ABI contracts with firmware; field reordering, type-width changes, or padding changes would break parsing.
- Shared `QLA8XXX_DEV_*` enum values are cross-generation protocol values. Adding or changing values requires all IDC state-machine users to be audited.
- Endianness-sensitive fields use `__le16`/`__le32` only in some structs; code that casts raw firmware/flash buffers must continue to use the expected conversion rules.

## Test Signals

- Build coverage for the qla2xxx module with NX/82xx and 8044 support enabled catches missing symbols and struct-layout syntax issues.
- Hardware or emulator probe should verify firmware state polling reaches `PHAN_INITIALIZE_COMPLETE` and IDC state transitions reach `QLA8XXX_DEV_READY`.
- Interrupt tests should validate the legacy per-function status/mask/vector mapping.
- Flash/minidump tests should parse firmware templates and ROM image descriptors without checksum or size failures.
- Temperature and watchdog tests should confirm `qla82xx_get_temp_*` interpretation matches CRB temperature encoding.
