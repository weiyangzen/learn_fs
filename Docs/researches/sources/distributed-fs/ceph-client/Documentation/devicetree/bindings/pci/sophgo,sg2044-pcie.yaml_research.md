<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2044-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2044-pcie.yaml

## Purpose
DesignWare based PCIe Root Complex controller on Sophgo SoCs is a PCI/PCIe host bridge or root-complex binding. SG2044 SoC PCIe Root Complex controller is based on the Synopsys DesignWare PCIe IP and thus inherits all the common properties defined in snps,dw-pcie.yaml. Maintainers: Inochi Amaoto <inochiama@gmail.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/sophgo,sg2044-pcie.yaml#`. compatible values `sophgo,sg2044-pcie`. required properties `compatible`, `reg`, `clocks`. notable properties `compatible`, `reg`, `reg-names`, `ranges`, `msi-parent`, `clocks`, `clock-names`, `interrupt-controller`. register names `dbi`, `atu`, `config`, `app`. clock names `core`. schema refs `pci-host-bridge.yaml#`, `snps,dw-pcie.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`, `snps,dw-pcie.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2044-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2044-pcie.yaml -->
