# Research Group subset-b-000598

This grouped report covers devicetree binding schemas for PCI/PCIe controllers, PECI controllers, performance monitor units, and PHY blocks from the ceph-client source mirror. Each file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-sm8450.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-sm8450.yaml

## Purpose
Qualcomm SM8450 PCI Express Root Complex is a PCI/PCIe host bridge or root-complex binding. Qualcomm SM8450 SoC PCIe root complex controller is based on the Synopsys DesignWare PCIe IP. Maintainers: Bjorn Andersson <andersson@kernel.org>, Manivannan Sadhasivam <mani@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/qcom,pcie-sm8450.yaml#`. compatible values `qcom,pcie-sm8450-pcie0`, `qcom,pcie-sm8450-pcie1`. required properties `power-domains`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, and 1 more. register names `parf`, `dbi`, `elbi`, `atu`, `config`, `mhi`. clock names `pipe`, `pipe_mux`, `phy_pipe`, `ref`, `aux`, `cfg`, `bus_master`, `bus_slave`, and 4 more. reset names `pci`. interrupt names `msi0`, `msi1`, `msi2`, `msi3`, `msi4`, `msi5`, `msi6`, `msi7`, and 1 more. schema refs `qcom,pcie-common.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `qcom,pcie-common.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, interrupt map/name mistakes hide link, MSI, or error events. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-sm8450.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-sm8450.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-sm8550.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-sm8550.yaml

## Purpose
Qualcomm SM8550 PCI Express Root Complex is a PCI/PCIe host bridge or root-complex binding. Qualcomm SM8550 SoC (and compatible) PCIe root complex controller is based on the Synopsys DesignWare PCIe IP. Maintainers: Bjorn Andersson <andersson@kernel.org>, Manivannan Sadhasivam <mani@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/qcom,pcie-sm8550.yaml#`. compatible values `qcom,pcie-sm8550`, `qcom,kaanapali-pcie`, `qcom,sar2130p-pcie`, `qcom,pcie-sm8650`, `qcom,pcie-sm8750`. required properties `power-domains`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, and 1 more. register names `parf`, `dbi`, `elbi`, `atu`, `config`, `mhi`. clock names `aux`, `cfg`, `bus_master`, `bus_slave`, `slave_q2a`, `ddrss_sf_tbu`, `noc_aggr`, `cnoc_sf_axi`, and 1 more. reset names `pci`, `link_down`. interrupt names `msi0`, `msi1`, `msi2`, `msi3`, `msi4`, `msi5`, `msi6`, `msi7`, and 1 more. schema refs `qcom,pcie-common.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `qcom,pcie-common.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, interrupt map/name mistakes hide link, MSI, or error events, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-sm8550.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-sm8550.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-x1e80100.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-x1e80100.yaml

## Purpose
Qualcomm X1E80100 PCI Express Root Complex is a PCI/PCIe host bridge or root-complex binding. Qualcomm X1E80100 SoC (and compatible) PCIe root complex controller is based on the Synopsys DesignWare PCIe IP. Maintainers: Bjorn Andersson <andersson@kernel.org>, Manivannan Sadhasivam <mani@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/qcom,pcie-x1e80100.yaml#`. compatible values `qcom,pcie-x1e80100`, `qcom,glymur-pcie`. required properties `power-domains`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, and 1 more. register names `parf`, `dbi`, `elbi`, `atu`, `config`, `mhi`. clock names `aux`, `cfg`, `bus_master`, `bus_slave`, `slave_q2a`, `noc_aggr`, `cnoc_sf_axi`. reset names `pci`, `link_down`. interrupt names `msi0`, `msi1`, `msi2`, `msi3`, `msi4`, `msi5`, `msi6`, `msi7`, and 1 more. schema refs `qcom,pcie-common.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `qcom,pcie-common.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, interrupt map/name mistakes hide link, MSI, or error events, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-x1e80100.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/qcom,pcie-x1e80100.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-gen4-pci-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-gen4-pci-ep.yaml

## Purpose
Renesas R-Car Gen4 PCIe Endpoint is a PCIe endpoint controller binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Yoshihiro Shimoda <yoshihiro.shimoda.uh@renesas.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rcar-gen4-pci-ep.yaml#`. compatible values `renesas,r8a779f0-pcie-ep`, `renesas,r8a779g0-pcie-ep`, `renesas,r8a779h0-pcie-ep`, `renesas,rcar-gen4-pcie-ep`. required properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`, and 2 more. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, and 5 more. register names `dbi`, `dbi2`, `atu`, `dma`, `app`, `phy`, `addr_space`. clock names `core`, `ref`. reset names `pwr`. interrupt names `dma`, `sft_ce`, `app`. schema refs `snps,dw-pcie-ep.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `power-domains`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `snps,dw-pcie-ep.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, interrupt map/name mistakes hide link, MSI, or error events. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-gen4-pci-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-gen4-pci-ep.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-gen4-pci-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-gen4-pci-host.yaml

## Purpose
Renesas R-Car Gen4 PCIe Host is a PCI/PCIe host bridge or root-complex binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Yoshihiro Shimoda <yoshihiro.shimoda.uh@renesas.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rcar-gen4-pci-host.yaml#`. compatible values `renesas,r8a779f0-pcie`, `renesas,r8a779g0-pcie`, `renesas,r8a779h0-pcie`, `renesas,rcar-gen4-pcie`. required properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`, and 2 more. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, and 4 more. register names `dbi`, `dbi2`, `atu`, `dma`, `app`, `phy`, `config`. clock names `core`, `ref`. reset names `pwr`. interrupt names `msi`, `dma`, `sft_ce`, `app`. schema refs `snps,dw-pcie.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `power-domains`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `snps,dw-pcie.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, interrupt map/name mistakes hide link, MSI, or error events. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-gen4-pci-host.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-gen4-pci-host.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-ep.yaml

## Purpose
Renesas R-Car PCIe Endpoint is a PCIe endpoint controller binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Lad Prabhakar <prabhakar.mahadev-lad.rj@bp.renesas.com>, Yoshihiro Shimoda <yoshihiro.shimoda.uh@renesas.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rcar-pci-ep.yaml#`. compatible values `renesas,r8a774a1-pcie-ep`, `renesas,r8a774b1-pcie-ep`, `renesas,r8a774c0-pcie-ep`, `renesas,r8a774e1-pcie-ep`, `renesas,r8a7795-pcie-ep`, `renesas,rcar-gen3-pcie-ep`. required properties `compatible`, `reg`, `reg-names`, `interrupts`, `resets`, `power-domains`, `clocks`, `clock-names`, and 1 more. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `resets`, `power-domains`, and 1 more. register names `apb-base`, `memory0`, `memory1`, `memory2`, `memory3`. clock names `pcie`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `power-domains`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-ep.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-host.yaml

## Purpose
Renesas R-Car PCIe Host is a PCI/PCIe host bridge or root-complex binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Marek Vasut <marek.vasut+renesas@gmail.com>, Yoshihiro Shimoda <yoshihiro.shimoda.uh@renesas.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rcar-pci-host.yaml#`. compatible values `renesas,pcie-r8a7779`, `renesas,pcie-r8a7742`, `renesas,pcie-r8a7743`, `renesas,pcie-r8a7744`, `renesas,pcie-r8a7790`, `renesas,pcie-r8a7791`, `renesas,pcie-r8a7793`, `renesas,pcie-rcar-gen2`, and 11 more. required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`. notable properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `power-domains`, `phys`, and 6 more. clock names `pcie`, `pcie_bus`. PHY names `pcie`. schema refs `pci-host-bridge.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); 1 conditional branch(es); 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`, `power-domains`, `phys`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-host.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rcar-pci-host.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/renesas,pci-rcar-gen2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/renesas,pci-rcar-gen2.yaml

## Purpose
Renesas AHB to PCI bridge is a PCI/PCIe controller binding. This is the bridge used internally to connect the USB controllers to the AHB. There is one bridge instance per USB port connected to the internal OHCI and EHCI controllers. Maintainers: Marek Vasut <marek.vasut+renesas@gmail.com>, Yoshihiro Shimoda <yoshihiro.shimoda.uh@renesas.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/renesas,pci-rcar-gen2.yaml#`. compatible values `renesas,pci-r8a7742`, `renesas,pci-r8a7743`, `renesas,pci-r8a7744`, `renesas,pci-r8a7745`, `renesas,pci-r8a7790`, `renesas,pci-r8a7791`, `renesas,pci-r8a7793`, `renesas,pci-r8a7794`, and 3 more. required properties `compatible`, `reg`, `interrupts`, `interrupt-map`, `interrupt-map-mask`, `clocks`, `power-domains`, `bus-range`, and 3 more. notable properties `compatible`, `reg`, `dma-ranges`, `bus-range`, `interrupts`, `clocks`, `clock-names`, `resets`, and 1 more. schema refs `pci-host-bridge.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); 1 conditional branch(es); 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`, `power-domains`, `interrupts`, `dma-ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/renesas,pci-rcar-gen2.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/renesas,pci-rcar-gen2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/renesas,r9a08g045-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/renesas,r9a08g045-pcie.yaml

## Purpose
Renesas RZ/G3S PCIe host controller is a PCI/PCIe controller binding. Renesas RZ/G3{E,S} PCIe host controllers comply with PCIe Base Specification 4.0 and support up to 5 GT/s (Gen2) for RZ/G3S and up to 8 GT/s (Gen3) for RZ/G3E. Maintainers: Claudiu Beznea <claudiu.beznea.uj@bp.renesas.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/renesas,r9a08g045-pcie.yaml#`. compatible values `renesas,r9a08g045-pcie`, `renesas,r9a09g047-pcie`. required properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `interrupt-names`, and 8 more. notable properties `compatible`, `reg`, `dma-ranges`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, and 4 more. clock names `aclk`, `pm`, `pmu`. reset names `aresetn`, `rst_b`, `rst_gp_b`, `rst_ps_b`, `rst_rsm_b`, `rst_cfg_b`, `rst_load_b`. interrupt names `serr`, `serr_cor`, `serr_nonfatal`, `serr_fatal`, `axi_err`, `inta`, `intb`, `intc`, and 12 more. schema refs `pci-host-bridge.yaml#`, `pci-pci-bridge.yaml#`, `phandle`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 3 `allOf` layer(s); 2 conditional branch(es); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`, `power-domains`, `interrupts`, `dma-ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`, `pci-pci-bridge.yaml#`, `phandle`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, interrupt map/name mistakes hide link, MSI, or error events, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/renesas,r9a08g045-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/renesas,r9a08g045-pcie.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip,rk3399-pcie-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip,rk3399-pcie-common.yaml

## Purpose
Rockchip AXI PCIe Bridge Common Properties is a PCI/PCIe controller binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Shawn Lin <shawn.lin@rock-chips.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rockchip,rk3399-pcie-common.yaml#`. required properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `phys`, `phy-names`, `resets`, and 1 more. notable properties `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, `phy-names`, `num-lanes`. clock names `aclk`, `aclk-perf`, `hclk`, `pm`. reset names `core`, `mgmt`, `mgmt-sticky`, `pipe`, `pm`, `pclk`, `aclk`. PHY names `pcie-phy`, `pcie-phy-0`, `pcie-phy-1`, `pcie-phy-2`, `pcie-phy-3`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 2 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`, `phys`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is open for inherited/vendor properties.

## Risks
Primary risks are clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip,rk3399-pcie-common.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip,rk3399-pcie-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip,rk3399-pcie-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip,rk3399-pcie-ep.yaml

## Purpose
Rockchip AXI PCIe Endpoint is a PCIe endpoint controller binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Shawn Lin <shawn.lin@rock-chips.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rockchip,rk3399-pcie-ep.yaml#`. compatible values `rockchip,rk3399-pcie-ep`. required properties `rockchip,max-outbound-regions`. notable properties `compatible`, `reg`, `reg-names`, `rockchip,max-outbound-regions`. register names `apb-base`, `mem-base`. schema refs `pci-ep.yaml#`, `uint32`, `rockchip,rk3399-pcie-common.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-ep.yaml#`, `uint32`, `rockchip,rk3399-pcie-common.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip,rk3399-pcie-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip,rk3399-pcie-ep.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip,rk3399-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip,rk3399-pcie.yaml

## Purpose
Rockchip AXI PCIe Root Port Bridge Host is a PCI/PCIe host bridge or root-complex binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Shawn Lin <shawn.lin@rock-chips.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rockchip,rk3399-pcie.yaml#`. compatible values `rockchip,rk3399-pcie`. required properties `ranges`, `#interrupt-cells`, `interrupts`, `interrupt-controller`, `interrupt-map`, `interrupt-map-mask`, `msi-map`. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `aspm-no-l0s`, `ep-gpios`, `vpcie12v-supply`, and 4 more. register names `axi-base`, `apb-base`. interrupt names `sys`, `legacy`, `client`. schema refs `pci-host-bridge.yaml#`, `rockchip,rk3399-pcie-common.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`, `rockchip,rk3399-pcie-common.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, interrupt map/name mistakes hide link, MSI, or error events. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip,rk3399-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip,rk3399-pcie.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-common.yaml

## Purpose
DesignWare based PCIe RC/EP controller on Rockchip SoCs is a PCI/PCIe controller binding. Generic properties for the DesignWare based PCIe RC/EP controller on Rockchip SoCs. Maintainers: Shawn Lin <shawn.lin@rock-chips.com>, Simon Xue <xxm@rock-chips.com>, Heiko Stuebner <heiko@sntech.de>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rockchip-dw-pcie-common.yaml#`. required properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `num-lanes`, `phys`, `phy-names`, and 3 more. notable properties `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `phys`, and 2 more. clock names `aclk_mst`, `aclk_slv`, `aclk_dbi`, `pclk`, `aux`, `pipe`, `ref`. reset names `pipe`, `pwr`. interrupt names `sys`, `pmc`, `msg`, `legacy`, `err`, `msi`, `dma0`, `dma1`, and 2 more. PHY names `pcie-phy`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `clocks`, `resets`, `power-domains`, `phys`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is open for inherited/vendor properties.

## Risks
Primary risks are clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, interrupt map/name mistakes hide link, MSI, or error events, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-common.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-ep.yaml

## Purpose
DesignWare based PCIe Endpoint controller on Rockchip SoCs is a PCIe endpoint controller binding. RK3588 SoC PCIe Endpoint controller is based on the Synopsys DesignWare PCIe IP and thus inherits all the common properties defined in snps,dw-pcie-ep.yaml. Maintainers: Niklas Cassel <cassel@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/rockchip-dw-pcie-ep.yaml#`. compatible values `rockchip,rk3568-pcie-ep`, `rockchip,rk3588-pcie-ep`. required properties `interrupts`, `interrupt-names`. notable properties `compatible`, `reg`, `reg-names`. register names `dbi`, `dbi2`, `apb`, `addr_space`, `atu`. schema refs `rockchip-dw-pcie-common.yaml#`, `snps,dw-pcie-ep.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `rockchip-dw-pcie-common.yaml#`, `snps,dw-pcie-ep.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/rockchip-dw-pcie-ep.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/samsung,exynos-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/samsung,exynos-pcie.yaml

## Purpose
Samsung SoC series PCIe Host Controller is a PCI/PCIe controller binding. Exynos5433 SoC PCIe host controller is based on the Synopsys DesignWare PCIe IP and thus inherits all the common properties defined in snps,dw-pcie.yaml. Maintainers: Marek Szyprowski <m.szyprowski@samsung.com>, Jaehoon Chung <jh80.chung@samsung.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/samsung,exynos-pcie.yaml#`. compatible values `samsung,exynos5433-pcie`. required properties `reg`, `reg-names`, `interrupts`, `#address-cells`, `#size-cells`, `#interrupt-cells`, `interrupt-map`, `interrupt-map-mask`, and 10 more. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `phys`, `num-lanes`, and 3 more. register names `dbi`, `elbi`, `config`. clock names `pcie`, `pcie_bus`. schema refs `snps,dw-pcie.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `phys`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `snps,dw-pcie.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/samsung,exynos-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/samsung,exynos-pcie.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sifive,fu740-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sifive,fu740-pcie.yaml

## Purpose
SiFive FU740 PCIe host controller is a PCI/PCIe controller binding. SiFive FU740 PCIe host controller is based on the Synopsys DesignWare PCI core. It shares common features with the PCIe DesignWare core and inherits common properties defined in Documentation/devicetree/bindings/pci/snps,dw-pcie.yaml. Maintainers: Paul Walmsley <paul.walmsley@sifive.com>, Greentime Hu <greentime.hu@sifive.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/sifive,fu740-pcie.yaml#`. compatible values `sifive,fu740-pcie`. required properties `dma-coherent`, `num-lanes`, `interrupts`, `interrupt-names`, `interrupt-map-mask`, `interrupt-map`, `clocks`, `clock-names`, and 3 more. notable properties `compatible`, `reg`, `reg-names`, `interrupt-names`, `msi-parent`, `clocks`, `clock-names`, `resets`, and 4 more. register names `dbi`, `config`, `mgmt`. clock names `pcie_aux`. interrupt names `msi`, `inta`, `intb`, `intc`, `intd`. schema refs `snps,dw-pcie.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `snps,dw-pcie.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, interrupt map/name mistakes hide link, MSI, or error events. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sifive,fu740-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sifive,fu740-pcie.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie-ep.yaml

## Purpose
Synopsys DesignWare PCIe endpoint interface is a PCIe endpoint controller binding. Synopsys DesignWare PCIe host controller endpoint Maintainers: Jingoo Han <jingoohan1@gmail.com>, Gustavo Pimentel <gustavo.pimentel@synopsys.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/snps,dw-pcie-ep.yaml#`. required properties `compatible`, `reg`, `reg-names`. notable properties `reg`, `reg-names`, `interrupts`, `interrupt-names`, `max-functions`. register names `dbi`, `dbi2`, `elbi`, `app`, `atu`, `dma`, `phy`, `addr_space`, and 4 more. interrupt names `vpd`, `l_eq`, `sft_ce`, `sft_ue`, `app`, `legacy`, `intr`, `sys`, and 3 more. schema refs `pci-ep.yaml#`, `snps,dw-pcie-common.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); 4 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-ep.yaml#`, `snps,dw-pcie-common.yaml#`; property closure is open for inherited/vendor properties.

## Risks
Primary risks are misordered register regions break MMIO window decoding, interrupt map/name mistakes hide link, MSI, or error events, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie-ep.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie.yaml

## Purpose
Synopsys DesignWare PCIe interface is a PCI/PCIe controller binding. Synopsys DesignWare PCIe host controller Maintainers: Jingoo Han <jingoohan1@gmail.com>, Gustavo Pimentel <gustavo.pimentel@synopsys.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/snps,dw-pcie.yaml#`. required properties `compatible`, `reg`, `reg-names`. notable properties `reg`, `reg-names`, `interrupts`, `interrupt-names`. register names `dbi`, `dbi2`, `elbi`, `app`, `atu`, `dma`, `phy`, `config`, and 12 more. interrupt names `vpd`, `l_eq`, `sft_ce`, `sft_ue`, `app`, `msi`, `aer`, `pme`, and 9 more. schema refs `pci-host-bridge.yaml#`, `snps,dw-pcie-common.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 3 `allOf` layer(s); 1 conditional branch(es); 4 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`, `snps,dw-pcie-common.yaml#`; property closure is open for inherited/vendor properties.

## Risks
Primary risks are misordered register regions break MMIO window decoding, interrupt map/name mistakes hide link, MSI, or error events, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/snps,dw-pcie.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/socionext,uniphier-pcie-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/socionext,uniphier-pcie-ep.yaml

## Purpose
Socionext UniPhier PCIe endpoint controller is a PCIe endpoint controller binding. UniPhier PCIe endpoint controller is based on the Synopsys DesignWare PCI core. It shares common features with the PCIe DesignWare core and inherits common properties defined in Documentation/devicetree/bindings/pci/snps,dw-pcie-ep.yaml. Maintainers: Kunihiko Hayashi <hayashi.kunihiko@socionext.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/socionext,uniphier-pcie-ep.yaml#`. compatible values `socionext,uniphier-pro5-pcie-ep`, `socionext,uniphier-nx1-pcie-ep`. required properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, and 4 more. register names `dbi`, `dbi2`, `link`, `addr_space`, `atu`. PHY names `pcie-phy`. schema refs `snps,dw-pcie-ep.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); 1 conditional branch(es); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `phys`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `snps,dw-pcie-ep.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/socionext,uniphier-pcie-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/socionext,uniphier-pcie-ep.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/socionext,uniphier-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/socionext,uniphier-pcie.yaml

## Purpose
Socionext UniPhier PCIe host controller is a PCI/PCIe controller binding. UniPhier PCIe host controller is based on the Synopsys DesignWare PCI core. It shares common features with the PCIe DesignWare core and inherits common properties defined in Documentation/devicetree/bindings/pci/snps,dw-pcie.yaml. Maintainers: Kunihiko Hayashi <hayashi.kunihiko@socionext.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/socionext,uniphier-pcie.yaml#`. compatible values `socionext,uniphier-pcie`. required properties `compatible`, `reg`, `reg-names`, `clocks`, `resets`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `resets`, `phys`, `phy-names`, `num-lanes`, and 2 more. register names `dbi`, `link`, `config`, `atu`. PHY names `pcie-phy`. schema refs `snps,dw-pcie.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`, `phys`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `snps,dw-pcie.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/socionext,uniphier-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/socionext,uniphier-pcie.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2042-pcie-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2042-pcie-host.yaml

## Purpose
Sophgo SG2042 PCIe Host (Cadence PCIe Wrapper) is a PCI/PCIe host bridge or root-complex binding. Sophgo SG2042 PCIe host controller is based on the Cadence PCIe core. Maintainers: Chen Wang <unicorn_wang@outlook.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/sophgo,sg2042-pcie-host.yaml#`. compatible values `sophgo,sg2042-pcie-host`. required properties `compatible`, `reg`, `reg-names`. notable properties `compatible`, `reg`, `reg-names`, `msi-parent`, `vendor-id`, `device-id`. register names `reg`, `cfg`. schema refs `cdns-pcie-host.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `cdns-pcie-host.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2042-pcie-host.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2042-pcie-host.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2044-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2044-pcie.yaml

## Purpose
DesignWare based PCIe Root Complex controller on Sophgo SoCs is a PCI/PCIe host bridge or root-complex binding. SG2044 SoC PCIe Root Complex controller is based on the Synopsys DesignWare PCIe IP and thus inherits all the common properties defined in snps,dw-pcie.yaml. Maintainers: Inochi Amaoto <inochiama@gmail.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/sophgo,sg2044-pcie.yaml#`. compatible values `sophgo,sg2044-pcie`. required properties `compatible`, `reg`, `clocks`. notable properties `compatible`, `reg`, `reg-names`, `ranges`, `msi-parent`, `clocks`, `clock-names`, `interrupt-controller`. register names `dbi`, `atu`, `config`, `app`. clock names `core`. schema refs `pci-host-bridge.yaml#`, `snps,dw-pcie.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`, `snps,dw-pcie.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2044-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2044-pcie.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,spear1340-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,spear1340-pcie.yaml

## Purpose
ST SPEAr1340 PCIe controller is a PCI/PCIe controller binding. SPEAr13XX uses the Synopsys DesignWare PCIe controller and ST MiPHY as PHY controller. Maintainers: Pratyush Anand <pratyush.anand@gmail.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/st,spear1340-pcie.yaml#`. compatible values `st,spear1340-pcie`, `snps,dw-pcie`. required properties `compatible`, `phys`, `phy-names`. notable properties `compatible`, `phys`, `st,pcie-is-gen1`. schema refs `snps,dw-pcie.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `phys`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `snps,dw-pcie.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,spear1340-pcie.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,spear1340-pcie.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,stm32-pcie-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,stm32-pcie-common.yaml

## Purpose
STM32MP25 PCIe RC/EP controller is a PCI/PCIe controller binding. STM32MP25 PCIe RC/EP common properties Maintainers: Christian Bruel <christian.bruel@foss.st.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/st,stm32-pcie-common.yaml#`. required properties `clocks`, `resets`. notable properties `clocks`, `resets`, `power-domains`, `access-controllers`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `clocks`, `resets`, `power-domains`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is open for inherited/vendor properties.

## Risks
Primary risks are schema/property drift can allow invalid DTS nodes or reject existing boards. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,stm32-pcie-common.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,stm32-pcie-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,stm32-pcie-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,stm32-pcie-ep.yaml

## Purpose
STMicroelectronics STM32MP25 PCIe Endpoint is a PCIe endpoint controller binding. PCIe endpoint controller based on the Synopsys DesignWare PCIe core. Maintainers: Christian Bruel <christian.bruel@foss.st.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/st,stm32-pcie-ep.yaml#`. compatible values `st,stm32mp25-pcie-ep`. required properties `phys`, `reset-gpios`. notable properties `compatible`, `reg`, `reg-names`, `phys`, `reset-gpios`. register names `dbi`, `dbi2`, `atu`, `addr_space`. schema refs `snps,dw-pcie-ep.yaml#`, `st,stm32-pcie-common.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `phys`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `snps,dw-pcie-ep.yaml#`, `st,stm32-pcie-common.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,stm32-pcie-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,stm32-pcie-ep.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,stm32-pcie-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,stm32-pcie-host.yaml

## Purpose
STMicroelectronics STM32MP25 PCIe Root Complex is a PCI/PCIe host bridge or root-complex binding. PCIe root complex controller based on the Synopsys DesignWare PCIe core. Maintainers: Christian Bruel <christian.bruel@foss.st.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/st,stm32-pcie-host.yaml#`. compatible values `st,stm32mp25-pcie-rc`. required properties `interrupt-map`, `interrupt-map-mask`, `ranges`, `dma-ranges`. notable properties `compatible`, `reg`, `reg-names`, `msi-parent`. register names `dbi`, `config`. schema refs `pci-pci-bridge.yaml#`, `snps,dw-pcie.yaml#`, `st,stm32-pcie-common.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-pci-bridge.yaml#`, `snps,dw-pcie.yaml#`, `st,stm32-pcie-common.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,stm32-pcie-host.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/st,stm32-pcie-host.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,am65-pci-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,am65-pci-ep.yaml

## Purpose
TI AM65 PCI Endpoint is a PCIe endpoint controller binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Kishon Vijay Abraham I <kishon@ti.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/ti,am65-pci-ep.yaml#`. compatible values `ti,am654-pcie-ep`. required properties `compatible`, `reg`, `reg-names`, `max-link-speed`, `power-domains`, `ti,syscon-pcie-mode`, `dma-coherent`. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `power-domains`, `ti,syscon-pcie-mode`, `dma-coherent`. register names `app`, `dbics`, `addr_space`, `atu`. schema refs `phandle-array`, `pci-ep.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `power-domains`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `phandle-array`, `pci-ep.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,am65-pci-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,am65-pci-ep.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,am65-pci-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,am65-pci-host.yaml

## Purpose
TI AM65 PCI Host is a PCI/PCIe host bridge or root-complex binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Kishon Vijay Abraham I <kishon@ti.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/ti,am65-pci-host.yaml#`. compatible values `ti,am654-pcie-rc`, `ti,keystone-pcie`. required properties `compatible`, `reg`, `reg-names`, `max-link-speed`, `ti,syscon-pcie-id`, `ti,syscon-pcie-mode`, `ranges`. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `msi-map`, `power-domains`, `phys`, `phy-names`, and 5 more. register names `app`, `dbics`, `config`, `atu`, `vmap_lp`, `vmap_hp`. schema refs `pci-host-bridge.yaml#`, `phandle-array`, `uint32`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); 1 conditional branch(es); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `power-domains`, `phys`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`, `phandle-array`, `uint32`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,am65-pci-host.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,am65-pci-host.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,j721e-pci-ep.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,j721e-pci-ep.yaml

## Purpose
TI J721E PCI EP (PCIe Wrapper) is a PCIe endpoint controller binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Kishon Vijay Abraham I <kishon@ti.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/ti,j721e-pci-ep.yaml#`. compatible values `ti,j721e-pcie-ep`, `ti,j784s4-pcie-ep`, `ti,am64-pcie-ep`, `ti,j7200-pcie-ep`. required properties `compatible`, `reg`, `reg-names`, `ti,syscon-pcie-ctrl`, `max-link-speed`, `num-lanes`, `power-domains`, `clocks`, and 4 more. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`, and 2 more. register names `intd_cfg`, `user_cfg`, `reg`, `mem`. clock names `fck`. interrupt names `link_state`. schema refs `phandle-array`, `cdns-pcie-ep.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 4 `allOf` layer(s); 3 conditional branch(es); 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `power-domains`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `phandle-array`, `cdns-pcie-ep.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, interrupt map/name mistakes hide link, MSI, or error events, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,j721e-pci-ep.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,j721e-pci-ep.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,j721e-pci-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,j721e-pci-host.yaml

## Purpose
TI J721E PCI Host (PCIe Wrapper) is a PCI/PCIe host bridge or root-complex binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Kishon Vijay Abraham I <kishon@ti.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/ti,j721e-pci-host.yaml#`. compatible values `ti,j721e-pcie-host`, `ti,j784s4-pcie-host`, `ti,am64-pcie-host`, `ti,j7200-pcie-host`, `ti,j722s-pcie-host`. required properties `compatible`, `reg`, `reg-names`, `ti,syscon-pcie-ctrl`, `max-link-speed`, `num-lanes`, `power-domains`, `clocks`, and 9 more. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `msi-map`, `clocks`, `clock-names`, and 7 more. register names `intd_cfg`, `user_cfg`, `reg`, `cfg`. clock names `fck`, `pcie_refclk`. interrupt names `link_state`. schema refs `phandle-array`, `cdns-pcie-host.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 4 `allOf` layer(s); 3 conditional branch(es); 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `power-domains`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `phandle-array`, `cdns-pcie-host.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, interrupt map/name mistakes hide link, MSI, or error events, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,j721e-pci-host.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/ti,j721e-pci-host.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/toshiba,visconti-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/toshiba,visconti-pcie.yaml

## Purpose
Toshiba Visconti5 SoC PCIe Host Controller is a PCI/PCIe controller binding. Toshiba Visconti5 SoC PCIe host controller is based on the Synopsys DesignWare PCIe IP. Maintainers: Nobuhiro Iwamatsu <nobuhiro1.iwamatsu@toshiba.co.jp>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/toshiba,visconti-pcie.yaml#`. compatible values `toshiba,visconti-pcie`. required properties `reg`, `reg-names`, `interrupts`, `#interrupt-cells`, `interrupt-map`, `interrupt-map-mask`, `num-lanes`, `clocks`, and 2 more. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `num-lanes`. register names `dbi`, `config`, `ulreg`, `smu`, `mpu`. clock names `ref`, `core`, `aux`. schema refs `snps,dw-pcie.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `snps,dw-pcie.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/toshiba,visconti-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/toshiba,visconti-pcie.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/v3,v360epc-pci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/v3,v360epc-pci.yaml

## Purpose
V3 Semiconductor V360 EPC PCI bridge is a PCIe endpoint controller binding. This bridge is found in the ARM Integrator/AP (Application Platform) Maintainers: Linus Walleij <linusw@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/v3,v360epc-pci.yaml#`. compatible values `arm,integrator-ap-pci`, `v3,v360epc-pci`. required properties `compatible`, `reg`, `clocks`, `dma-ranges`, `#interrupt-cells`, `interrupt-map`, `interrupt-map-mask`. notable properties `compatible`, `reg`, `ranges`, `dma-ranges`, `interrupts`, `clocks`. schema refs `pci-host-bridge.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `interrupts`, `ranges`, `dma-ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/v3,v360epc-pci.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/v3,v360epc-pci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/versatile.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/versatile.yaml

## Purpose
ARM Versatile Platform Baseboard PCI interface is a PCI/PCIe controller binding. PCI host controller found on the ARM Versatile PB board's FPGA. Maintainers: Rob Herring <robh@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/versatile.yaml#`. compatible values `arm,versatile-pci`. required properties `compatible`, `reg`, `ranges`, `#interrupt-cells`, `interrupt-map`, `interrupt-map-mask`. notable properties `compatible`, `reg`, `ranges`, `#interrupt-cells`, `interrupt-map`, `interrupt-map-mask`. schema refs `pci-host-bridge.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/versatile.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/versatile.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xilinx-versal-cpm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xilinx-versal-cpm.yaml

## Purpose
CPM Host Controller device tree for Xilinx Versal SoCs is a PCI/PCIe controller binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Bharat Kumar Gogada <bharat.kumar.gogada@amd.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/xilinx-versal-cpm.yaml#`. compatible values `xlnx,versal-cpm-host-1.00`, `xlnx,versal-cpm5-host`, `xlnx,versal-cpm5-host1`, `xlnx,versal-cpm5nc-host`. required properties `reg`, `reg-names`, `#interrupt-cells`, `interrupts`, `interrupt-map`, `interrupt-map-mask`, `bus-range`, `msi-map`, and 1 more. notable properties `compatible`, `reg`, `reg-names`, `ranges`, `#interrupt-cells`, `interrupts`, `msi-map`, `interrupt-controller`. register names `cpm_slcr`, `cfg`, `cpm_csr`. schema refs `pci-host-bridge.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `interrupts`, `ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xilinx-versal-cpm.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xilinx-versal-cpm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,axi-pcie-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,axi-pcie-host.yaml

## Purpose
Xilinx AXI PCIe Root Port Bridge is a PCI/PCIe host bridge or root-complex binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Thippeswamy Havalige <thippeswamy.havalige@amd.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/xlnx,axi-pcie-host.yaml#`. compatible values `xlnx,axi-pcie-host-1.00.a`. required properties `compatible`, `reg`, `ranges`, `interrupts`, `interrupt-map`, `#interrupt-cells`, `interrupt-controller`. notable properties `compatible`, `reg`, `ranges`, `#interrupt-cells`, `interrupts`, `interrupt-controller`. schema refs `pci-host-bridge.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `interrupts`, `ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,axi-pcie-host.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,axi-pcie-host.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,nwl-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,nwl-pcie.yaml

## Purpose
Xilinx NWL PCIe Root Port Bridge is a PCI/PCIe host bridge or root-complex binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Thippeswamy Havalige <thippeswamy.havalige@amd.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/xlnx,nwl-pcie.yaml#`. compatible values `xlnx,nwl-pcie-2.11`. required properties `compatible`, `reg`, `reg-names`, `interrupts`, `#interrupt-cells`, `interrupt-map`, `interrupt-map-mask`, `msi-controller`, and 1 more. notable properties `compatible`, `reg`, `reg-names`, `#interrupt-cells`, `interrupts`, `interrupt-names`, `interrupt-map`, `interrupt-map-mask`, and 7 more. register names `breg`, `pcireg`, `cfg`. interrupt names `misc`, `dummy`, `intx`, `msi1`, `msi0`. schema refs `msi-controller.yaml#`, `pci-host-bridge.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 2 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `power-domains`, `phys`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `msi-controller.yaml#`, `pci-host-bridge.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, interrupt map/name mistakes hide link, MSI, or error events. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,nwl-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,nwl-pcie.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,xdma-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,xdma-host.yaml

## Purpose
Xilinx XDMA PL PCIe Root Port Bridge is a PCI/PCIe host bridge or root-complex binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Thippeswamy Havalige <thippeswamy.havalige@amd.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/xlnx,xdma-host.yaml#`. compatible values `xlnx,xdma-host-3.00`, `xlnx,qdma-host-3.00`. required properties `compatible`, `reg`, `ranges`, `interrupts`, `interrupt-map`, `interrupt-map-mask`, `#interrupt-cells`, `interrupt-controller`. notable properties `compatible`, `reg`, `reg-names`, `ranges`, `#interrupt-cells`, `interrupts`, `interrupt-names`, `interrupt-map`, and 2 more. register names `cfg`, `breg`. interrupt names `misc`, `msi0`, `msi1`. schema refs `pci-host-bridge.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); 1 conditional branch(es); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `interrupts`, `ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `pci-host-bridge.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, interrupt map/name mistakes hide link, MSI, or error events, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,xdma-host.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/xlnx,xdma-host.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/nuvoton,npcm-peci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/nuvoton,npcm-peci.yaml

## Purpose
Nuvoton PECI Bus is a PECI controller/common binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Tomer Maimon <tmaimon77@gmail.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/peci/nuvoton,npcm-peci.yaml#`. compatible values `nuvoton,npcm750-peci`, `nuvoton,npcm845-peci`. required properties `compatible`, `reg`, `interrupts`, `clocks`. notable properties `compatible`, `reg`, `interrupts`, `clocks`, `cmd-timeout-ms`. schema refs `peci-controller.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `peci-controller.yaml#`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/nuvoton,npcm-peci.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/nuvoton,npcm-peci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-aspeed.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-aspeed.yaml

## Purpose
Aspeed PECI Bus is a PECI controller/common binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Iwona Winiarska <iwona.winiarska@intel.com>, Jae Hyun Yoo <jae.hyun.yoo@linux.intel.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/peci/peci-aspeed.yaml#`. compatible values `aspeed,ast2400-peci`, `aspeed,ast2500-peci`, `aspeed,ast2600-peci`. required properties `compatible`, `reg`, `interrupts`, `clocks`, `resets`. notable properties `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `cmd-timeout-ms`, `clock-frequency`. schema refs `peci-controller.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `peci-controller.yaml#`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-aspeed.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-aspeed.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-controller.yaml

## Purpose
Generic for PECI is a PECI controller/common binding. PECI (Platform Environment Control Interface) is an interface that provides a communication channel from Intel processors and chipset components to external monitoring or control devices. Maintainers: Iwona Winiarska <iwona.winiarska@intel.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/peci/peci-controller.yaml#`. required properties none declared. notable properties `$nodename`, `cmd-timeout-ms`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: compatible strings and node topology. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is open for inherited/vendor properties.

## Risks
Primary risks are schema/property drift can allow invalid DTS nodes or reject existing boards. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-controller.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/amlogic,g12-ddr-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/amlogic,g12-ddr-pmu.yaml

## Purpose
Amlogic G12 DDR performance monitor is a performance monitoring unit binding. Amlogic G12 series SoC integrate DDR bandwidth monitor. A timer is inside and can generate interrupt when timeout. The bandwidth is counted in the timer ISR. Different platform has different subset of event format attribute. Maintainers: Jiucheng Xu <jiucheng.xu@amlogic.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/amlogic,g12-ddr-pmu.yaml#`. compatible values `amlogic,g12a-ddr-pmu`, `amlogic,g12b-ddr-pmu`, `amlogic,sm1-ddr-pmu`. required properties `compatible`, `reg`, `interrupts`. notable properties `compatible`, `reg`, `interrupts`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/amlogic,g12-ddr-pmu.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/amlogic,g12-ddr-pmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/apm,xgene-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/apm,xgene-pmu.yaml

## Purpose
APM X-Gene SoC PMU is a performance monitoring unit binding. This is APM X-Gene SoC PMU (Performance Monitoring Unit) module. The following PMU devices are supported:    L3C            - L3 cache controller   IOB            - IO bridge   MCB            - Memory controller bridge   MC             - Memory controller Maintainers: Khuong Dinh <khuong@os.amperecomputing.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/apm,xgene-pmu.yaml#`. compatible values `apm,xgene-pmu`, `apm,xgene-pmu-v2`. required properties `compatible`, `regmap-csw`, `regmap-mcba`, `regmap-mcbb`, `reg`, `interrupts`. notable properties `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`, `interrupts`, `regmap-csw`, `regmap-mcba`, and 1 more. schema refs `phandle`, `uint32`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `interrupts`, `ranges`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `phandle`, `uint32`; property closure is constrained mostly by referenced schemas.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/apm,xgene-pmu.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/apm,xgene-pmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,ccn.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,ccn.yaml

## Purpose
ARM CCN (Cache Coherent Network) Performance Monitors is a performance monitoring unit binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Robin Murphy <robin.murphy@arm.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/arm,ccn.yaml#`. compatible values `arm,ccn-502`, `arm,ccn-504`, `arm,ccn-508`, `arm,ccn-512`. required properties `compatible`, `reg`, `interrupts`. notable properties `compatible`, `reg`, `interrupts`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,ccn.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,ccn.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,cmn.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,cmn.yaml

## Purpose
Arm CMN (Coherent Mesh Network) Performance Monitors is a performance monitoring unit binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Robin Murphy <robin.murphy@arm.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/arm,cmn.yaml#`. compatible values `arm,cmn-600`, `arm,cmn-650`, `arm,cmn-700`, `arm,cmn-s3`, `arm,ci-700`. required properties `compatible`, `reg`, `interrupts`. notable properties `compatible`, `reg`, `interrupts`, `arm,root-node`. schema refs `uint32`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 conditional branch(es); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `uint32`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,cmn.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,cmn.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,coresight-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,coresight-pmu.yaml

## Purpose
Arm Coresight Performance Monitoring Unit Architecture is a performance monitoring unit binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Robin Murphy <robin.murphy@arm.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/arm,coresight-pmu.yaml#`. compatible values `arm,coresight-pmu`. required properties `compatible`, `reg`. notable properties `compatible`, `reg`, `interrupts`, `cpus`, `reg-io-width`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,coresight-pmu.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,coresight-pmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,dsu-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,dsu-pmu.yaml

## Purpose
ARM DynamIQ Shared Unit (DSU) Performance Monitor Unit (PMU) is a performance monitoring unit binding. ARM DynamIQ Shared Unit (DSU) integrates one or more CPU cores with a shared L3 memory system, control logic and external interfaces to form a multicore cluster. The PMU enables gathering various statistics on the operation of the DSU. The PMU provides independent 32-bit counters that can count any of the supported events, along with a 64-bit cycle counter. The PMU is accessed via CPU system registers and has no MMIO component. Maintainers: Suzuki K Poulose <suzuki.poulose@arm.com>, Robin Murphy <robin.murphy@arm.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/arm,dsu-pmu.yaml#`. compatible values `arm,dsu-pmu`, `arm,dsu-110-pmu`. required properties `compatible`, `interrupts`, `cpus`. notable properties `compatible`, `interrupts`, `cpus`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,dsu-pmu.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,dsu-pmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,ni.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,ni.yaml

## Purpose
Arm NI (Network-on-Chip Interconnect) Performance Monitors is a performance monitoring unit binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Robin Murphy <robin.murphy@arm.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/arm,ni.yaml#`. compatible values `arm,ni-700`. required properties `compatible`, `reg`, `interrupts`. notable properties `compatible`, `reg`, `interrupts`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,ni.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,ni.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,smmu-v3-pmcg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,smmu-v3-pmcg.yaml

## Purpose
Arm SMMUv3 Performance Monitor Counter Group is a performance monitoring unit binding. An SMMUv3 may have several Performance Monitor Counter Group (PMCG). They are standalone performance monitoring units that support both architected and IMPLEMENTATION DEFINED event counters. Maintainers: Will Deacon <will@kernel.org>, Robin Murphy <robin.murphy@arm.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/arm,smmu-v3-pmcg.yaml#`. compatible values `arm,mmu-600-pmcg`, `arm,smmu-v3-pmcg`. required properties `compatible`, `reg`. notable properties `compatible`, `reg`, `interrupts`, `msi-parent`, `$nodename`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 `oneOf` and 2 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,smmu-v3-pmcg.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/arm,smmu-v3-pmcg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/fsl-imx-ddr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/fsl-imx-ddr.yaml

## Purpose
Freescale(NXP) IMX8/9 DDR performance monitor is a performance monitoring unit binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Frank Li <frank.li@nxp.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/fsl-imx-ddr.yaml#`. compatible values `fsl,imx8-ddr-pmu`, `fsl,imx8dxl-db-pmu`, `fsl,imx8m-ddr-pmu`, `fsl,imx8mq-ddr-pmu`, `fsl,imx8mm-ddr-pmu`, `fsl,imx8mn-ddr-pmu`, `fsl,imx8mp-ddr-pmu`, `fsl,imx93-ddr-pmu`, and 6 more. required properties `compatible`, `reg`, `interrupts`. notable properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. clock names `ipg`, `cnt`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 `allOf` layer(s); 1 conditional branch(es); 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/fsl-imx-ddr.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/fsl-imx-ddr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/marvell-cn10k-ddr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/marvell-cn10k-ddr.yaml

## Purpose
Marvell CN10K DDR performance monitor is a performance monitoring unit binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Bharat Bhushan <bbhushan2@marvell.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/marvell-cn10k-ddr.yaml#`. compatible values `marvell,cn10k-ddr-pmu`. required properties `compatible`, `reg`. notable properties `compatible`, `reg`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/marvell-cn10k-ddr.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/marvell-cn10k-ddr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/marvell-cn10k-tad.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/marvell-cn10k-tad.yaml

## Purpose
Marvell CN10K LLC-TAD performance monitor is a performance monitoring unit binding. The Tag-and-Data units (TADs) maintain coherence and contain CN10K shared on-chip last level cache (LLC). The tad pmu measures the performance of last-level cache. Each tad pmu supports up to eight counters.  The DT setup comprises of number of tad blocks, the sizes of pmu regions, tad blocks and overall base address of the HW. Maintainers: Bhaskara Budiredla <bbudiredla@marvell.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/marvell-cn10k-tad.yaml#`. compatible values `marvell,cn10k-tad-pmu`. required properties `compatible`, `reg`, `marvell,tad-cnt`, `marvell,tad-page-size`, `marvell,tad-pmu-page-size`. notable properties `compatible`, `reg`, `marvell,tad-cnt`, `marvell,tad-page-size`, `marvell,tad-pmu-page-size`. schema refs `uint32`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `uint32`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/marvell-cn10k-tad.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/marvell-cn10k-tad.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/riscv,pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/riscv,pmu.yaml

## Purpose
RISC-V SBI PMU events is a performance monitoring unit binding. The SBI PMU extension allows supervisor software to configure, start and stop any performance counter at anytime. Thus, a user can leverage all capabilities of performance analysis tools, such as perf, if the SBI PMU extension is enabled. The following constraints apply:    The platform must provide information about PMU event to counter mappings   either via device tree or another way, specific to the platform.   Without the event to counter mappings, the SBI PMU extension cannot be used.    Platforms should provide information about the PMU event selector values   that should be encoded in the expected value of MHPMEVENTx while configuring   MHPMCOUNTERx for that specific event. The can either be done via device tree   or another way, specific to the platform.   The exact value to be written to MHPMEVENTx is completely dependent on the   platform.    For information on the SBI specification see the section "Performance   Monitoring Unit Extension" of:     https://github.com/riscv-non-isa/riscv-sbi-doc/blob/master/riscv-sbi.adoc Maintainers: Atish Patra <atishp@rivosinc.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/riscv,pmu.yaml#`. compatible values `riscv,pmu`. required properties `compatible`. notable properties `compatible`, `riscv,event-to-mhpmevent`, `riscv,event-to-mhpmcounters`, `riscv,raw-event-to-mhpmcounters`. schema refs `uint32-matrix`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; dependency rules for `riscv,event-to-mhpmevent`; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: compatible strings and node topology. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `uint32-matrix`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/riscv,pmu.yaml` and `make dtbs_check` against boards using this binding; the 2 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/riscv,pmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/spe-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/spe-pmu.yaml

## Purpose
ARMv8.2 Statistical Profiling Extension (SPE) Performance Monitor Units (PMU) is a performance monitoring unit binding. ARMv8.2 introduces the optional Statistical Profiling Extension for collecting performance sample data using an in-memory trace buffer. Maintainers: Will Deacon <will@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/spe-pmu.yaml#`. compatible values `arm,statistical-profiling-extension-v1`. required properties `compatible`, `interrupts`. notable properties `compatible`, `interrupts`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/spe-pmu.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/spe-pmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/starfive,jh8100-starlink-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/starfive,jh8100-starlink-pmu.yaml

## Purpose
StarFive JH8100 StarLink PMU is a performance monitoring unit binding. StarFive's JH8100 StarLink PMU integrates one or more CPU cores with a shared L3 memory system. The PMU support overflow interrupt, up to 16 programmable 64bit event counters, and an independent 64bit cycle counter. StarFive's JH8100 StarLink PMU is accessed via MMIO. Maintainers: Ji Sheng Teoh <jisheng.teoh@starfivetech.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/starfive,jh8100-starlink-pmu.yaml#`. compatible values `starfive,jh8100-starlink-pmu`. required properties `compatible`, `reg`, `interrupts`. notable properties `compatible`, `reg`, `interrupts`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/starfive,jh8100-starlink-pmu.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/starfive,jh8100-starlink-pmu.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun4i-a10-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun4i-a10-usb-phy.yaml

## Purpose
Allwinner A10 USB PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun4i-a10-usb-phy.yaml#`. compatible values `allwinner,sun4i-a10-usb-phy`, `allwinner,sun7i-a20-usb-phy`. required properties `#phy-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, and 6 more. register names `phy_ctrl`, `pmu1`, `pmu2`. clock names `usb_phy`. reset names `usb0_reset`, `usb1_reset`, `usb2_reset`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun4i-a10-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun4i-a10-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun50i-a64-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun50i-a64-usb-phy.yaml

## Purpose
Allwinner A64 USB PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun50i-a64-usb-phy.yaml#`. compatible values `allwinner,sun20i-d1-usb-phy`, `allwinner,sun50i-a64-usb-phy`, `allwinner,sun50i-a100-usb-phy`, `allwinner,sun55i-a523-usb-phy`. required properties `#phy-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, and 5 more. register names `phy_ctrl`, `pmu0`, `pmu1`. clock names `usb0_phy`, `usb1_phy`. reset names `usb0_reset`, `usb1_reset`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun50i-a64-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun50i-a64-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun50i-h6-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun50i-h6-usb-phy.yaml

## Purpose
Allwinner H6 USB PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun50i-h6-usb-phy.yaml#`. compatible values `allwinner,sun50i-h6-usb-phy`. required properties `#phy-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, and 5 more. register names `phy_ctrl`, `pmu0`, `pmu3`. clock names `usb0_phy`, `usb3_phy`. reset names `usb0_reset`, `usb3_reset`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun50i-h6-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun50i-h6-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun50i-h6-usb3-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun50i-h6-usb3-phy.yaml

## Purpose
Allwinner H6 USB3 PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Ondrej Jirman <megous@megous.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun50i-h6-usb3-phy.yaml#`. compatible values `allwinner,sun50i-h6-usb3-phy`. required properties `compatible`, `reg`, `clocks`, `resets`, `#phy-cells`. notable properties `compatible`, `reg`, `clocks`, `resets`, `#phy-cells`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun50i-h6-usb3-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun50i-h6-usb3-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun5i-a13-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun5i-a13-usb-phy.yaml

## Purpose
Allwinner A13 USB PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun5i-a13-usb-phy.yaml#`. compatible values `allwinner,sun5i-a13-usb-phy`. required properties `#phy-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, and 5 more. register names `phy_ctrl`, `pmu1`. clock names `usb_phy`. reset names `usb0_reset`, `usb1_reset`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun5i-a13-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun5i-a13-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun6i-a31-mipi-dphy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun6i-a31-mipi-dphy.yaml

## Purpose
Allwinner A31 MIPI D-PHY Controller is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun6i-a31-mipi-dphy.yaml#`. compatible values `allwinner,sun6i-a31-mipi-dphy`, `allwinner,sun50i-a100-mipi-dphy`, `allwinner,sun50i-a64-mipi-dphy`, `allwinner,sun20i-d1-mipi-dphy`. required properties `#phy-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. notable properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `#phy-cells`, `allwinner,direction`. clock names `bus`, `mod`. schema refs `string`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `string`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun6i-a31-mipi-dphy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun6i-a31-mipi-dphy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun6i-a31-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun6i-a31-usb-phy.yaml

## Purpose
Allwinner A31 USB PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun6i-a31-usb-phy.yaml#`. compatible values `allwinner,sun6i-a31-usb-phy`. required properties `#phy-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, and 6 more. register names `phy_ctrl`, `pmu1`, `pmu2`. clock names `usb0_phy`, `usb1_phy`, `usb2_phy`. reset names `usb0_reset`, `usb1_reset`, `usb2_reset`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun6i-a31-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun6i-a31-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-a23-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-a23-usb-phy.yaml

## Purpose
Allwinner A23 USB PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun8i-a23-usb-phy.yaml#`. compatible values `allwinner,sun8i-a23-usb-phy`, `allwinner,sun8i-a33-usb-phy`. required properties `#phy-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, and 5 more. register names `phy_ctrl`, `pmu1`. clock names `usb0_phy`, `usb1_phy`. reset names `usb0_reset`, `usb1_reset`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-a23-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-a23-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-a83t-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-a83t-usb-phy.yaml

## Purpose
Allwinner A83t USB PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun8i-a83t-usb-phy.yaml#`. compatible values `allwinner,sun8i-a83t-usb-phy`. required properties `#phy-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, and 6 more. register names `phy_ctrl`, `pmu1`, `pmu2`. clock names `usb0_phy`, `usb1_phy`, `usb2_phy`, `usb2_hsic_12M`. reset names `usb0_reset`, `usb1_reset`, `usb2_reset`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-a83t-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-a83t-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-h3-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-h3-usb-phy.yaml

## Purpose
Allwinner H3 USB PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun8i-h3-usb-phy.yaml#`. compatible values `allwinner,sun8i-h3-usb-phy`, `allwinner,sun50i-h616-usb-phy`. required properties `#phy-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, and 7 more. register names `phy_ctrl`, `pmu0`, `pmu1`, `pmu2`, `pmu3`. clock names `usb0_phy`, `usb1_phy`, `usb2_phy`, `usb3_phy`, `pmu2_clk`. reset names `usb0_reset`, `usb1_reset`, `usb2_reset`, `usb3_reset`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 `allOf` layer(s); 1 conditional branch(es); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-h3-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-h3-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-r40-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-r40-usb-phy.yaml

## Purpose
Allwinner R40 USB PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun8i-r40-usb-phy.yaml#`. compatible values `allwinner,sun8i-r40-usb-phy`. required properties `#phy-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, and 6 more. register names `phy_ctrl`, `pmu0`, `pmu1`, `pmu2`. clock names `usb0_phy`, `usb1_phy`, `usb2_phy`. reset names `usb0_reset`, `usb1_reset`, `usb2_reset`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-r40-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-r40-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-v3s-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-v3s-usb-phy.yaml

## Purpose
Allwinner V3s USB PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun8i-v3s-usb-phy.yaml#`. compatible values `allwinner,sun8i-v3s-usb-phy`. required properties `#phy-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, and 4 more. register names `phy_ctrl`, `pmu0`. clock names `usb0_phy`. reset names `usb0_reset`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-v3s-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun8i-v3s-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun9i-a80-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun9i-a80-usb-phy.yaml

## Purpose
Allwinner A80 USB PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,sun9i-a80-usb-phy.yaml#`. compatible values `allwinner,sun9i-a80-usb-phy`. required properties `#phy-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, `phy_type`, and 1 more. clock names `phy`, `hsic_12M`, `hsic_480M`. reset names `phy`, `hsic`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 conditional branch(es); 1 `oneOf` and 1 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun9i-a80-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 2 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,sun9i-a80-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,suniv-f1c100s-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,suniv-f1c100s-usb-phy.yaml

## Purpose
Allwinner F1C100s USB PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/allwinner,suniv-f1c100s-usb-phy.yaml#`. compatible values `allwinner,suniv-f1c100s-usb-phy`. required properties `#phy-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `reg-names`, `resets`, `reset-names`. notable properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, and 4 more. register names `phy_ctrl`. clock names `usb0_phy`. reset names `usb0_reset`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,suniv-f1c100s-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/allwinner,suniv-f1c100s-usb-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,axg-mipi-dphy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,axg-mipi-dphy.yaml

## Purpose
Amlogic AXG MIPI D-PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/amlogic,axg-mipi-dphy.yaml#`. compatible values `amlogic,axg-mipi-dphy`. required properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, `phy-names`, and 1 more. notable properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, `phy-names`, and 1 more. clock names `pclk`. reset names `phy`. PHY names `analog`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`, `phys`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,axg-mipi-dphy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,axg-mipi-dphy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-mipi-dphy-analog.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-mipi-dphy-analog.yaml

## Purpose
Amlogic G12A MIPI analog PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Neil Armstrong <narmstrong@baylibre.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/amlogic,g12a-mipi-dphy-analog.yaml#`. compatible values `amlogic,g12a-mipi-dphy-analog`. required properties `compatible`, `#phy-cells`. notable properties `compatible`, `#phy-cells`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: compatible strings and node topology. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-mipi-dphy-analog.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-mipi-dphy-analog.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-usb2-phy.yaml

## Purpose
Amlogic G12A USB2 PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/amlogic,g12a-usb2-phy.yaml#`. compatible values `amlogic,g12a-usb2-phy`, `amlogic,a1-usb2-phy`. required properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`. notable properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `#phy-cells`, and 1 more. clock names `xtal`. reset names `phy`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 conditional branch(es); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`, `power-domains`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-usb2-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-usb2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-usb3-pcie-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-usb3-pcie-phy.yaml

## Purpose
Amlogic G12A USB3 + PCIE Combo PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/amlogic,g12a-usb3-pcie-phy.yaml#`. compatible values `amlogic,g12a-usb3-pcie-phy`. required properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`. notable properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, `phy-supply`. clock names `ref_clk`. reset names `phy`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-usb3-pcie-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,g12a-usb3-pcie-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson-axg-mipi-pcie-analog.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson-axg-mipi-pcie-analog.yaml

## Purpose
Amlogic AXG shared MIPI/PCIE analog PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Remi Pommarel <repk@triplefau.lt>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/amlogic,meson-axg-mipi-pcie-analog.yaml#`. compatible values `amlogic,axg-mipi-pcie-analog-phy`. required properties `compatible`, `#phy-cells`. notable properties `compatible`, `#phy-cells`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: compatible strings and node topology. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson-axg-mipi-pcie-analog.yaml` and `make dtbs_check` against in-tree DTS users; no embedded examples are present, so DTS coverage matters more. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson-axg-mipi-pcie-analog.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson-axg-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson-axg-pcie.yaml

## Purpose
Amlogic AXG PCIE PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Remi Pommarel <repk@triplefau.lt>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/amlogic,meson-axg-pcie.yaml#`. compatible values `amlogic,axg-pcie-phy`. required properties `compatible`, `reg`, `phys`, `phy-names`, `resets`, `#phy-cells`. notable properties `compatible`, `reg`, `resets`, `phys`, `phy-names`, `#phy-cells`. PHY names `analog`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `resets`, `phys`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson-axg-pcie.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson-axg-pcie.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson-gxl-usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson-gxl-usb2-phy.yaml

## Purpose
Amlogic Meson GXL USB2 PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/amlogic,meson-gxl-usb2-phy.yaml#`. compatible values `amlogic,meson-gxl-usb2-phy`. required properties `compatible`, `reg`, `#phy-cells`. notable properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `#phy-cells`, `phy-supply`. clock names `phy`. reset names `phy`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, reset polarity/name drift can strand hardware in reset, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson-gxl-usb2-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson-gxl-usb2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson8-hdmi-tx-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson8-hdmi-tx-phy.yaml

## Purpose
Amlogic Meson8, Meson8b and Meson8m2 HDMI TX PHY is a physical-layer transceiver binding. The HDMI TX PHY node should be the child of a syscon node with the required property:  compatible = "amlogic,meson-hhi-sysctrl", "simple-mfd", "syscon"  Refer to the bindings described in Documentation/devicetree/bindings/mfd/syscon.yaml Maintainers: Martin Blumenstingl <martin.blumenstingl@googlemail.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/amlogic,meson8-hdmi-tx-phy.yaml#`. compatible values `amlogic,meson8b-hdmi-tx-phy`, `amlogic,meson8m2-hdmi-tx-phy`, `amlogic,meson8-hdmi-tx-phy`. required properties `compatible`, `#phy-cells`. notable properties `compatible`, `reg`, `clocks`, `#phy-cells`, `$nodename`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson8-hdmi-tx-phy.yaml` and `make dtbs_check` against boards using this binding; the 2 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson8-hdmi-tx-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson8b-usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson8b-usb2-phy.yaml

## Purpose
Amlogic Meson8, Meson8b, Meson8m2 and GXBB USB2 PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Martin Blumenstingl <martin.blumenstingl@googlemail.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/amlogic,meson8b-usb2-phy.yaml#`. compatible values `amlogic,meson8-usb2-phy`, `amlogic,meson8b-usb2-phy`, `amlogic,meson8m2-usb2-phy`, `amlogic,meson-mx-usb2-phy`, `amlogic,meson-gxbb-usb2-phy`. required properties `compatible`, `reg`, `clocks`, `clock-names`, `#phy-cells`. notable properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `#phy-cells`, `phy-supply`. clock names `usb_general`, `usb`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 `oneOf` and 0 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson8b-usb2-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/amlogic,meson8b-usb2-phy.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/bcm-ns-usb2-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/bcm-ns-usb2-phy.yaml

## Purpose
Broadcom Northstar USB 2.0 PHY is a physical-layer transceiver binding. To initialize USB 2.0 PHY driver needs to setup PLL correctly. To do this it requires passing phandle to the USB PHY reference clock. Maintainers: Rafał Miłecki <rafal@milecki.pl>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/bcm-ns-usb2-phy.yaml#`. compatible values `brcm,ns-usb2-phy`. required properties `compatible`, `reg`, `clocks`, `clock-names`, `#phy-cells`, `brcm,syscon-clkset`. notable properties `compatible`, `reg`, `clocks`, `clock-names`, `#phy-cells`, `brcm,syscon-clkset`. clock names `phy-ref-clk`. schema refs `phandle`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `phandle`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/bcm-ns-usb2-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/bcm-ns-usb2-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/bcm-ns-usb3-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/bcm-ns-usb3-phy.yaml

## Purpose
Broadcom Northstar USB 3.0 PHY is a physical-layer transceiver binding. Initialization of USB 3.0 PHY depends on Northstar version. There are currently three known series: Ax, Bx and Cx. Known A0: BCM4707 rev 0 Known B0: BCM4707 rev 4, BCM53573 rev 2 Known B1: BCM4707 rev 6 Known C0: BCM47094 rev 0 Maintainers: Rafał Miłecki <rafal@milecki.pl>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/bcm-ns-usb3-phy.yaml#`. compatible values `brcm,ns-ax-usb3-phy`, `brcm,ns-bx-usb3-phy`. required properties `compatible`, `reg`, `usb3-dmp-syscon`, `#phy-cells`. notable properties `compatible`, `reg`, `#phy-cells`, `usb3-dmp-syscon`. schema refs `phandle`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `phandle`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, PHY phandle/cell mismatches break lane bring-up. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/bcm-ns-usb3-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/bcm-ns-usb3-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/brcm,bcm63xx-usbh-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/brcm,bcm63xx-usbh-phy.yaml

## Purpose
BCM63xx USBH PHY is a physical-layer transceiver binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Álvaro Fernández Rojas <noltari@gmail.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/brcm,bcm63xx-usbh-phy.yaml#`. compatible values `brcm,bcm6318-usbh-phy`, `brcm,bcm6328-usbh-phy`, `brcm,bcm6358-usbh-phy`, `brcm,bcm6362-usbh-phy`, `brcm,bcm6368-usbh-phy`, `brcm,bcm63268-usbh-phy`. required properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `#phy-cells`. notable properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `#phy-cells`. clock names `usbh`, `usb_ref`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through 1 conditional branch(es); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, clock-name drift can leave runtime PM or link training incomplete, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/brcm,bcm63xx-usbh-phy.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/brcm,bcm63xx-usbh-phy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/brcm,brcmstb-usb-phy.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/brcm,brcmstb-usb-phy.yaml

## Purpose
Broadcom STB USB PHY is a physical-layer transceiver binding. Broadcom's PHY that handles EHCI/OHCI and/or XHCI Maintainers: Al Cooper <alcooperx@gmail.com>, Rafał Miłecki <rafal@milecki.pl>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/phy/brcm,brcmstb-usb-phy.yaml#`. compatible values `brcm,bcm4908-usb-phy`, `brcm,bcm7211-usb-phy`, `brcm,bcm7216-usb-phy`, `brcm,bcm74110-usb-phy`, `brcm,brcmstb-usb-phy`. required properties `reg`, `#phy-cells`. notable properties `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`, and 7 more. register names `ctrl`, `xhci_ec`, `xhci_gbl`, `usb_phy`, `usb_mdio`, `bdc_ec`. clock names `sw_usb`, `sw_usb3`. interrupt names `wake`. schema refs `phandle`, `uint32`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 3 `allOf` layer(s); 3 conditional branch(es); 0 `oneOf` and 2 `anyOf` choice set(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`, `clocks`, `power-domains`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `phandle`, `uint32`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding, clock-name drift can leave runtime PM or link training incomplete, interrupt map/name mistakes hide link, MSI, or error events, PHY phandle/cell mismatches break lane bring-up, conditional schema branches can reject otherwise valid SoC variants if compatibles are ordered incorrectly. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/brcm,brcmstb-usb-phy.yaml` and `make dtbs_check` against boards using this binding; the 2 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/phy/brcm,brcmstb-usb-phy.yaml -->
