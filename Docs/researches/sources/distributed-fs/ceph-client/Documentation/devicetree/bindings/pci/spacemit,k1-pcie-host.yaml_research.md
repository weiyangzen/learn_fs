<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/spacemit,k1-pcie-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/spacemit,k1-pcie-host.yaml

## Purpose
SpacemiT K1 PCI Express Host Controller is a PCI/PCIe host bridge or root-complex binding. The SpacemiT K1 SoC PCIe host controller is based on the Synopsys DesignWare PCIe IP.  The controller uses the DesignWare built-in MSI interrupt controller, and supports 256 MSIs. Maintainers: Alex Elder <elder@riscstar.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/spacemit,k1-pcie-host.yaml#`. compatible values `spacemit,k1-pcie`. required properties `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `interrupt-names`, `spacemit,apmu`. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, and 2 more. register names `dbi`, `atu`, `config`, `link`. clock names `dbi`, `mstr`, `slv`. reset names `dbi`, `mstr`, `slv`. interrupt names `msi`. schema refs `pci-pci-bridge.yaml#`, `snps,dw-pcie.yaml#`, `phandle-array`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-pci-bridge.yaml#`, `snps,dw-pcie.yaml#`, `phandle-array`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, interrupt map/name mistakes hide link, MSI, or error events. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/spacemit,k1-pcie-host.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/spacemit,k1-pcie-host.yaml -->
