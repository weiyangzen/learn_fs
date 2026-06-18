<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,nwl-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,nwl-pcie.yaml

## Purpose
Xilinx NWL PCIe Root Port Bridge is a PCI/PCIe host bridge or root-complex binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Thippeswamy Havalige <thippeswamy.havalige@amd.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/xlnx,nwl-pcie.yaml#`. compatible values `xlnx,nwl-pcie-2.11`. required properties `compatible`, `reg`, `reg-names`, `interrupts`, `#interrupt-cells`, `interrupt-map`, `interrupt-map-mask`, `msi-controller`, and 1 more. notable properties `compatible`, `reg`, `reg-names`, `#interrupt-cells`, `interrupts`, `interrupt-names`, `interrupt-map`, `interrupt-map-mask`, and 7 more. register names `breg`, `pcireg`, `cfg`. interrupt names `misc`, `dummy`, `intx`, `msi1`, `msi0`. schema refs `msi-controller.yaml#`, `pci-host-bridge.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `power-domains`, `phys`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `msi-controller.yaml#`, `pci-host-bridge.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, interrupt map/name mistakes hide link, MSI, or error events. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,nwl-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,nwl-pcie.yaml -->
