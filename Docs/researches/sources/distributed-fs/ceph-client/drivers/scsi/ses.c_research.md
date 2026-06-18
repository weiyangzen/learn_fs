# sources/distributed-fs/ceph-client/drivers/scsi/ses.c

## Purpose

`ses.c` implements the SCSI Enclosure Services driver. It binds enclosure devices, reads SES diagnostic pages, registers enclosure components with the generic enclosure class, exposes controls such as fault/locate/active/power/status/id, and matches SCSI devices to enclosure slots using SAS/FCP descriptor information.

## Important APIs, Types, and Functions

`struct ses_device` stores page 1, page 2, and page 10 buffers and lengths. `struct ses_component` stores the parsed address for a component. Command helpers are `ses_recv_diag()` and `ses_send_diag()`. Component callbacks include `ses_get_fault()`, `ses_set_fault()`, `ses_get_status()`, `ses_get_locate()`, `ses_set_locate()`, `ses_set_active()`, `ses_show_id()`, `ses_get_power_status()`, and `ses_set_power_status()`.

Discovery and matching are handled by `ses_process_descriptor()`, `ses_enclosure_find_by_addr()`, `ses_enclosure_data_process()`, `ses_match_to_enclosure()`, `ses_intf_add()`, and removal helpers. Registration uses a SCSI class interface plus `ses_template` as the enclosure SCSI driver.

## Control Flow

`ses_init()` registers the class interface and SCSI driver. `ses_probe()` accepts `TYPE_ENCLOSURE`. `ses_intf_add()` handles both enclosure devices and ordinary devices that might belong to an existing enclosure. For an enclosure, it reads page 1 to discover subenclosures and element types, counts device/array-device components, optionally reads page 2 status/control and page 10 additional status, registers an `enclosure_device`, assigns scratch storage, processes descriptors, and matches already scanned devices.

`ses_enclosure_data_process()` optionally reads page 7 element names and refreshes page 10, then walks all type descriptors. Device and array-device slots allocate or update enclosure components, attach optional names, parse SAS/FCP addresses, and register components. Runtime callbacks refresh page 2 before reading status bits; setters build a selected control descriptor and send page 2 back with SEND DIAGNOSTIC.

Removal distinguishes member devices from enclosure devices. Member removal clears device-to-slot association. Enclosure removal frees diagnostic page buffers and component scratch, drops the enclosure reference, and unregisters it.

## State and Persistence Behavior

Per-enclosure state lives in `edev->scratch` as `struct ses_device`; per-component parsed addresses live in `component[i].scratch`. Page buffers persist for callback use, but page 2 is refreshed before descriptor reads and rewritten for control changes. Hardware remains authoritative for enclosure status and controls.

## Dependencies and Integration Points

The driver depends on SCSI diagnostic commands, SCSI device typing and enclosure detection, the generic enclosure class, SES page formats, unaligned helpers, and SAS transport helpers such as `scsi_is_sas_rphy()` and `sas_get_address()`. User-visible integration is through enclosure sysfs.

## Risks and Edge Cases

SES parsing is length-sensitive. Malformed or short page 1, 7, or 10 data can reduce functionality or abort binding. Page 2 support is optional; without it, controls return defaults or `-EINVAL`. Component numbering for page 2 counts only device and array-device elements while walking all element types, so inconsistent SES pages can target the wrong descriptor. Address matching is strongest for SAS and limited for other protocols.

## Test Signals

Test explicit and embedded enclosures, multiple subenclosures, missing page 2, missing page 7, malformed page 10, SAS slot matching, late device matching, enclosure/member removal, and fault/locate/active/power controls. Robustness tests should feed short or inconsistent diagnostic pages and verify clean failure without leaks.
