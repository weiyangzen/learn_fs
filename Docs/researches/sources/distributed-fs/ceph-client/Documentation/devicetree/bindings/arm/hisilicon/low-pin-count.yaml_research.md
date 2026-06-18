<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/low-pin-count.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/low-pin-count.yaml

## Purpose
This schema describes the HiSilicon HiP06/HiP07 Low Pin Count controller, which provides non-CPU-addressed LPC I/O access to legacy ISA devices.

## Important APIs, Types, And Functions
It requires an `isa@...` node name, `compatible` of `hisilicon,hip06-lpc` or `hisilicon,hip07-lpc`, one `reg` resource, and fixed `#address-cells = <2>` and `#size-cells = <1>` when child ISA devices are present.

## Control Flow
The schema validates the parent LPC node and permits child device objects through `additionalProperties: { type: object }`. It intentionally omits a `ranges` requirement because LPC I/O ports are not CPU addresses on arm64.

## State And Persistence
The node records a persistent LPC controller register block and child-device I/O port tuples. Runtime state is in LPC/ISA/IPMI drivers.

## Dependencies And Integration Points
It integrates with ISA/EISA child bindings such as `ipmi-bt` and with HiSilicon LPC controller code interpreting two-cell port addresses.

## Risks
Adding `ranges` or treating LPC ports as CPU addresses would be semantically wrong. Incorrect address/size cell counts can make child device `reg` encodings invalid.

## Test Signals
`dtbs_check` validates node naming, cell counts, and child-address shape. Runtime signals include successful discovery of LPC-attached IPMI or legacy devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/low-pin-count.yaml -->
