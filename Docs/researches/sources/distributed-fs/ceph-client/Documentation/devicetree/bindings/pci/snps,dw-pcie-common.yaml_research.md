<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie-common.yaml

## Purpose
Synopsys DWC PCIe RP/EP controller is a PCIe endpoint controller binding. Generic Synopsys DesignWare PCIe Root Port and Endpoint controller properties. Maintainers: Jingoo Han <jingoohan1@gmail.com>, Gustavo Pimentel <gustavo.pimentel@synopsys.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/snps,dw-pcie-common.yaml#`. required properties none declared. notable properties `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `reset-names`, and 10 more. clock names `dbi`, `mstr`, `slv`, `pipe`, `core`, `aux`, `ref`, `extref`, and 12 more. reset names `dbi`, `mstr`, `slv`, `app`, `non-sticky`, `sticky`, `pipe`, `core`, and 10 more. schema refs `flag`, `uint32`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 6 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `phys`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `flag`, `uint32`; property closure is open for inherited/vendor properties.

## Risks
Primary risks are clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie-common.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie-common.yaml -->
