<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/st,mlahb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/st,mlahb.yaml

## Purpose
This binding describes the STM32 master AHB bus interconnect node used on STM32MP1 platforms.

## Important APIs, Types, And Functions
It requires a node name matching `ahb@...`, compatible `st,mlahb`, `st,stm32mp1-mlahb`, `simple-bus`, one `reg` range, and standard bus `#address-cells`, `#size-cells`, and `ranges`.

## Control Flow
Validation enforces the bus-compatible chain and requires address translation properties needed for child devices on the bus.

## State And Persistence
The DT describes an interconnect bus window and address translation. Runtime state is standard platform bus enumeration of children.

## Dependencies And Integration Points
It integrates with simple-bus handling, STM32MP1 address maps, and child peripheral bindings.

## Risks
Missing `ranges` or incorrect address/size cells can make child devices unreachable. Compatible order must include `simple-bus` for generic enumeration.

## Test Signals
`dtbs_check` validates bus shape; child device creation and probing validate runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/st,mlahb.yaml -->
