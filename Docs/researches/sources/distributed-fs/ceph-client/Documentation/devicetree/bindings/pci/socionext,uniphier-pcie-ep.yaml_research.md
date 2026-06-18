<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/socionext,uniphier-pcie-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/socionext,uniphier-pcie-ep.yaml

## Purpose
Socionext UniPhier PCIe endpoint controller is a PCIe endpoint controller binding. UniPhier PCIe endpoint controller is based on the Synopsys DesignWare PCI core. It shares common features with the PCIe DesignWare core and inherits common properties defined in Documentation/devicetree/bindings/pci/snps,dw-pcie-ep.yaml. Maintainers: Kunihiko Hayashi <hayashi.kunihiko@socionext.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/socionext,uniphier-pcie-ep.yaml#`. compatible values `socionext,uniphier-pro5-pcie-ep`, `socionext,uniphier-nx1-pcie-ep`. required properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, and 4 more. register names `dbi`, `dbi2`, `link`, `addr_space`, `atu`. PHY names `pcie-phy`. schema refs `snps,dw-pcie-ep.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); 1 conditional branch(es); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `phys`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `snps,dw-pcie-ep.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/socionext,uniphier-pcie-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/socionext,uniphier-pcie-ep.yaml -->
