# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_hwi.h

## Purpose
`pm8001_hwi.h` defines the SPC/PM8001 hardware-interface ABI used by `pm8001_hwi.c`: inbound and outbound MPI opcodes, packed IOMB request/response payloads, hardware event/status values, register offsets, scratchpad/reset bit definitions, NVMD constants, and device-registration result codes. It is the firmware wire-format contract for the SPC generation of the driver.

## Important APIs, Types, And Constants
The opcode blocks map host-to-firmware requests such as `OPC_INB_PHYSTART`, `OPC_INB_SSPINIIOSTART`, `OPC_INB_SMP_REQUEST`, `OPC_INB_REG_DEV`, `OPC_INB_SATA_HOST_OPSTART`, `OPC_INB_LOCAL_PHY_CONTROL`, `OPC_INB_FW_FLASH_UPDATE`, `OPC_INB_GET_NVMD_DATA`, `OPC_INB_SET_NVMD_DATA`, and `OPC_INB_SAS_RE_INITIALIZE`, plus firmware-to-host responses such as `OPC_OUB_HW_EVENT`, `OPC_OUB_SSP_COMP`, `OPC_OUB_SMP_COMP`, `OPC_OUB_SATA_COMP`, `OPC_OUB_SATA_EVENT`, `OPC_OUB_SSP_EVENT`, abort responses, NVMD responses, and device-state responses.

Packed request/response structs define the exact IOMB payloads: `mpi_msg_hdr`, `phy_start_req`, `phy_stop_req`, SATA FIS wrappers, `sata_completion_resp`, `hw_event_resp`, `reg_dev_req`, `dereg_dev_req`, `dev_reg_resp`, `local_phy_ctl_req/resp`, `hw_event_ack_req`, `ssp_completion_resp`, `sata_event_resp`, `ssp_event_resp`, `general_event_resp`, `smp_req`, `smp_completion_resp`, `task_abort_req/resp`, diagnostic commands, `set_dev_state_req/resp`, `sas_re_initialization_req`, `sata_start_req`, `ssp_ini_tm_start_req`, `ssp_ini_io_start_req`, `fw_flash_Update_req/resp`, and NVMD get/set structures.

The header also defines firmware event/status vocabularies: `HW_EVENT_*`, port states, `IO_*` completion codes, flash/NVMD mode bits, `DEVREG_*` registration statuses, MSGU register offsets, MSI-X table offsets, scratchpad state bits, main/general status table offsets, BAR-shift/reset register addresses, GSM/MBIC/GPIO addresses, and masks such as `OPCODE_BITS`, `NDS_BITS`, `PDS_BITS`, `SHIFT_REG_64K_MASK`, and `SHIFT_REG_BIT_SHIFT`.

## Control Flow
There is no executable control flow, but the file drives runtime switches in `pm8001_hwi.c`. Inbound opcodes select the firmware command built by request helpers. Outbound opcodes select the completion handler in `process_one_iomb()`. `HW_EVENT_*` values select topology handling in `mpi_hw_event()`. `IO_*` values select SCSI/libsas status translation in SSP/SATA/SMP completion handlers. Register and scratchpad constants control initialization, interrupt masking, BAR shifting, soft reset, and forensic dump reads.

## State And Persistence Behavior
The packed structs represent transient messages in inbound/outbound DMA rings. Register constants name hardware state that persists until reset or firmware changes it. NVMD and firmware flash request/response structures are used for persistent adapter-storage operations, but the header stores no state itself.

## Dependencies And Integration Points
The header includes Linux integer types and `scsi/libsas.h` because several payloads embed `struct sas_identify_frame`, `struct dev_to_host_fis`, and `struct ssp_response_iu`. It is tightly integrated with `pm8001_hwi.c` and any code that builds or decodes SPC IOMBs. It also binds the driver to little-endian firmware fields through `__le32` and `__le64`, packed layout, and 4-byte alignment attributes.

## Risks And Edge Cases
Because this header is an ABI contract, struct layout, alignment, field size, and opcode values must not change casually. Flexible or variable protocol data is represented with packed fixed-size IOMBs and in one case a trailing `ssp_response_iu`; users must ensure they do not overrun the configured IOMB size. Duplicate or stale constants can hide firmware-generation differences, and the warning around `IO_ERROR_UNKNOWN_GENERIC` indicates status numbering is used as an index elsewhere. Endianness mistakes are easy because all firmware fields must be converted at the use site.

## Test Signals
Compile-time assertions or build warnings around packed struct sizes would be valuable. Runtime validation should cover representative inbound command payloads, outbound opcode dispatch, IO status translation for common and rare `IO_*` values, hardware event decoding, register offset access during init/reset, NVMD direct and indirect modes, and firmware flash response statuses.
