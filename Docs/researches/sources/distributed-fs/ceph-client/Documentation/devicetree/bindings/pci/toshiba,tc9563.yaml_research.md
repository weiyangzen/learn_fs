<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/toshiba,tc9563.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/toshiba,tc9563.yaml

## Purpose
Toshiba TC9563 PCIe switch is a PCIe endpoint controller binding. Toshiba TC9563 PCIe switch has one upstream and three downstream ports. The 3rd downstream port has integrated endpoint device of Ethernet MAC. Other two downstream ports are supposed to connect to external device.  The TC9563 PCIe switch can be configured through I2C interface before PCIe link is established to change FTS, ASPM related entry delays, tx amplitude etc for better power efficiency and functionality. Maintainers: Krishna Chaitanya Chundru <krishna.chundru@oss.qualcomm.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/toshiba,tc9563.yaml#`. compatible values `pci1179,0623`. required properties `resx-gpios`, `vdd18-supply`, `vdd09-supply`, `vddc-supply`, `vddio1-supply`, `vddio2-supply`, `vddio18-supply`, `i2c-parent`. notable properties `compatible`, `reg`, `resx-gpios`, `vdd18-supply`, `vdd09-supply`, `vddc-supply`, `vddio1-supply`, `vddio2-supply`, and 2 more. schema refs `pci-bus-common.yaml#`, `pci-pci-bridge.yaml#`, `phandle-array`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-bus-common.yaml#`, `pci-pci-bridge.yaml#`, `phandle-array`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/toshiba,tc9563.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/toshiba,tc9563.yaml -->
