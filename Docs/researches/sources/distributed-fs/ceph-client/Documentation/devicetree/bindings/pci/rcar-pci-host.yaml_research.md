<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-host.yaml

## Purpose
Renesas R-Car PCIe Host is a PCI/PCIe host bridge or root-complex binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Marek Vasut <marek.vasut+renesas@gmail.com>, Yoshihiro Shimoda <yoshihiro.shimoda.uh@renesas.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rcar-pci-host.yaml#`. compatible values `renesas,pcie-r8a7779`, `renesas,pcie-r8a7742`, `renesas,pcie-r8a7743`, `renesas,pcie-r8a7744`, `renesas,pcie-r8a7790`, `renesas,pcie-r8a7791`, `renesas,pcie-r8a7793`, `renesas,pcie-rcar-gen2`, and 11 more. required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`. notable properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `power-domains`, `phys`, and 6 more. clock names `pcie`, `pcie_bus`. PHY names `pcie`. schema refs `pci-host-bridge.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); 1 conditional branch(es); 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`, `power-domains`, `phys`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-host.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-host.yaml -->
