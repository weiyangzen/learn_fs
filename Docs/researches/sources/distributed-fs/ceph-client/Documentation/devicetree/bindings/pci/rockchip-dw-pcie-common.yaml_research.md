<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-common.yaml

## Purpose
DesignWare based PCIe RC/EP controller on Rockchip SoCs is a PCI/PCIe controller binding. Generic properties for the DesignWare based PCIe RC/EP controller on Rockchip SoCs. Maintainers: Shawn Lin <shawn.lin@rock-chips.com>, Simon Xue <xxm@rock-chips.com>, Heiko Stuebner <heiko@sntech.de>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rockchip-dw-pcie-common.yaml#`. required properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `num-lanes`, `phys`, `phy-names`, and 3 more. notable properties `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `phys`, and 2 more. clock names `aclk_mst`, `aclk_slv`, `aclk_dbi`, `pclk`, `aux`, `pipe`, `ref`. reset names `pipe`, `pwr`. interrupt names `sys`, `pmc`, `msg`, `legacy`, `err`, `msi`, `dma0`, `dma1`, and 2 more. PHY names `pcie-phy`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `clocks`, `resets`, `power-domains`, `phys`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is open for inherited/vendor properties.

## Risks
Primary risks are clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, interrupt map/name mistakes hide link, MSI, or error events, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-common.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-common.yaml -->
