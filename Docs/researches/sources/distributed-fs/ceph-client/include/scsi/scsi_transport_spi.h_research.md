<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_spi.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_transport_spi.h

## Purpose
This header defines the parallel SCSI SPI transport attributes exported to sysfs, including negotiation parameters, domain validation state, signaling type, driver callbacks, and message population helpers.

## Important APIs, Types, And Functions
`struct spi_transport_attrs` stores period/offset/width/IU/DT/QAS/flow/streaming/RTI/precomp/hold-MCS negotiation state, device capability bits, driver flags, and domain-validation mutex/state. `enum spi_signal_type` and `struct spi_host_attrs` model host signaling. Accessor macros map target/host private data to attributes. `struct spi_function_template` contains get/set callbacks and sysfs visibility bits. APIs attach/release transport, schedule/run domain validation, display transfer agreements, print messages, and populate width/sync/PPR/tag messages.

## Control Flow
Transport attach reserves target/host attribute storage. Drivers set capabilities and callbacks. Sysfs get/set invokes template callbacks, while domain validation can be scheduled per device and serialized by `dv_mutex`. Message helpers construct protocol negotiation messages used by LLDDs.

## State And Persistence
SPI state is stored in `scsi_target::starget_data` and `Scsi_Host::shost_data`. Domain-validation pending/in-progress bits and mutex serialize runtime validation. No durable state is owned.

## Dependencies And Integration Points
It depends on Linux transport class and mutex, and forward-declares SCSI target/device/host/command types. It integrates with older parallel SCSI LLDDs, sysfs transport attributes, and negotiation message construction.

## Risks
Accessor macros assume the transport data layout is installed. Domain validation can race target removal if lifetimes are not held. Negotiation values must match protocol units expected by SDTR/PPR messages. Visibility bits must align with implemented callbacks.

## Test Signals
Attach/release transport, sysfs attribute get/set callbacks, DV scheduling and serialization, sync/wide/PPR/tag message bytes, signaling changes, deny-binding callback, and target private-data accessor alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_spi.h -->
