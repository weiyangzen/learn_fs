<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/pctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/pctrl.yaml

## Purpose
This binding documents HiSilicon peripheral miscellaneous control registers, represented as a small MMIO controller node.

## Important APIs, Types, And Functions
The valid schema API is `compatible = "hisilicon,pctrl"` plus one `reg` range. The included example shows `pctrl@fca09000`.

## Control Flow
Validation requires both `compatible` and `reg`, with `reg` limited to one item and no additional properties allowed.

## State And Persistence
The node has no independent runtime state. It describes persistent peripheral control registers that platform or pin/control drivers can map.

## Dependencies And Integration Points
It depends on the core DT schema and integrates with HiSilicon board DTS files and any driver matching `hisilicon,pctrl`.

## Risks
Wrong MMIO range or node placement can break peripheral setup. Because `additionalProperties` is false, future extensions must update the schema before DTS properties are added.

## Test Signals
Binding examples and affected DTS files should pass `dt_binding_check` and `dtbs_check`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/pctrl.yaml -->
