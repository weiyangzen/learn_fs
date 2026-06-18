<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xilinx-versal-cpm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xilinx-versal-cpm.yaml

## Purpose
CPM Host Controller device tree for Xilinx Versal SoCs is a PCI/PCIe controller binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Bharat Kumar Gogada <bharat.kumar.gogada@amd.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/xilinx-versal-cpm.yaml#`. compatible values `xlnx,versal-cpm-host-1.00`, `xlnx,versal-cpm5-host`, `xlnx,versal-cpm5-host1`, `xlnx,versal-cpm5nc-host`. required properties `reg`, `reg-names`, `#interrupt-cells`, `interrupts`, `interrupt-map`, `interrupt-map-mask`, `bus-range`, `msi-map`, and 1 more. notable properties `compatible`, `reg`, `reg-names`, `ranges`, `#interrupt-cells`, `interrupts`, `msi-map`, `interrupt-controller`. register names `cpm_slcr`, `cfg`, `cpm_csr`. schema refs `pci-host-bridge.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `interrupts`, `ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xilinx-versal-cpm.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xilinx-versal-cpm.yaml -->
