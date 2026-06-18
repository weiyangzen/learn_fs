<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl692_defs.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl692_defs.h

## Purpose
`mxl692_defs.h` defines the MaxLinear Eagle/MxL69x firmware protocol used by `mxl692.c`: packet sizes, firmware format limits, opcodes and debug names, device/demod/power/tuner enums, MPEG/QAM/OOB/ATSC/SMA structs, and packed host-message payloads.

## Important APIs, Types, And Functions
Key constants include host-message header size, firmware header/segment sizes, max I2C packet size, firmware load time, and firmware max size. `enum MXL_EAGLE_OPCODE_E` and `MXL_EAGLE_OPCODE_STRING[]` define all host-command IDs used for device, tuner, ATSC, QAM, OOB, SMA, and internal commands. Important structs include `MXL_EAGLE_HOST_MSG_HEADER_T`, `MXL_EAGLE_DEV_VER_T`, `MXL_EAGLE_DEV_XTAL_T`, `MXL_EAGLE_DEV_STATUS_T`, `MXL_EAGLE_MPEGOUT_PARAMS_T`, `MXL_EAGLE_QAM_DEMOD_PARAMS_T`, `MXL_EAGLE_QAM_DEMOD_STATUS_T`, `MXL_EAGLE_ATSC_DEMOD_STATUS_T`, `MXL_EAGLE_ATSC_DEMOD_ERROR_COUNTERS_T`, and `MXL_EAGLE_TUNER_CHANNEL_PARAMS_T`.

## Control Flow
The header is declarative. `mxl692.c` uses the opcode enum to select endian-swap logic, command names for diagnostics, payload structs for command construction/parsing, and firmware constants during validation/download.

## State And Persistence
These definitions describe firmware wire formats and hardware command semantics. Packed structs are part of the host/firmware ABI. Persistent runtime state lives in firmware and device registers, not in this header.

## Dependencies And Integration Points
The file depends on Linux integer types and `__packed` support through included kernel headers in the C file. It integrates with the MxL692 firmware and with DVB frontend logic that maps Linux modulation/frequency requests into Eagle demod/tuner payloads.

## Risks
Struct packing and endian conversions must match firmware exactly. Changing opcode ordering breaks `MXL_EAGLE_OPCODE_STRING[]` indexing and command IDs. Some constants are duplicated, and many protocol areas are defined even if the current driver only uses a subset, so future feature additions need careful swap/checksum coverage.

## Test Signals
Build tests with structure packing warnings enabled, known-command byte-vector checks, firmware validation/download tests, ATSC and QAM status payload parsing, and endian coverage on big- and little-endian kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl692_defs.h -->
