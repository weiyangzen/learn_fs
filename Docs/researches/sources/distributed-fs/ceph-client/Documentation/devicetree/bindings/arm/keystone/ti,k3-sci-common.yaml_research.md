<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/keystone/ti,k3-sci-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/keystone/ti,k3-sci-common.yaml

## Purpose
This shared schema fragment defines common properties for TI K3 device-management nodes that communicate with the System Controller Processor through TI-SCI.

## Important APIs, Types, And Functions
The common properties are `ti,sci` phandle, `ti,sci-dev-id` uint32, and `ti,sci-proc-ids` tuple containing processor ID and host ID for remote processor ownership transfer.

## Control Flow
It is intended for inclusion by more specific clock, reset, interrupt, and processor-management bindings. `additionalProperties: true` lets those bindings define their own required and specialized fields.

## State And Persistence
The properties persist firmware protocol addressing and ownership metadata in DT. Runtime state is managed by the TI-SCI firmware and Linux TI-SCI clients.

## Dependencies And Integration Points
It depends on `/schemas/types.yaml` and integrates with the parent TI-SCI controller node described by `ti,sci.yaml`, plus TI clock/reset/power/remoteproc bindings.

## Risks
Wrong device IDs or processor/host tuples can make firmware calls target the wrong resource. Because this is common glue, changes can affect multiple K3 subsystems.

## Test Signals
Consumers should pass `dtbs_check` through their concrete bindings. Runtime signals include successful TI-SCI clock, reset, interrupt, or remote processor operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/keystone/ti,k3-sci-common.yaml -->
