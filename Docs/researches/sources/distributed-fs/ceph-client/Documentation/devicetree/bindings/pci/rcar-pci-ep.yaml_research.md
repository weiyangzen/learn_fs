<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-ep.yaml

## Purpose
Renesas R-Car PCIe Endpoint is a PCIe endpoint controller binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Lad Prabhakar <prabhakar.mahadev-lad.rj@bp.renesas.com>, Yoshihiro Shimoda <yoshihiro.shimoda.uh@renesas.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rcar-pci-ep.yaml#`. compatible values `renesas,r8a774a1-pcie-ep`, `renesas,r8a774b1-pcie-ep`, `renesas,r8a774c0-pcie-ep`, `renesas,r8a774e1-pcie-ep`, `renesas,r8a7795-pcie-ep`, `renesas,rcar-gen3-pcie-ep`. required properties `compatible`, `reg`, `reg-names`, `interrupts`, `resets`, `power-domains`, `clocks`, `clock-names`, and 1 more. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `resets`, `power-domains`, and 1 more. register names `apb-base`, `memory0`, `memory1`, `memory2`, `memory3`. clock names `pcie`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `power-domains`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-ep.yaml -->
