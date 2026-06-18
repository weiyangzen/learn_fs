<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/apple,atcphy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/apple,atcphy.yaml

## Purpose
Apple Type-C PHY (ATCPHY) is a physical-layer transceiver binding. The Apple Type-C PHY (ATCPHY) is a combined PHY for USB 2.0, USB 3.x, USB4/Thunderbolt, and DisplayPort connectivity via Type-C ports found in Apple Silicon SoCs. The PHY handles muxing between these different protocols and also provides the reset controller for the attached DWC3 USB controller. It is designed for USB4 operation and does not handle individual differential pairs as distinct DisplayPort lanes. Any reference to lane in this binding hence refers to two differential pairs (RX and TX) as used in USB terminology. In order to correctly setup these lanes for the various modes calibration values copied from Apple's firmware and converted to the format described below by our bootloader m1n1 are required. Without these only USB2 operation is possible. Maintainers: Sven Peter <sven@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/apple,atcphy.yaml#`. compatible values `apple,t6000-atcphy`, `apple,t6020-atcphy`, `apple,t8112-atcphy`, `apple,t8103-atcphy`. required properties `compatible`, `reg`, `reg-names`, `#phy-cells`, `#reset-cells`, `orientation-switch`, `mode-switch`, `power-domains`, and 1 more. notable properties `compatible`, `reg`, `reg-names`, `power-domains`, `#phy-cells`, `#reset-cells`, `mode-switch`, `orientation-switch`, and 10 more. register names `core`, `lpdptx`, `axi2af`, `usb2phy`, `pipehandler`. schema refs `port`, `ports`, `uint32-matrix`, `usb-switch.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `power-domains`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `port`, `ports`, `uint32-matrix`, `usb-switch.yaml#`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/apple,atcphy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/apple,atcphy.yaml -->
