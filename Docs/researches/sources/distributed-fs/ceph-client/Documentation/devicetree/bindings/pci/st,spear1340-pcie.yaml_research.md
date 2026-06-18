<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,spear1340-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,spear1340-pcie.yaml

## Purpose
ST SPEAr1340 PCIe controller is a PCI/PCIe controller binding. SPEAr13XX uses the Synopsys DesignWare PCIe controller and ST MiPHY as PHY controller. Maintainers: Pratyush Anand <pratyush.anand@gmail.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/st,spear1340-pcie.yaml#`. compatible values `st,spear1340-pcie`, `snps,dw-pcie`. required properties `compatible`, `phys`, `phy-names`. notable properties `compatible`, `phys`, `st,pcie-is-gen1`. schema refs `snps,dw-pcie.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `phys`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `snps,dw-pcie.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,spear1340-pcie.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,spear1340-pcie.yaml -->
