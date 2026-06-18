<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sifive,fu740-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sifive,fu740-pcie.yaml

## Purpose
SiFive FU740 PCIe host controller is a PCI/PCIe controller binding. SiFive FU740 PCIe host controller is based on the Synopsys DesignWare PCI core. It shares common features with the PCIe DesignWare core and inherits common properties defined in Documentation/devicetree/bindings/pci/snps,dw-pcie.yaml. Maintainers: Paul Walmsley <paul.walmsley@sifive.com>, Greentime Hu <greentime.hu@sifive.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/sifive,fu740-pcie.yaml#`. compatible values `sifive,fu740-pcie`. required properties `dma-coherent`, `num-lanes`, `interrupts`, `interrupt-names`, `interrupt-map-mask`, `interrupt-map`, `clocks`, `clock-names`, and 3 more. notable properties `compatible`, `reg`, `reg-names`, `interrupt-names`, `msi-parent`, `clocks`, `clock-names`, `resets`, and 4 more. register names `dbi`, `config`, `mgmt`. clock names `pcie_aux`. interrupt names `msi`, `inta`, `intb`, `intc`, `intd`. schema refs `snps,dw-pcie.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `snps,dw-pcie.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, interrupt map/name mistakes hide link, MSI, or error events. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sifive,fu740-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sifive,fu740-pcie.yaml -->
