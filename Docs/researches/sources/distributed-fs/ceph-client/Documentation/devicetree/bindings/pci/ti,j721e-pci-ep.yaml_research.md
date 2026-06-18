<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,j721e-pci-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,j721e-pci-ep.yaml

## Purpose
TI J721E PCI EP (PCIe Wrapper) is a PCIe endpoint controller binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Kishon Vijay Abraham I <kishon@ti.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/ti,j721e-pci-ep.yaml#`. compatible values `ti,j721e-pcie-ep`, `ti,j784s4-pcie-ep`, `ti,am64-pcie-ep`, `ti,j7200-pcie-ep`. required properties `compatible`, `reg`, `reg-names`, `ti,syscon-pcie-ctrl`, `max-link-speed`, `num-lanes`, `power-domains`, `clocks`, and 4 more. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`, and 2 more. register names `intd_cfg`, `user_cfg`, `reg`, `mem`. clock names `fck`. interrupt names `link_state`. schema refs `phandle-array`, `cdns-pcie-ep.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 4 `allOf` layer(s); 3 conditional branch(es); 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `power-domains`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `phandle-array`, `cdns-pcie-ep.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, interrupt map/name mistakes hide link, MSI, or error events, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,j721e-pci-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,j721e-pci-ep.yaml -->
