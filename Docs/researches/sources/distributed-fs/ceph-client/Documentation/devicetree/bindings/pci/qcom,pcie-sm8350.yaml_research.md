<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-sm8350.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-sm8350.yaml

## Purpose
Qualcomm SM8350 PCI Express Root Complex is a PCI/PCIe host bridge or root-complex binding. Qualcomm SM8350 SoC PCIe root complex controller is based on the Synopsys DesignWare PCIe IP. Maintainers: Bjorn Andersson <andersson@kernel.org>, Manivannan Sadhasivam <mani@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/qcom,pcie-sm8350.yaml#`. compatible values `qcom,pcie-sm8350`. required properties `power-domains`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, and 1 more. register names `parf`, `dbi`, `elbi`, `atu`, `config`, `mhi`. clock names `aux`, `cfg`, `bus_master`, `bus_slave`, `slave_q2a`, `tbu`, `ddrss_sf_tbu`, `aggre1`, and 1 more. reset names `pci`. interrupt names `msi0`, `msi1`, `msi2`, `msi3`, `msi4`, `msi5`, `msi6`, `msi7`, and 1 more. schema refs `qcom,pcie-common.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `qcom,pcie-common.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, interrupt map/name mistakes hide link, MSI, or error events. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-sm8350.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-sm8350.yaml -->
