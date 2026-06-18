<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hip04-bootwrapper.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hip04-bootwrapper.yaml

## Purpose
This binding describes the HiSilicon HiP04 bootwrapper SMP boot method. It records the physical bootwrapper and optional relocation areas used by platform code to release secondary CPUs.

## Important APIs, Types, And Functions
The schema exposes `compatible = "hisilicon,hip04-bootwrapper"` and `boot-method`, a uint32 array with two to four cells: bootwrapper physical address, bootwrapper size, relocation physical address, and relocation size.

## Control Flow
Validation requires both properties and constrains `boot-method` with `minItems: 2` and `maxItems: 4`. There are no child nodes or fallback compatibles.

## State And Persistence
The DT node persists boot protocol addresses. Runtime state is held by firmware/platform code that copies or jumps through the described regions.

## Dependencies And Integration Points
It depends on `/schemas/types.yaml` for uint32-array validation and integrates with HiP04 SMP bring-up code that interprets the boot method.

## Risks
Bad physical addresses or sizes can make secondary CPU startup fail very early. Because the property is a positional array, element order is a high-risk contract.

## Test Signals
`dt_binding_check` catches array length and type errors; boot testing on HiP04 systems is the real signal for address correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hip04-bootwrapper.yaml -->
