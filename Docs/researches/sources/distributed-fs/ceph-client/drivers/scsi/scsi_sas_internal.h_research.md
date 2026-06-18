# sources/distributed-fs/ceph-client/drivers/scsi/scsi_sas_internal.h

## Purpose

`scsi_sas_internal.h` defines the private container used by the SAS transport implementation to extend the generic `scsi_transport_template` with SAS-specific function templates, attribute storage, and transport containers. It is an internal bridge between SAS transport code and the shared SCSI sysfs/transport class machinery.

## Important APIs, types, and functions

The header defines fixed attribute-count constants for SAS host, PHY, port, remote port, end-device, and expander attributes. `struct sas_internal` embeds `struct scsi_transport_template t`, pointers to `struct sas_function_template` and `struct sas_domain_function_template`, private arrays of `struct device_attribute`, transport containers for each SAS object class, and null-terminated attribute pointer arrays used by `scsi_sysfs.c`/transport code. `to_sas_internal(tmpl)` maps a generic transport template pointer back to the surrounding SAS-private object.

## Control flow

There is no function flow in the header. SAS transport setup code populates the embedded template, private attributes, and attribute pointer arrays, then passes the generic transport template into SCSI core paths. Later callbacks recover the full SAS object through `to_sas_internal()`.

## State and persistence behavior

Instances of `struct sas_internal` persist as transport-template state allocated by SAS transport registration. The arrays hold per-transport attribute definitions, not per-device dynamic data. The header itself owns no allocation or teardown logic.

## Dependencies and integration points

The header assumes the SAS transport implementation has included definitions for `struct scsi_transport_template`, SAS function templates, device attributes, and transport containers. It integrates with `scsi_transport_sas.c`, generic transport class registration, and sysfs attribute generation for SAS PHYs, ports, remote PHYs, end devices, and expanders.

## Risks and edge cases

The fixed attribute counts must match the number of attributes populated by SAS transport code; under-counting causes array overflow, and over-counting can leave unexpected empty entries. The null-terminated pointer arrays reserve one extra slot; writers must preserve termination. Because the generic template is embedded as the first named member used by `container_of()`, any refactor must keep `to_sas_internal()` synchronized with the struct layout.

## Test signals

Compile SAS transport support and boot with SAS hardware or emulated SAS objects. Sysfs tests should verify expected attribute counts and names for host, PHY, port, rphy, end-device, and expander objects. Static checks should compare the count constants against the initializer code in the SAS transport implementation.
