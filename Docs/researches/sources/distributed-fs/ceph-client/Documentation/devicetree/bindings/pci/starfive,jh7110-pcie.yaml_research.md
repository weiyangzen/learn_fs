<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/starfive,jh7110-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/starfive,jh7110-pcie.yaml

## Purpose
StarFive JH7110 PCIe host controller is a PCI/PCIe controller binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Kevin Xie <kevin.xie@starfivetech.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/starfive,jh7110-pcie.yaml#`. compatible values `starfive,jh7110-pcie`. required properties `clocks`, `resets`, `starfive,stg-syscon`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, and 2 more. clock names `noc`, `tl`, `axi_mst0`, `apb`. reset names `mst0`, `slv0`, `slv`, `brg`, `core`, `apb`. schema refs `phandle-array`, `plda,xpressrich3-axi-common.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `phys`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `phandle-array`, `plda,xpressrich3-axi-common.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/starfive,jh7110-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/starfive,jh7110-pcie.yaml -->
