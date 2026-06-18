<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/airoha,en7581-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/airoha,en7581-pcie-phy.yaml

## Purpose
Airoha EN7581 PCI-Express PHY is a physical-layer transceiver binding. The PCIe PHY supports physical layer functionality for PCIe Gen2/Gen3 port. Maintainers: Lorenzo Bianconi <lorenzo@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/airoha,en7581-pcie-phy.yaml#`. compatible values `airoha,en7581-pcie-phy`. required properties `compatible`, `reg`, `reg-names`, `#phy-cells`. notable properties `compatible`, `reg`, `reg-names`, `#phy-cells`. register names `csr-2l`, `pma0`, `pma1`, `p0-xr-dtime`, `p1-xr-dtime`, `rx-aeq`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/airoha,en7581-pcie-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/airoha,en7581-pcie-phy.yaml -->
