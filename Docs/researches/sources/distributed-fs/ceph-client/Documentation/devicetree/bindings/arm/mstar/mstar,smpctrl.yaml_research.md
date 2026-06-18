<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar,smpctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar,smpctrl.yaml

## Purpose
This schema documents MStar/SigmaStar SMP control registers used to set secondary CPU boot addresses and release magic values.

## Important APIs, Types, And Functions
It requires a compatible list of a SoC-specific value such as `sstar,ssd201-smpctrl` followed by `mstar,smpctrl`, plus a single `reg` range.

## Control Flow
Validation is a strict fixed-shape check and disallows additional properties.

## State And Persistence
The node describes persistent SMP control registers. Runtime state is written by platform CPU bring-up code.

## Dependencies And Integration Points
It integrates with MStar/SigmaStar SMP startup code and CPU nodes that depend on secondary bring-up.

## Risks
Incorrect registers can leave secondary CPUs parked in boot ROM loops. Compatible order must retain the generic fallback for shared handling.

## Test Signals
`dtbs_check` validates the schema; successful multi-core boot validates runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar,smpctrl.yaml -->
