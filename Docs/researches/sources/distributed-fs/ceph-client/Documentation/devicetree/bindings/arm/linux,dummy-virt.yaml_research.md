<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/linux,dummy-virt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/linux,dummy-virt.yaml

## Purpose
This schema identifies the QEMU dummy virt machine root node.

## Important APIs, Types, And Functions
It fixes `$nodename` to `/` and requires the root `compatible` string `linux,dummy-virt`.

## Control Flow
Validation is a direct constant check. `additionalProperties: true` leaves normal virtual platform contents to other bindings.

## State And Persistence
The DT root compatible stores virtual machine identity. There is no hardware state beyond what QEMU exposes in other nodes.

## Dependencies And Integration Points
It integrates with QEMU-generated DTBs and Linux virtual platform detection.

## Risks
The schema is intentionally minimal; it will not catch malformed devices below the root. Incorrect compatible value can affect virtual machine matching.

## Test Signals
`dtbs_check` against QEMU virt DT output or checked-in DTS validates the root compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/linux,dummy-virt.yaml -->
