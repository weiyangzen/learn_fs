<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/sas.h -->
# sources/distributed-fs/ceph-client/include/scsi/sas.h

## Purpose
This header contains SAS protocol constants and packed wire-format structures for SAS, SSP, SMP, SATA FIS embedding, task management, primitives, open reject reasons, GPIO register types, and endian-specific frame layouts.

## Important APIs, Types, And Functions
It defines address sizing/macros, SMP frame/function/result opcodes, SSP frame types, SAM task-management functions and responses, `enum sas_oob_mode`, `enum sas_device_type`, `enum sas_protocol`, `enum phy_func`, `enum sas_prim`, `enum sas_open_rej_reason`, and `enum sas_gpio_reg_type`. Wire types include `struct dev_to_host_fis`, `struct host_to_dev_fis`, `struct sas_identify_frame`, `struct ssp_frame_hdr`, `struct ssp_response_iu`, `struct ssp_command_iu`, `struct xfer_rdy_iu`, `struct ssp_tmf_iu`, `struct report_general_resp`, `struct discover_resp`, `struct report_phy_sata_resp`, and SMP wrapper responses.

## Control Flow
This header has no executable control flow. It provides the constants and layouts consumed by discovery, SMP command generation, SSP command/response parsing, task management, and SATA/STP tunneling. The preprocessor selects little-endian or big-endian bitfield layouts and fails compilation if bitfield order is unknown.

## State And Persistence
No runtime state is stored here. The packed structs represent transient on-wire frames and device responses. SAS addresses are eight-byte big-endian values, and hashed SAS addresses are three-byte protocol fields.

## Dependencies And Integration Points
The header depends on Linux fixed-width types and byteorder definitions. It is included by libsas and SAS transport headers and must match SAS/SMP/SSP protocol bit layouts expected by firmware, expanders, and low-level drivers.

## Risks
Packed bitfield layout is architecture-sensitive; incorrect endian definitions break protocol parsing. Flexible arrays in SSP responses require careful bounds checks. Constants overlap in protocol-defined ways and must not be interpreted without command context. The `SAS_ADDR()` macro assumes aligned-enough storage for dereferencing as `__be64`.

## Test Signals
Compile on little and big endian configurations, validate struct sizes/offsets against SAS specs, parse sample SMP discover/report-phy-SATA frames, build SSP command/TMF IUs, verify task management response decoding, and exercise SATA FIS passthrough through libsas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/sas.h -->
