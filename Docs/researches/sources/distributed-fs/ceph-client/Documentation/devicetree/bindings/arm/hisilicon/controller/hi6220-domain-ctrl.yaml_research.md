<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hi6220-domain-ctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hi6220-domain-ctrl.yaml

## Purpose
This schema documents the HiSilicon Hi6220 always-on, media, and power-management domain controller register blocks. These nodes are `syscon` providers that expose clocks and, optionally, reset lines to other DT consumers.

## Important APIs, Types, And Functions
The binding surface is the `compatible` tuple, `reg`, `#clock-cells`, and optional `#reset-cells`. The first compatible selects `hisilicon,hi6220-aoctrl`, `hisilicon,hi6220-mediactrl`, or `hisilicon,hi6220-pmctrl`; the second must be `syscon`.

## Control Flow
Validation requires the compatible tuple, one register range, and clock provider cells. `additionalProperties: false` rejects undeclared properties, so consumers must use standard clock/reset/syscon links rather than ad hoc fields.

## State And Persistence
The schema has no runtime state. It describes persistent MMIO control registers used by kernel syscon, clock, and reset drivers after boot.

## Dependencies And Integration Points
It depends on the core devicetree meta-schema and integrates with Linux `syscon`, clock provider, and reset-controller lookups for Hi6220 platform drivers.

## Risks
The main risk is an incorrect compatible order or missing `syscon`, which prevents shared register access. Missing `#clock-cells` breaks clock phandle consumers; over-declaring reset cells on blocks without resets can mislead drivers.

## Test Signals
`make dt_binding_check` validates the examples and schema shape. `make dtbs_check` on Hi6220 DTS files confirms compatible ordering, register ranges, and clock/reset cell usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hi6220-domain-ctrl.yaml -->
