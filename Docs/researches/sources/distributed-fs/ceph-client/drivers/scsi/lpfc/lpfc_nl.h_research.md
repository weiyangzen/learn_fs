# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nl.h

## Purpose
`lpfc_nl.h` defines the LPFC driver's Fibre Channel transport event masks and payload layouts for one-way driver-to-application notifications. It is the shared event ABI used by driver event producers and userspace/libdfc-style consumers through the FC transport/netlink event path.

## Important APIs, Types, and Constants
- Registration bits include `FC_REG_LINK_EVENT`, `FC_REG_RSCN_EVENT`, `FC_REG_CT_EVENT`, `FC_REG_DUMP_EVENT`, `FC_REG_TEMPERATURE_EVENT`, `FC_REG_VPORTRSCN_EVENT`, `FC_REG_ELS_EVENT`, `FC_REG_FABRIC_EVENT`, `FC_REG_SCSI_EVENT`, `FC_REG_BOARD_EVENT`, and `FC_REG_ADAPTER_EVENT`.
- `FC_REG_EVENT_MASK` is the union of supported registration categories.
- Temperature event codes are `LPFC_CRIT_TEMP`, `LPFC_THRESHOLD_TEMP`, and `LPFC_NORMAL_TEMP`.
- `struct lpfc_rscn_event_header` describes RSCN payloads with flexible `rscn_payload[]` data.
- `struct lpfc_els_event_header`, `struct lpfc_lsrjt_event`, and `struct lpfc_logo_event` describe ELS notifications and special LS_RJT/LOGO payloads.
- `struct lpfc_fabric_event_header` and `struct lpfc_fcprdchkerr_event` describe fabric busy/port busy/FCP read-check errors.
- `struct lpfc_scsi_event_header`, `struct lpfc_scsi_varqueuedepth_event`, and `struct lpfc_scsi_check_condition_event` describe SCSI queue, reset, queue-depth, and check-condition notifications.
- `struct lpfc_board_event_header`, `struct lpfc_adapter_event_header`, and `struct temp_event` cover board, adapter arrival, and temperature events.

## Control Flow and State
The header does not implement event delivery. Producers allocate or fill the defined structures with `event_type` first, followed by subcategory and type-specific fields, then pass the payload to the FC transport notification mechanism. Consumers can parse the first words generically and dispatch by category/subcategory. Registration masks filter which event categories an application receives.

## State and Persistence Behavior
No state is stored in this header. Event state is transient and carried in payload structs. The ABI expectation is persistent: field order, integer widths, and category constants must remain compatible with userspace tools.

## Dependencies and Integration Points
The header relies on fixed-width integer types and driver FC naming conventions. It is included by mailbox/discovery/SCSI/link modules that build event payloads. It integrates with RSCN handling, ELS receipt/reject paths, fabric notifications, SCSI error and queue-depth reporting, board interrupt reporting, adapter arrival notifications, dump events, and temperature monitoring.

## Risks and Edge Cases
- This is a binary payload ABI; changing struct layout, field order, or integer size would break consumers.
- There are duplicate definitions for the temperature codes in the file; they currently match, but future edits must keep them synchronized or remove the duplication carefully.
- Flexible RSCN payload length must be validated by event senders and receivers to avoid truncation or overread.
- WWPN/WWNN fields are raw 8-byte arrays; endianness/formatting must be handled consistently by producers and consumers.
- The broad `FC_REG_EVENT_MASK` must be updated when new event categories are added or userspace cannot subscribe to them through the aggregate mask.

## Test Signals
ABI tests should verify struct sizes/offsets expected by consumers, category mask filtering, RSCN payload-length handling, ELS subcategory dispatch for PLOGI/PRLO/ADISC/LS_RJT/LOGO, fabric and SCSI special-case payload content, temperature event codes, and compatibility with existing userspace event decoders.
