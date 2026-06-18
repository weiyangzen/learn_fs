<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hip04-fabric.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hip04-fabric.yaml

## Purpose
This schema describes the HiSilicon HiP04 fabric controller MMIO block, a platform control block involved in SoC fabric configuration.

## Important APIs, Types, And Functions
The binding surface is intentionally small: `compatible = "hisilicon,hip04-fabric"` and a single `reg` resource.

## Control Flow
The schema requires both properties and rejects extras with `additionalProperties: false`, so validation is a direct fixed-shape check.

## State And Persistence
The DT node describes persistent hardware registers. No schema-level state is created; runtime state belongs to platform controller code that maps the region.

## Dependencies And Integration Points
It depends only on the core schema and integrates with HiP04 platform initialization code using the compatible string and MMIO range.

## Risks
The risk surface is mostly address accuracy. An incorrect `reg` range can map the wrong fabric registers, and extra undocumented properties will fail schema validation.

## Test Signals
`dt_binding_check` validates the schema; `dtbs_check` for HiP04 board DTS files catches missing or malformed fabric controller nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hip04-fabric.yaml -->
