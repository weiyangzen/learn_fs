<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie.yaml

## Purpose
DesignWare based PCIe Root Complex controller on Rockchip SoCs is a PCI/PCIe host bridge or root-complex binding. RK3568 SoC PCIe Root Complex controller is based on the Synopsys DesignWare PCIe IP and thus inherits all the common properties defined in snps,dw-pcie.yaml. Maintainers: Shawn Lin <shawn.lin@rock-chips.com>, Simon Xue <xxm@rock-chips.com>, Heiko Stuebner <heiko@sntech.de>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rockchip-dw-pcie.yaml#`. compatible values `rockchip,rk3568-pcie`, `rockchip,rk3528-pcie`, `rockchip,rk3562-pcie`, `rockchip,rk3576-pcie`, `rockchip,rk3588-pcie`. required properties none declared. notable properties `compatible`, `reg`, `reg-names`, `ranges`, `msi-map`, `legacy-interrupt-controller`, `vpcie3v3-supply`. register names `dbi`, `apb`, `config`. schema refs `rockchip-dw-pcie-common.yaml#`, `snps,dw-pcie.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 4 `allOf` layer(s); 2 conditional branch(es); 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `rockchip-dw-pcie-common.yaml#`, `snps,dw-pcie.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie.yaml -->
