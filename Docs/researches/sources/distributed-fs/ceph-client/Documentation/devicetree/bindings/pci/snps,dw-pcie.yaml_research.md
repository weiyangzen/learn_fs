<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie.yaml

## Purpose
Synopsys DesignWare PCIe interface is a PCI/PCIe controller binding. Synopsys DesignWare PCIe host controller Maintainers: Jingoo Han <jingoohan1@gmail.com>, Gustavo Pimentel <gustavo.pimentel@synopsys.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/snps,dw-pcie.yaml#`. required properties `compatible`, `reg`, `reg-names`. notable properties `reg`, `reg-names`, `interrupts`, `interrupt-names`. register names `dbi`, `dbi2`, `elbi`, `app`, `atu`, `dma`, `phy`, `config`, and 12 more. interrupt names `vpd`, `l_eq`, `sft_ce`, `sft_ue`, `app`, `msi`, `aer`, `pme`, and 9 more. schema refs `pci-host-bridge.yaml#`, `snps,dw-pcie-common.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 3 `allOf` layer(s); 1 conditional branch(es); 4 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`, `snps,dw-pcie-common.yaml#`; property closure is open for inherited/vendor properties.

## Risks
Primary risks are misordered register regions break MMIO window decoding, interrupt map/name mistakes hide link, MSI, or error events, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie.yaml -->
