<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_log_sas.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_log_sas.h

## Purpose

`mpi_log_sas.h` defines SAS `IOCLogInfo` bit encodings and log codes for Fusion firmware. It covers IOP-originated errors, SAS port-layer/open/link/data-transfer errors, enclosure-management failures, direct-attached SEP errors, and integrated RAID action/compatibility/device-firmware-update failures.

## Important APIs, Types, and Definitions

- `SAS_LOGINFO_NEXUS_LOSS` and `SAS_LOGINFO_MASK` support high-level nexus-loss recognition.
- Originator constants split SAS log info into IOP, PL, and IR domains, selected by `IOC_LOGINFO_ORIGINATOR_MASK`.
- `IOC_LOGINFO_CODE_MASK` and shift identify the code byte within the 32-bit value.
- IOP codes cover invalid SAS address, invalid config page variants, firmware upload failures, diagnostic message errors, task termination, enclosure management command validation, target-assist/status-send termination, target-mode aborts, and timestamp events.
- PL codes and subcodes cover open failure reasons, invalid SGL, wrong relative offset/frame length, frame transfer errors, SATA NCQ and link failures, discovery failures, config-page errors, resets, aborts, device missing delay retry, persistent reservation ownership failures, and enclosure-management transport failures.
- IR codes cover RAID action errors for volume creation/activation, physical disk creation, compatibility failures, and device firmware update mode errors.
- Convenience prefixes combine `MPI_IOCLOGINFO_TYPE_SAS` and originator bits for IOP, PL, and IR values.

## Control Flow

The header has no executable control flow. It defines the decode path for `IOCLogInfo` values returned by SAS-capable firmware. A driver receives a reply or event with nonzero log info, determines the SAS log type and originator, masks out the code and subcode fields, and maps them to transport, firmware-upload, enclosure, target-mode, or IR management diagnostics. `mptbase.c` explicitly points SAS IOCLogInfo decode users at this header.

## State and Persistence Behavior

The log values are transient observations of firmware and link state. Some codes imply durable or semi-durable conditions, such as invalid config pages, persistent table failures, unsupported metadata, RAID compatibility errors, or firmware upload flash-region failures, but the header itself stores no state. Recovery state is maintained by consumers such as SAS topology management, SCSI error handling, RAID management, and enclosure-management code.

## Dependencies and Integration Points

The prefix macros depend on `MPI_IOCLOGINFO_TYPE_SAS` and `MPI_IOCLOGINFO_TYPE_SHIFT`, defined in the common MPI headers included through `mptbase.h`. `mptscsih.c` includes this header for SCSI/SAS error logging; `mptsas.c` and `mptbase.c` consume the same values alongside SAS events from `mpi_ioc.h`, SAS control messages from `mpi_sas.h`, and SAS config pages from `mpi_cnfg.h`.

## Risks and Edge Cases

Several codes carry subcode payloads in the low bits, so exact equality checks can miss families of errors. Some historical names contain typos such as `ERR0R`; these names are source compatibility surface and should not be renamed without a compatibility plan. `PL_LOGINFO_SUB_CODE_OPEN_FAILURE_ZONE_VIOLATION` and `PL_LOGINFO_SUB_CODE_OPEN_FAILURE_ABANDON0` share the same value, so decoders should allow aliases. The header guard name is generic (`IOPI_IOCLOGINFO_H_INCLUDED`) and could collide if another file uses the same guard. Future firmware may return unknown values with known prefixes; decoders should print raw values.

## Test Signals

Tests should verify originator/code/subcode extraction, prefix matching, nexus-loss matching, unknown-code fallback, and alias handling. Runtime signals include readable diagnostics for SATA link down, open failure, invalid SGL, frame transfer error, discovery timeout, enclosure management errors, target-mode aborts, firmware upload failures, RAID creation/activation failures, and compatibility errors during `mptsas` topology or IR workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_log_sas.h -->
