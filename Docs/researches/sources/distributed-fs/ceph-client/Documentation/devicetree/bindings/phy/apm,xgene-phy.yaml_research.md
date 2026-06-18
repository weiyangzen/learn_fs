<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/apm,xgene-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/apm,xgene-phy.yaml

## Purpose
APM X-Gene 15Gbps Multi-purpose PHY is a physical-layer transceiver binding. PHY nodes are defined to describe on-chip 15Gbps Multi-purpose PHY. Each PHY (pair of lanes) has its own node. Maintainers: Khuong Dinh <khuong@os.amperecomputing.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/apm,xgene-phy.yaml#`. compatible values `apm,xgene-phy`. required properties none declared. notable properties `compatible`, `reg`, `clocks`, `#phy-cells`, `apm,tx-eye-tuning`, `apm,tx-eye-direction`, `apm,tx-boost-gain`, `apm,tx-amplitude`, and 4 more. schema refs `uint32-array`, `uint32-matrix`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `uint32-array`, `uint32-matrix`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/apm,xgene-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/apm,xgene-phy.yaml -->
