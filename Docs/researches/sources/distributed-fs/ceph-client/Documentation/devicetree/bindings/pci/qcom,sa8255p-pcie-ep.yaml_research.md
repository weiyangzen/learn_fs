<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,sa8255p-pcie-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,sa8255p-pcie-ep.yaml

## Purpose
Qualcomm firmware managed PCIe Endpoint Controller is a PCIe endpoint controller binding. Qualcomm SA8255p SoC PCIe endpoint controller is based on the Synopsys DesignWare PCIe IP which is managed by firmware. Maintainers: Manivannan Sadhasivam <mani@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/qcom,sa8255p-pcie-ep.yaml#`. compatible values `qcom,sa8255p-pcie-ep`. required properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `reset-gpios`, `power-domains`. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `power-domains`, `num-lanes`, `iommus`, and 3 more. register names `parf`, `dbi`, `elbi`, `atu`, `addr_space`, `mmio`, `dma`. interrupt names `global`, `doorbell`, `dma`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `power-domains`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, interrupt map/name mistakes hide link, MSI, or error events. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,sa8255p-pcie-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,sa8255p-pcie-ep.yaml -->
