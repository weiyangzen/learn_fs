<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_sas.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_transport_sas.h

## Purpose
This header defines the generic SAS transport class sysfs/device model for SAS phys, ports, remote phys/end devices/expanders, link rates, TLR, SMP BSG handling, and driver callback templates.

## Important APIs, Types, And Functions
Key types include `enum sas_linkrate`, `struct sas_identify`, `struct sas_phy`, `struct sas_rphy`, `struct sas_end_device`, `struct sas_expander_device`, `struct sas_port`, `struct sas_phy_linkrates`, and `struct sas_function_template`. APIs allocate/add/delete/free phys, rphys, and ports; add/delete phys to ports; remove children/hosts; query SAS address/TLR/ATA NCQ priority; attach/release transport; read port mode page; and identify SAS device/phy/port/local/expander devices.

## Control Flow
Drivers attach a SAS transport template, allocate phys and ports under host devices, attach rphys for end devices or expanders, and expose link/error attributes. SMP requests can be dispatched through the template `smp_handler`. Port membership is managed by adding/removing phys, while rphy add/remove/delete controls remote-device visibility and SCSI target binding.

## State And Persistence
Transport objects are runtime device-model objects. Phys track enable state, negotiated/min/max link rates, error counters, SAS identity, port siblings, and hostdata. Ports track phy lists and remote rphy under a mutex. End devices track ready LED and TLR settings; expanders track vendor/product/component strings and levels.

## Dependencies And Integration Points
It depends on Linux transport class, mutex, BSG, SAS protocol definitions, and SCSI host/device model. It is used by libsas and SAS LLDDs to expose topology through sysfs and BSG.

## Risks
The `scsi_is_sas_rphy()` stub returns false when attrs are disabled, so code must handle feature-gated builds. Device lifetimes depend on `put_device()` helpers. Linkrate constants include virtual values outside normal four-bit SAS fields. TLR/NCQ helpers depend on remote/device type.

## Test Signals
Build with/without `CONFIG_SCSI_SAS_ATTRS`, allocate/add/delete phys/rphys/ports, SMP BSG dispatch, link error retrieval, phy reset/enable/speed callbacks, TLR enable/disable, expander detection, local phy detection, and port phy refcounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_sas.h -->
