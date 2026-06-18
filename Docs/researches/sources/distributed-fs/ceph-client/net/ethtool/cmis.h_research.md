# sources/distributed-fs/ceph-client/net/ethtool/cmis.h

## Purpose
This header defines the CMIS CDB command data model and function API used by ethtool module firmware flashing. It captures command identifiers, request/reply wire layouts, validation flags, and helper entry points shared between CDB transport and firmware update code.

## Important APIs, Types, And Functions
Important constants include LPL/EPL maximum payload sizes, CDB page/address identifiers, and validation flags `CDB_F_COMPLETION_VALID`, `CDB_F_STATUS_VALID`, and `CDB_F_MODULE_STATE_VALID`. Types include `ethtool_cmis_cdb`, `ethtool_cmis_cdb_cmd_id`, `ethtool_cmis_cdb_request`, `ethtool_cmis_cdb_cmd_args`, `ethtool_cmis_cdb_rpl_hdr`, and `ethtool_cmis_cdb_rpl`. Declared APIs include command composition, completion-flag adjustment, page initialization, CDB init/fini, condition polling, and command execution.

## Control Flow
The header itself has no executable flow. Callers allocate or initialize an `ethtool_cmis_cdb`, compose command args with LPL/EPL payload pointers and validation flags, then execute commands through `ethtool_cmis_cdb_execute_cmd()`.

## State, Persistence, And Dependencies
The central state is the in-memory `ethtool_cmis_cdb` object, which records CMIS revision, allowable read/write length extension, and max completion time for subsequent commands. Request objects contain a copied LPL payload and optionally point at external EPL storage. Dependencies include ethtool module EEPROM access types and netdevice/module firmware notification types.

## Integration Points
`cmis_cdb.c` implements the API. `cmis_fw_update.c` uses it to run CMIS firmware management commands. Module update orchestration in sibling files passes firmware flash parameters and notification handles into these helpers.

## Risks
The structs intentionally mirror CMIS wire layouts; padding, endianness, and checksum coverage are security- and interoperability-sensitive. EPL payload pointers are not owned by the request struct and must remain valid during command execution. Validation flags vary by CMIS revision, so callers must set them carefully.

## Test Signals
Build and ABI tests should verify struct field offsets, command IDs, checksum coverage, LPL/EPL length limits, revision-dependent flags, and firmware update paths that exercise each declared API.
