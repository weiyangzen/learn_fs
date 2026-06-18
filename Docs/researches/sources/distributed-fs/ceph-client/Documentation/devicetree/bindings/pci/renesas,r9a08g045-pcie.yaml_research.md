<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/renesas,r9a08g045-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/renesas,r9a08g045-pcie.yaml

## Purpose
Renesas RZ/G3S PCIe host controller is a PCI/PCIe controller binding. Renesas RZ/G3{E,S} PCIe host controllers comply with PCIe Base Specification 4.0 and support up to 5 GT/s (Gen2) for RZ/G3S and up to 8 GT/s (Gen3) for RZ/G3E. Maintainers: Claudiu Beznea <claudiu.beznea.uj@bp.renesas.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/renesas,r9a08g045-pcie.yaml#`. compatible values `renesas,r9a08g045-pcie`, `renesas,r9a09g047-pcie`. required properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `interrupt-names`, and 8 more. notable properties `compatible`, `reg`, `dma-ranges`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, and 4 more. clock names `aclk`, `pm`, `pmu`. reset names `aresetn`, `rst_b`, `rst_gp_b`, `rst_ps_b`, `rst_rsm_b`, `rst_cfg_b`, `rst_load_b`. interrupt names `serr`, `serr_cor`, `serr_nonfatal`, `serr_fatal`, `axi_err`, `inta`, `intb`, `intc`, and 12 more. schema refs `pci-host-bridge.yaml#`, `pci-pci-bridge.yaml#`, `phandle`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 3 `allOf` layer(s); 2 conditional branch(es); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`, `power-domains`, `interrupts`, `dma-ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`, `pci-pci-bridge.yaml#`, `phandle`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, interrupt map/name mistakes hide link, MSI, or error events, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/renesas,r9a08g045-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/renesas,r9a08g045-pcie.yaml -->
