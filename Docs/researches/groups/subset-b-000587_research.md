# subset-b-000587 grouped research

This grouped report covers 63 source-tree-aligned devicetree binding YAML files. Each section is wrapped with the required BEGIN/END markers so the reconciliation lane can split it into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8650-camss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8650-camss.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8650-camss.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Qualcomm SM8650 Camera Subsystem (CAMSS)`. Description signal from the file: The CAMSS IP is a CSI decoder and ISP present on Qualcomm platforms..

## Purpose
The file defines the devicetree ABI for `Qualcomm SM8650 Camera Subsystem (CAMSS)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: qcom,sm8650-camss.
- required node contract: compatible, reg, reg-names, clocks, clock-names, interconnects, interconnect-names, interrupts, interrupt-names, iommus, power-domains, power-domain-names.
- property surface: `compatible` (const qcom,sm8650-camss), `reg` (maxItems=17), `reg-names` (ordered-items=17; ordered csid_wrapper, csid0, csid1, csid2, csid_lite0, csid_lite1, csiphy0, csiphy1, and 9 more), `clocks` (maxItems=33), `clock-names` (ordered-items=33; ordered camnoc_axi, cpas_ahb, cpas_fast_ahb, cpas_vfe0, cpas_vfe1, cpas_vfe2, cpas_vfe_lite, csid, and 25 more), `interrupts` (maxItems=16), `interrupt-names` (ordered-items=16; ordered csid0, csid1, csid2, csid_lite0, csid_lite1, csiphy0, csiphy1, csiphy2, and 8 more), `interconnects` (maxItems=2), `interconnect-names` (ordered-items=2; ordered ahb, hf_mnoc), `iommus` (maxItems=3), `power-domains` (ordered-items=4), `power-domain-names` (ordered-items=4; ordered ife0, ife1, ife2, top), `ports` (ref /schemas/graph.yaml#/properties/ports), `vdd-csiphy01-0p9-supply` (Phandle to a 0.9V regulator supply to CSIPHY0 and CSIPHY1 IP blocks.), `vdd-csiphy01-1p2-supply` (Phandle to a 1.2V regulator supply to CSIPHY0 and CSIPHY1 IP blocks.), `vdd-csiphy24-0p9-supply` (Phandle to a 0.9V regulator supply to CSIPHY2 and CSIPHY4 IP blocks.), and 3 more.
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. Regulator supply properties persist power-rail dependencies that board DTS files must wire correctly. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Vladimir Zapolskiy <vladimir.zapolskiy@linaro.org>.
- schema id: http://devicetree.org/schemas/media/qcom,sm8650-camss.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, reg-names, clocks, clock-names, interconnects, interconnect-names, interrupts, interrupt-names, iommus, power-domains, power-domain-names`, optional top-level properties include `ports, vdd-csiphy01-0p9-supply, vdd-csiphy01-1p2-supply, vdd-csiphy24-0p9-supply, vdd-csiphy24-1p2-supply, vdd-csiphy35-0p9-supply, vdd-csiphy35-1p2-supply`, and compatible coverage is `qcom,sm8650-camss`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8650-camss.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8650-camss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8750-iris.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8750-iris.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8750-iris.yaml`, a video codec/accelerator devicetree binding. The schema title is `Qualcomm SM8750 SoC Iris video encoder and decoder`. Description signal from the file: The Iris video processing unit on Qualcomm SM8750 SoC is a video encode and decode accelerator..

## Purpose
The file defines the devicetree ABI for `Qualcomm SM8750 SoC Iris video encoder and decoder`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: qcom,sm8750-iris.
- required node contract: compatible, dma-coherent, interconnects, interconnect-names, iommus, power-domain-names, resets, reset-names.
- property surface: `compatible` (enum qcom,sm8750-iris), `clocks` (maxItems=6), `clock-names` (ordered-items=6; ordered iface, core, vcodec0_core, iface1, core_freerun, vcodec0_core_freerun), `dma-coherent`, `interconnects` (maxItems=2), `interconnect-names` (ordered-items=2; ordered cpu-cfg, video-mem), `iommus` (maxItems=2), `operating-points-v2`, `opp-table`, `power-domains` (maxItems=4), `power-domain-names` (ordered-items=4; ordered venus, vcodec0, mxc, mmcx), `resets` (maxItems=4), `reset-names` (ordered-items=4; ordered bus0, bus1, core, vcodec0_core).
- referenced schemas: qcom,venus-common.yaml#.
- Structural features: closed schema via `unevaluatedProperties: false`; 1 allOf composition block(s).
- Schema closure: unevaluatedProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- schema id: http://devicetree.org/schemas/media/qcom,sm8750-iris.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: qcom,venus-common.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, dma-coherent, interconnects, interconnect-names, iommus, power-domain-names, resets, reset-names`, optional top-level properties include `clocks, clock-names, operating-points-v2, opp-table, power-domains`, and compatible coverage is `qcom,sm8750-iris`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8750-iris.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: qcom,venus-common.yaml#.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,sm8750-iris.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,venus-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,venus-common.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,venus-common.yaml`, a video codec/accelerator devicetree binding. The schema title is `Qualcomm SoC Venus Video Encode and Decode Accelerators Common Properties`. Description signal from the file: The Venus IP is a video encode and decode accelerator present on Qualcomm platforms.

## Purpose
The file defines the devicetree ABI for `Qualcomm SoC Venus Video Encode and Decode Accelerators Common Properties`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- required node contract: reg, clocks, clock-names, interrupts, memory-region, power-domains.
- property surface: `reg` (maxItems=1), `clocks` (minItems=3, maxItems=7), `clock-names` (minItems=3, maxItems=7), `firmware-name` (maxItems=1), `interrupts` (maxItems=1), `iommus` (minItems=1, maxItems=20), `memory-region` (maxItems=1), `power-domains` (minItems=1, maxItems=4), `power-domain-names` (minItems=1, maxItems=4), `video-firmware` (Firmware subnode is needed when the platform does not have TrustZone.).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: inherits openness from composed references or leaves additional properties unconstrained where allowed.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file has no inline example block, so coverage depends on external DTS users and schemas that reference it.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. The `memory-region` property also persists reserved-memory relationships in the devicetree for firmware or DMA-visible buffers. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Stanimir Varbanov <stanimir.k.varbanov@gmail.com>, Vikash Garodia <quic_vgarodia@quicinc.com>.
- schema id: http://devicetree.org/schemas/media/qcom,venus-common.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `reg, clocks, clock-names, interrupts, memory-region, power-domains`, optional top-level properties include `firmware-name, iommus, power-domain-names, video-firmware`, and compatible coverage is `none declared`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,venus-common.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,venus-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,x1e80100-camss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,x1e80100-camss.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,x1e80100-camss.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Qualcomm X1E80100 Camera Subsystem (CAMSS)`. Description signal from the file: The CAMSS IP is a CSI decoder and ISP present on Qualcomm platforms..

## Purpose
The file defines the devicetree ABI for `Qualcomm X1E80100 Camera Subsystem (CAMSS)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: qcom,x1e80100-camss.
- required node contract: compatible, reg, reg-names, clocks, clock-names, interrupts, interrupt-names, interconnects, interconnect-names, iommus, power-domains, power-domain-names, vdd-csiphy-0p8-supply, vdd-csiphy-1p2-supply, and 1 more.
- property surface: `compatible` (const qcom,x1e80100-camss), `reg` (maxItems=17), `reg-names` (ordered-items=17; ordered csid0, csid1, csid2, csid_lite0, csid_lite1, csid_wrapper, csiphy0, csiphy1, and 9 more), `clocks` (maxItems=29), `clock-names` (ordered-items=29; ordered camnoc_nrt_axi, camnoc_rt_axi, core_ahb, cpas_ahb, cpas_fast_ahb, cpas_vfe0, cpas_vfe1, cpas_vfe_lite, and 21 more), `interrupts` (maxItems=13), `interrupt-names` (ordered-items=13; ordered csid0, csid1, csid2, csid_lite0, csid_lite1, csiphy0, csiphy1, csiphy2, and 5 more), `interconnects` (maxItems=4), `interconnect-names` (ordered-items=4; ordered ahb, hf_mnoc, sf_mnoc, sf_icp_mnoc), `iommus` (maxItems=8), `power-domains` (ordered-items=3), `power-domain-names` (ordered-items=3; ordered ife0, ife1, top), `vdd-csiphy-0p8-supply` (0.8V supply to a PHY.), `vdd-csiphy-1p2-supply` (1.2V supply to a PHY.), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. Regulator supply properties persist power-rail dependencies that board DTS files must wire correctly. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Bryan O'Donoghue <bryan.odonoghue@linaro.org>.
- schema id: http://devicetree.org/schemas/media/qcom,x1e80100-camss.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, reg-names, clocks, clock-names, interrupts, interrupt-names, interconnects, interconnect-names, iommus, power-domains, power-domain-names, vdd-csiphy-0p8-supply, vdd-csiphy-1p2-supply, and 1 more`, optional top-level properties include `none declared`, and compatible coverage is `qcom,x1e80100-camss`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,x1e80100-camss.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/qcom,x1e80100-camss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,pispbe.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,pispbe.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,pispbe.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Raspberry Pi PiSP Image Signal Processor (ISP) Back End`. Description signal from the file: The Raspberry Pi PiSP Image Signal Processor (ISP) Back End is an image processor that fetches images in Bayer or Grayscale format from DRAM memory in tiles and produces images consumable by applications. The full ISP documentation is available at https://datasheets.raspberrypi.com/camera/raspberry-pi-image-signal-processor-specification.pdf.

## Purpose
The file defines the devicetree ABI for `Raspberry Pi PiSP Image Signal Processor (ISP) Back End`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: brcm,bcm2712-pispbe, raspberrypi,pispbe.
- required node contract: compatible, reg, interrupts, clocks.
- property surface: `compatible` (ordered-items=2; ordered raspberrypi,pispbe), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `iommus` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Raspberry Pi Kernel Maintenance <kernel-list@raspberrypi.com>, Jacopo Mondi <jacopo.mondi@ideasonboard.com>.
- schema id: http://devicetree.org/schemas/media/raspberrypi,pispbe.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks`, optional top-level properties include `iommus`, and compatible coverage is `brcm,bcm2712-pispbe, raspberrypi,pispbe`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,pispbe.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,pispbe.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,rp1-cfe.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,rp1-cfe.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,rp1-cfe.yaml`, a devicetree binding schema. The schema title is `Raspberry Pi PiSP Camera Front End`. Description signal from the file: The Raspberry Pi PiSP Camera Front End is a module in Raspberrypi 5's RP1 I/O controller, that contains: - MIPI D-PHY - MIPI CSI-2 receiver - Simple image processor (called PiSP Front End, or FE) The FE documentation is available at: https://datasheets.raspberrypi.com/camera/raspberry-pi-image-signal-processor-specification.pdf The PHY and CSI-2 receiver part have no public documentation..

## Purpose
The file defines the devicetree ABI for `Raspberry Pi PiSP Camera Front End`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: raspberrypi,rp1-cfe.
- required node contract: compatible, reg, interrupts, clocks.
- property surface: `compatible` (ordered-items=1; ordered raspberrypi,rp1-cfe), `reg` (ordered-items=4), `interrupts` (maxItems=1), `clocks` (maxItems=1), `port` (ref /schemas/graph.yaml#/$defs/port-base).
- referenced schemas: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: single graph `port`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Tomi Valkeinen <tomi.valkeinen@ideasonboard.com>, Raspberry Pi Kernel Maintenance <kernel-list@raspberrypi.com>.
- schema id: http://devicetree.org/schemas/media/raspberrypi,rp1-cfe.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks`, optional top-level properties include `port`, and compatible coverage is `raspberrypi,rp1-cfe`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,rp1-cfe.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/raspberrypi,rp1-cfe.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rc.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rc.yaml`, a media ancillary controller devicetree binding. The schema title is `Generic Infrared Remote Controller`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `Generic Infrared Remote Controller`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- property surface: `$nodename`, `linux,rc-map-name` (ref /schemas/types.yaml#/definitions/string; enum rc-adstech-dvb-t-pci, rc-alink-dtu-m, rc-anysee, rc-apac-viewcomp, rc-astrometa-t2hybrid, rc-asus-pc39, rc-asus-ps3-100, rc-ati-tv-wonder-hd-600, and 132 more).
- referenced schemas: /schemas/types.yaml#/definitions/string.
- Structural features: no graph child-node or composition machinery beyond top-level property validation.
- Schema closure: inherits openness from composed references or leaves additional properties unconstrained where allowed.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file has no inline example block, so coverage depends on external DTS users and schemas that reference it.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Mauro Carvalho Chehab <mchehab@kernel.org>, Sean Young <sean@mess.org>.
- schema id: http://devicetree.org/schemas/media/rc.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/string.

## Risks And Edge Cases
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `none declared`, optional top-level properties include `$nodename, linux,rc-map-name`, and compatible coverage is `none declared`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rc.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/string.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,ceu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,ceu.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,ceu.yaml`, a devicetree binding schema. The schema title is `Renesas Capture Engine Unit (CEU)`. Description signal from the file: The Capture Engine Unit is the image capture interface found in the Renesas SH Mobile, R-Mobile and RZ SoCs. The interface supports a single parallel input with data bus width of 8 or 16 bits..

## Purpose
The file defines the devicetree ABI for `Renesas Capture Engine Unit (CEU)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r7s72100-ceu, renesas,r8a7740-ceu.
- required node contract: compatible, reg, interrupts, clocks, power-domains, port.
- property surface: `compatible` (enum renesas,r7s72100-ceu, renesas,r8a7740-ceu), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `power-domains` (maxItems=1), `port` (ref /schemas/graph.yaml#/$defs/port-base).
- referenced schemas: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: single graph `port`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Jacopo Mondi <jacopo+renesas@jmondi.org>, linux-renesas-soc@vger.kernel.org.
- schema id: http://devicetree.org/schemas/media/renesas,ceu.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, power-domains, port`, optional top-level properties include `none declared`, and compatible coverage is `renesas,r7s72100-ceu, renesas,r8a7740-ceu`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,ceu.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,ceu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,csi2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,csi2.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,csi2.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Renesas R-Car MIPI CSI-2 receiver`. Description signal from the file: The R-Car CSI-2 receiver device provides MIPI CSI-2 capabilities for the Renesas R-Car and RZ/G2 family of devices. It is used in conjunction with the R-Car VIN module, which provides the video capture capabilities..

## Purpose
The file defines the devicetree ABI for `Renesas R-Car MIPI CSI-2 receiver`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r8a774a1-csi2, renesas,r8a774b1-csi2, renesas,r8a774c0-csi2, renesas,r8a774e1-csi2, renesas,r8a7795-csi2, renesas,r8a7796-csi2, renesas,r8a77961-csi2, renesas,r8a77965-csi2, renesas,r8a77970-csi2, renesas,r8a77980-csi2, renesas,r8a77990-csi2, renesas,r8a779a0-csi2, renesas,r8a779g0-csi2, renesas,r8a779h0-csi2.
- required node contract: compatible, reg, interrupts, clocks, power-domains, resets, ports.
- property surface: `compatible` (ordered-items=1), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `power-domains` (maxItems=1), `resets` (maxItems=1), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Niklas Söderlund <niklas.soderlund@ragnatech.se>.
- schema id: http://devicetree.org/schemas/media/renesas,csi2.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, power-domains, resets, ports`, optional top-level properties include `none declared`, and compatible coverage is `renesas,r8a774a1-csi2, renesas,r8a774b1-csi2, renesas,r8a774c0-csi2, renesas,r8a774e1-csi2, renesas,r8a7795-csi2, renesas,r8a7796-csi2, renesas,r8a77961-csi2, renesas,r8a77965-csi2, renesas,r8a77970-csi2, renesas,r8a77980-csi2, renesas,r8a77990-csi2, renesas,r8a779a0-csi2, renesas,r8a779g0-csi2, renesas,r8a779h0-csi2`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,csi2.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,csi2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,drif.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,drif.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,drif.yaml`, a media ancillary controller devicetree binding. The schema title is `Renesas R-Car Gen3 Digital Radio Interface Controller (DRIF)`. Description signal from the file: R-Car Gen3 DRIF is a SPI like receive only slave device. A general representation of DRIF interfacing with a master device is shown below. +---------------------+ +---------------------+ | |-----SCK------->|CLK | | Master |-----SS-------->|SYNC DRIFn (slave) | | |-----SD0------->|D0 | | |-----SD1------->|D1 | +---------------------+ +---------------------+ As per datasheet, each DRIF channel (drifn) is made up of two.

## Purpose
The file defines the devicetree ABI for `Renesas R-Car Gen3 Digital Radio Interface Controller (DRIF)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r8a7795-drif, renesas,r8a7796-drif, renesas,r8a77965-drif, renesas,r8a77990-drif, renesas,rcar-gen3-drif.
- required node contract: compatible, reg, interrupts, clocks, clock-names, resets, dmas, dma-names, renesas,bonding, power-domains.
- property surface: `compatible` (ordered-items=2; ordered renesas,rcar-gen3-drif), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `clock-names` (const fck), `resets` (maxItems=1), `dmas` (minItems=1, maxItems=2), `dma-names` (minItems=1, ordered-items=2; ordered rx, rx), `renesas,bonding` (ref /schemas/types.yaml#/definitions/phandle), `power-domains` (maxItems=1), `renesas,primary-bond` (Indicates that the channel acts as primary among the bonded channels.), `port` (ref /schemas/graph.yaml#/$defs/port-base).
- referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/$defs/port-base, /schemas/graph.yaml#/$defs/endpoint-base, /schemas/types.yaml#/definitions/uint32.
- Structural features: single graph `port`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 2 allOf composition block(s); 2 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 2 conditional site(s): allOf[0], allOf[1]. The file includes 2 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. DMA channel properties persist the binding between the hardware block and the DMA engine channels it relies on.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Ramesh Shanmugasundaram <rashanmu@gmail.com>, Fabrizio Castro <fabrizio.castro.jz@renesas.com>.
- schema id: http://devicetree.org/schemas/media/renesas,drif.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/$defs/port-base, /schemas/graph.yaml#/$defs/endpoint-base, /schemas/types.yaml#/definitions/uint32.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, resets, dmas, dma-names, renesas,bonding, power-domains`, optional top-level properties include `renesas,primary-bond, port`, and compatible coverage is `renesas,r8a7795-drif, renesas,r8a7796-drif, renesas,r8a77965-drif, renesas,r8a77990-drif, renesas,rcar-gen3-drif`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,drif.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/$defs/port-base, /schemas/graph.yaml#/$defs/endpoint-base, /schemas/types.yaml#/definitions/uint32.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,drif.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fcp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fcp.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fcp.yaml`, a devicetree binding schema. The schema title is `Renesas R-Car Frame Compression Processor (FCP)`. Description signal from the file: The FCP is a companion module of video processing modules in the Renesas R-Car Gen3 and RZ/G2 SoCs. It provides data compression and decompression, data caching, and conversion of AXI transactions in order to reduce the memory bandwidth. There are three types of FCP: FCP for Codec (FCPC), FCP for VSP (FCPV) and FCP for FDP (FCPF). Their configuration and behaviour depend on the module they are paired with. These DT b.

## Purpose
The file defines the devicetree ABI for `Renesas R-Car Frame Compression Processor (FCP)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,fcpv, renesas,fcpf, renesas,r9a07g043u-fcpvd, renesas,r9a07g044-fcpvd, renesas,r9a07g054-fcpvd, renesas,r9a09g056-fcpvd, renesas,r9a09g057-fcpvd.
- required node contract: compatible, reg, clocks, power-domains, resets.
- property surface: `compatible`, `reg` (maxItems=1), `clocks` (minItems=1, ordered-items=3), `clock-names` (ordered-items=3; ordered aclk, pclk, vclk), `iommus` (maxItems=1), `power-domains` (maxItems=1), `resets` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`; 1 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Laurent Pinchart <laurent.pinchart@ideasonboard.com>.
- schema id: http://devicetree.org/schemas/media/renesas,fcp.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, clocks, power-domains, resets`, optional top-level properties include `clock-names, iommus`, and compatible coverage is `renesas,fcpv, renesas,fcpf, renesas,r9a07g043u-fcpvd, renesas,r9a07g044-fcpvd, renesas,r9a07g054-fcpvd, renesas,r9a09g056-fcpvd, renesas,r9a09g057-fcpvd`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fcp.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fcp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fdp1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fdp1.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fdp1.yaml`, a devicetree binding schema. The schema title is `Renesas R-Car Fine Display Processor (FDP1)`. Description signal from the file: The FDP1 is a de-interlacing module which converts interlaced video to progressive video. It is capable of performing pixel format conversion between YCbCr/YUV formats and RGB formats. Only YCbCr/YUV formats are supported as an input to the module..

## Purpose
The file defines the devicetree ABI for `Renesas R-Car Fine Display Processor (FDP1)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,fdp1.
- required node contract: compatible, reg, interrupts, clocks, power-domains, resets.
- property surface: `compatible` (enum renesas,fdp1), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `power-domains` (maxItems=1), `resets` (maxItems=1), `renesas,fcp` (ref /schemas/types.yaml#/definitions/phandle).
- referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Laurent Pinchart <laurent.pinchart@ideasonboard.com>.
- schema id: http://devicetree.org/schemas/media/renesas,fdp1.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, power-domains, resets`, optional top-level properties include `renesas,fcp`, and compatible coverage is `renesas,fdp1`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fdp1.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,fdp1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,imr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,imr.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,imr.yaml`, a devicetree binding schema. The schema title is `Renesas R-Car Image Renderer (Distortion Correction Engine)`. Description signal from the file: The image renderer, or the distortion correction engine, is a drawing processor with a simple instruction system capable of referencing video capture data or data in an external memory as 2D texture data and performing texture mapping and drawing with respect to any shape that is split into triangular objects. The image renderer light extended 4 (IMR-LX4) is found in R-Car Gen3 SoCs..

## Purpose
The file defines the devicetree ABI for `Renesas R-Car Image Renderer (Distortion Correction Engine)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r8a7795-imr-lx4, renesas,r8a7796-imr-lx4, renesas,imr-lx4.
- required node contract: compatible, reg, interrupts, clocks, power-domains, resets.
- property surface: `compatible` (ordered-items=2; ordered renesas,imr-lx4), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `power-domains` (maxItems=1), `resets` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Sergei Shtylyov <sergei.shtylyov@gmail.com>.
- schema id: http://devicetree.org/schemas/media/renesas,imr.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, power-domains, resets`, optional top-level properties include `none declared`, and compatible coverage is `renesas,r8a7795-imr-lx4, renesas,r8a7796-imr-lx4, renesas,imr-lx4`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,imr.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,imr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,isp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,isp.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,isp.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Renesas R-Car ISP Channel Selector`. Description signal from the file: The R-Car ISP Channel Selector provides MIPI CSI-2 VC and DT filtering capabilities for the Renesas R-Car family of devices. It is used in conjunction with the R-Car VIN and CSI-2 modules, which provides the video capture capabilities..

## Purpose
The file defines the devicetree ABI for `Renesas R-Car ISP Channel Selector`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r8a779a0-isp, renesas,r8a779g0-isp, renesas,r8a779h0-isp, renesas,rcar-gen4-isp.
- required node contract: compatible, reg, reg-names, interrupts, interrupt-names, clocks, clock-names, power-domains, resets, reset-names, ports.
- property surface: `compatible` (ordered-items=2; ordered renesas,rcar-gen4-isp), `reg` (minItems=1, maxItems=2), `reg-names` (minItems=1, ordered-items=2; ordered cs, core), `interrupts` (minItems=1, maxItems=2), `interrupt-names` (minItems=1, ordered-items=2; ordered cs, core), `clocks` (minItems=1, maxItems=2), `clock-names` (minItems=1, ordered-items=2; ordered cs, core), `power-domains` (maxItems=1), `resets` (minItems=1, maxItems=2), `reset-names` (minItems=1, ordered-items=2; ordered cs, core), `renesas,vspx` (ref /schemas/types.yaml#/definitions/phandle), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Niklas Söderlund <niklas.soderlund@ragnatech.se>.
- schema id: http://devicetree.org/schemas/media/renesas,isp.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, reg-names, interrupts, interrupt-names, clocks, clock-names, power-domains, resets, reset-names, ports`, optional top-level properties include `renesas,vspx`, and compatible coverage is `renesas,r8a779a0-isp, renesas,r8a779g0-isp, renesas,r8a779h0-isp, renesas,rcar-gen4-isp`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,isp.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,isp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,jpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,jpu.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,jpu.yaml`, a devicetree binding schema. The schema title is `Renesas JPEG Processing Unit`. Description signal from the file: The JPEG processing unit (JPU) incorporates the JPEG codec with an encoding and decoding function conforming to the JPEG baseline process, so that the JPU can encode image data and decode JPEG data quickly..

## Purpose
The file defines the devicetree ABI for `Renesas JPEG Processing Unit`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,jpu-r8a7790, renesas,jpu-r8a7791, renesas,jpu-r8a7792, renesas,jpu-r8a7793, renesas,rcar-gen2-jpu.
- required node contract: compatible, reg, interrupts, clocks, power-domains, resets.
- property surface: `compatible` (ordered-items=2; ordered renesas,rcar-gen2-jpu), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `power-domains` (maxItems=1), `resets` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Mikhail Ulyanov <mikhail.ulyanov@cogentembedded.com>.
- schema id: http://devicetree.org/schemas/media/renesas,jpu.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, power-domains, resets`, optional top-level properties include `none declared`, and compatible coverage is `renesas,jpu-r8a7790, renesas,jpu-r8a7791, renesas,jpu-r8a7792, renesas,jpu-r8a7793, renesas,rcar-gen2-jpu`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,jpu.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,jpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,r9a09g057-ivc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,r9a09g057-ivc.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,r9a09g057-ivc.yaml`, a devicetree binding schema. The schema title is `Renesas RZ/V2H(P) Input Video Control Block`. Description signal from the file: The IVC block is a module that takes video frames from memory and feeds them to the Image Signal Processor for processing..

## Purpose
The file defines the devicetree ABI for `Renesas RZ/V2H(P) Input Video Control Block`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r9a09g057-ivc.
- required node contract: compatible, reg, interrupts, clocks, clock-names, power-domains, resets, reset-names, port.
- property surface: `compatible` (const renesas,r9a09g057-ivc), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (ordered-items=3), `clock-names` (ordered-items=3; ordered reg, axi, isp), `power-domains` (maxItems=1), `resets` (ordered-items=3), `reset-names` (ordered-items=3; ordered reg, axi, isp), `port` (ref /schemas/graph.yaml#/properties/port).
- referenced schemas: /schemas/graph.yaml#/properties/port, /schemas/graph.yaml#/properties/endpoint.
- Structural features: single graph `port`; endpoint subnodes; closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Daniel Scally <dan.scally@ideasonboard.com>.
- schema id: http://devicetree.org/schemas/media/renesas,r9a09g057-ivc.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/port, /schemas/graph.yaml#/properties/endpoint.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, power-domains, resets, reset-names, port`, optional top-level properties include `none declared`, and compatible coverage is `renesas,r9a09g057-ivc`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,r9a09g057-ivc.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/port, /schemas/graph.yaml#/properties/endpoint.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,r9a09g057-ivc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-cru.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-cru.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-cru.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Renesas RZ/G2L (and alike SoC's) Camera Data Receiving Unit (CRU) Image processing`. Description signal from the file: The CRU image processing module is a data conversion module equipped with pixel color space conversion, LUT, pixel format conversion, etc. An MIPI CSI-2 input and parallel (including ITU-R BT.656) input are provided as the image sensor interface..

## Purpose
The file defines the devicetree ABI for `Renesas RZ/G2L (and alike SoC's) Camera Data Receiving Unit (CRU) Image processing`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r9a07g043-cru, renesas,r9a07g044-cru, renesas,r9a07g054-cru, renesas,rzg2l-cru, renesas,r9a09g047-cru.
- required node contract: compatible, reg, interrupts, interrupt-names, clocks, clock-names, resets, reset-names, power-domains.
- property surface: `compatible`, `reg` (maxItems=1), `interrupts`, `interrupt-names`, `clocks` (ordered-items=3), `clock-names` (ordered-items=3; ordered video, apb, axi), `power-domains` (maxItems=1), `resets` (ordered-items=2), `reset-names` (ordered-items=2; ordered presetn, aresetn), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 3 allOf composition block(s); 3 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 3 conditional site(s): allOf[0], allOf[1], allOf[2]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Lad Prabhakar <prabhakar.mahadev-lad.rj@bp.renesas.com>.
- schema id: http://devicetree.org/schemas/media/renesas,rzg2l-cru.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, interrupt-names, clocks, clock-names, resets, reset-names, power-domains`, optional top-level properties include `ports`, and compatible coverage is `renesas,r9a07g043-cru, renesas,r9a07g044-cru, renesas,r9a07g054-cru, renesas,rzg2l-cru, renesas,r9a09g047-cru`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-cru.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-cru.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-csi2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-csi2.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-csi2.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Renesas RZ/G2L (and alike SoC's) MIPI CSI-2 receiver`. Description signal from the file: The CSI-2 receiver device provides MIPI CSI-2 capabilities for the Renesas RZ/G2L (and alike SoCs). MIPI CSI-2 is part of the CRU block which is used in conjunction with the Image Processing module, which provides the video capture capabilities..

## Purpose
The file defines the devicetree ABI for `Renesas RZ/G2L (and alike SoC's) MIPI CSI-2 receiver`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r9a07g043-csi2, renesas,r9a07g044-csi2, renesas,r9a07g054-csi2, renesas,rzg2l-csi2, renesas,r9a09g047-csi2, renesas,r9a09g057-csi2.
- required node contract: compatible, reg, interrupts, clocks, clock-names, power-domains, resets, reset-names, ports.
- property surface: `compatible`, `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks`, `clock-names`, `power-domains` (maxItems=1), `resets` (ordered-items=2), `reset-names` (ordered-items=2; ordered presetn, cmn-rstb), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 1 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Lad Prabhakar <prabhakar.mahadev-lad.rj@bp.renesas.com>.
- schema id: http://devicetree.org/schemas/media/renesas,rzg2l-csi2.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, power-domains, resets, reset-names, ports`, optional top-level properties include `none declared`, and compatible coverage is `renesas,r9a07g043-csi2, renesas,r9a07g044-csi2, renesas,r9a07g054-csi2, renesas,rzg2l-csi2, renesas,r9a09g047-csi2, renesas,r9a09g057-csi2`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-csi2.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,rzg2l-csi2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,vin.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,vin.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,vin.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Renesas R-Car Video Input (VIN)`. Description signal from the file: The R-Car Video Input (VIN) device provides video input capabilities for the Renesas R-Car family of devices. Each VIN instance has a single parallel input that supports RGB and YUV video, with both external synchronization and BT.656 synchronization for the latter. Depending on the instance the VIN input is connected to external SoC pins, or on Gen3 and RZ/G2 platforms to a CSI-2 receiver..

## Purpose
The file defines the devicetree ABI for `Renesas R-Car Video Input (VIN)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,vin-r8a7742, renesas,vin-r8a7743, renesas,vin-r8a7744, renesas,vin-r8a7745, renesas,vin-r8a77470, renesas,vin-r8a7790, renesas,vin-r8a7791, renesas,vin-r8a7792, renesas,vin-r8a7793, renesas,vin-r8a7794, renesas,rcar-gen2-vin, renesas,vin-r8a774a1, renesas,vin-r8a774b1, renesas,vin-r8a774c0, renesas,vin-r8a774e1, renesas,vin-r8a7778, and 13 more.
- required node contract: compatible, reg, interrupts, clocks, power-domains.
- property surface: `compatible`, `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `power-domains` (maxItems=1), `resets` (maxItems=1), `port` (ref /schemas/graph.yaml#/$defs/port-base), `renesas,id` (ref /schemas/types.yaml#/definitions/uint32; minimum=0, maximum=31), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port, /schemas/graph.yaml#/properties/endpoint.
- Structural features: multi-port graph container `ports`; single graph `port`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 2 allOf composition block(s); 2 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 2 conditional site(s): allOf[0], allOf[1]. The file includes 3 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Niklas Söderlund <niklas.soderlund@ragnatech.se>.
- schema id: http://devicetree.org/schemas/media/renesas,vin.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port, /schemas/graph.yaml#/properties/endpoint.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, power-domains`, optional top-level properties include `resets, port, renesas,id, ports`, and compatible coverage is `renesas,vin-r8a7742, renesas,vin-r8a7743, renesas,vin-r8a7744, renesas,vin-r8a7745, renesas,vin-r8a77470, renesas,vin-r8a7790, renesas,vin-r8a7791, renesas,vin-r8a7792, renesas,vin-r8a7793, renesas,vin-r8a7794, renesas,rcar-gen2-vin, renesas,vin-r8a774a1, renesas,vin-r8a774b1, renesas,vin-r8a774c0, renesas,vin-r8a774e1, renesas,vin-r8a7778, and 13 more`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,vin.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port, /schemas/graph.yaml#/properties/endpoint.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,vin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,vsp1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,vsp1.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,vsp1.yaml`, a devicetree binding schema. The schema title is `Renesas VSP Video Processing Engine`. Description signal from the file: The VSP is a video processing engine that supports up-/down-scaling, alpha blending, color space conversion and various other image processing features. It can be found in the Renesas R-Car Gen2, R-Car Gen3, RZ/G1, and RZ/G2 SoCs..

## Purpose
The file defines the devicetree ABI for `Renesas VSP Video Processing Engine`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: renesas,r9a07g044-vsp2, renesas,vsp1, renesas,vsp2, renesas,r9a07g043u-vsp2, renesas,r9a07g054-vsp2, renesas,r9a09g056-vsp2, renesas,r9a09g057-vsp2.
- required node contract: compatible, reg, interrupts, clocks, power-domains, resets.
- property surface: `compatible`, `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (minItems=1, ordered-items=3), `clock-names` (ordered-items=3; ordered aclk, pclk, vclk), `power-domains` (maxItems=1), `resets` (maxItems=1), `renesas,fcp` (ref /schemas/types.yaml#/definitions/phandle).
- referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Structural features: closed schema via `additionalProperties: false`; 2 allOf composition block(s); 2 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 2 conditional site(s): allOf[0], allOf[1]. The file includes 2 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Laurent Pinchart <laurent.pinchart@ideasonboard.com>.
- schema id: http://devicetree.org/schemas/media/renesas,vsp1.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, power-domains, resets`, optional top-level properties include `clock-names, renesas,fcp`, and compatible coverage is `renesas,r9a07g044-vsp2, renesas,vsp1, renesas,vsp2, renesas,r9a07g043u-vsp2, renesas,r9a07g054-vsp2, renesas,r9a09g056-vsp2, renesas,r9a09g057-vsp2`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,vsp1.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/renesas,vsp1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,px30-vip.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,px30-vip.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,px30-vip.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Rockchip PX30 Video Input Processor (VIP)`. Description signal from the file: The Rockchip PX30 Video Input Processor (VIP) receives the data from a camera sensor or CCIR656 encoder and transfers it into system main memory by AXI bus..

## Purpose
The file defines the devicetree ABI for `Rockchip PX30 Video Input Processor (VIP)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: rockchip,px30-vip.
- required node contract: compatible, reg, interrupts, clocks, ports.
- property surface: `compatible` (const rockchip,px30-vip), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (ordered-items=3), `clock-names` (ordered-items=3; ordered aclk, hclk, pclk), `resets` (ordered-items=3), `reset-names` (ordered-items=3; ordered axi, ahb, pclkin), `power-domains` (maxItems=1), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Mehdi Djait <mehdi.djait@linux.intel.com>, Michael Riesch <michael.riesch@collabora.com>.
- schema id: http://devicetree.org/schemas/media/rockchip,px30-vip.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, ports`, optional top-level properties include `clock-names, resets, reset-names, power-domains`, and compatible coverage is `rockchip,px30-vip`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,px30-vip.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,px30-vip.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-mipi-csi2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-mipi-csi2.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-mipi-csi2.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Rockchip MIPI CSI-2 Receiver`. Description signal from the file: The Rockchip MIPI CSI-2 Receiver is a CSI-2 bridge with one input port and one output port. It receives the data with the help of an external MIPI PHY (C-PHY or D-PHY) and passes it to the Rockchip Video Capture (VICAP) block..

## Purpose
The file defines the devicetree ABI for `Rockchip MIPI CSI-2 Receiver`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: fsl,imx93-mipi-csi2, rockchip,rk3568-mipi-csi2.
- required node contract: compatible, reg, clocks, phys, ports, power-domains.
- property surface: `compatible` (enum fsl,imx93-mipi-csi2, rockchip,rk3568-mipi-csi2), `reg` (maxItems=1), `interrupts` (minItems=1, ordered-items=2), `interrupt-names` (minItems=1, ordered-items=2; ordered err1, err2), `clocks` (minItems=1, maxItems=2), `clock-names` (minItems=1, ordered-items=2; ordered per, pixel), `phys` (maxItems=1), `ports` (ref /schemas/graph.yaml#/properties/ports), `power-domains` (maxItems=1), `resets` (maxItems=1).
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 2 allOf composition block(s); 2 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 2 conditional site(s): allOf[0], allOf[1]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Michael Riesch <michael.riesch@collabora.com>.
- schema id: http://devicetree.org/schemas/media/rockchip,rk3568-mipi-csi2.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, clocks, phys, ports, power-domains`, optional top-level properties include `interrupts, interrupt-names, clock-names, resets`, and compatible coverage is `fsl,imx93-mipi-csi2, rockchip,rk3568-mipi-csi2`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-mipi-csi2.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-mipi-csi2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-vepu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-vepu.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-vepu.yaml`, a video codec/accelerator devicetree binding. The schema title is `Hantro G1 VPU encoders implemented on Rockchip SoCs`. Description signal from the file: Hantro G1 video encode-only accelerators present on Rockchip SoCs..

## Purpose
The file defines the devicetree ABI for `Hantro G1 VPU encoders implemented on Rockchip SoCs`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: rockchip,rk3568-vepu, rockchip,rk3588-vepu121.
- required node contract: compatible, reg, interrupts, clocks, clock-names.
- property surface: `compatible` (enum rockchip,rk3568-vepu, rockchip,rk3588-vepu121), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=2), `clock-names` (ordered-items=2; ordered aclk, hclk), `power-domains` (maxItems=1), `iommus` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Nicolas Frattaroli <frattaroli.nicolas@gmail.com>.
- schema id: http://devicetree.org/schemas/media/rockchip,rk3568-vepu.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names`, optional top-level properties include `power-domains, iommus`, and compatible coverage is `rockchip,rk3568-vepu, rockchip,rk3588-vepu121`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-vepu.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-vepu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-vicap.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-vicap.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-vicap.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Rockchip RK3568 Video Capture (VICAP)`. Description signal from the file: The Rockchip RK3568 Video Capture (VICAP) block features a digital video port (DVP, a parallel video interface) and a MIPI CSI-2 port. It receives the data from camera sensors, video decoders, or other companion ICs and transfers it into system main memory by AXI bus..

## Purpose
The file defines the devicetree ABI for `Rockchip RK3568 Video Capture (VICAP)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: rockchip,rk3568-vicap.
- required node contract: compatible, reg, interrupts, clocks, ports.
- property surface: `compatible` (const rockchip,rk3568-vicap), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (ordered-items=4), `clock-names` (ordered-items=4; ordered aclk, hclk, dclk, iclk), `iommus` (maxItems=1), `resets` (ordered-items=5), `reset-names` (ordered-items=5; ordered arst, hrst, drst, prst, irst), `rockchip,grf` (ref /schemas/types.yaml#/definitions/phandle), `power-domains` (maxItems=1), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Michael Riesch <michael.riesch@collabora.com>.
- schema id: http://devicetree.org/schemas/media/rockchip,rk3568-vicap.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/port.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, ports`, optional top-level properties include `clock-names, iommus, resets, reset-names, rockchip,grf, power-domains`, and compatible coverage is `rockchip,rk3568-vicap`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-vicap.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,rk3568-vicap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,vdec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,vdec.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,vdec.yaml`, a video codec/accelerator devicetree binding. The schema title is `Rockchip Video Decoder (VDec)`. Description signal from the file: Rockchip SoCs have variants of the same stateless Video Decoder that can decodes H.264, HEVC, VP9 and AV1 streams, depending on the variant..

## Purpose
The file defines the devicetree ABI for `Rockchip Video Decoder (VDec)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: rockchip,rk3288-vdec, rockchip,rk3399-vdec, rockchip,rk3576-vdec, rockchip,rk3588-vdec, rockchip,rk3228-vdec, rockchip,rk3328-vdec.
- required node contract: compatible, reg, interrupts, clocks, clock-names, power-domains.
- property surface: `compatible`, `reg` (minItems=1, maxItems=3), `reg-names`, `interrupts` (maxItems=1), `clocks` (minItems=4, ordered-items=5), `clock-names` (minItems=4, ordered-items=5; ordered axi, ahb, cabac, core, hevc_cabac), `assigned-clocks`, `assigned-clock-rates`, `resets` (ordered-items=5), `reset-names` (ordered-items=5; ordered axi, ahb, cabac, core, hevc_cabac), `power-domains` (maxItems=1), `iommus` (maxItems=1), `sram` (ref /schemas/types.yaml#/definitions/phandle).
- referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Structural features: closed schema via `additionalProperties: false`; 1 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Heiko Stuebner <heiko@sntech.de>.
- schema id: http://devicetree.org/schemas/media/rockchip,vdec.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, power-domains`, optional top-level properties include `reg-names, assigned-clocks, assigned-clock-rates, resets, reset-names, iommus, sram`, and compatible coverage is `rockchip,rk3288-vdec, rockchip,rk3399-vdec, rockchip,rk3576-vdec, rockchip,rk3588-vdec, rockchip,rk3228-vdec, rockchip,rk3328-vdec`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,vdec.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip,vdec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-isp1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-isp1.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-isp1.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Rockchip SoC Image Signal Processing unit v1`. Description signal from the file: Rockchip ISP1 is the Camera interface for the Rockchip series of SoCs which contains image processing, scaling, and compression functions..

## Purpose
The file defines the devicetree ABI for `Rockchip SoC Image Signal Processing unit v1`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: fsl,imx8mp-isp, rockchip,px30-cif-isp, rockchip,rk3399-cif-isp.
- required node contract: compatible, reg, interrupts, clocks, clock-names, power-domains, ports.
- property surface: `compatible` (enum fsl,imx8mp-isp, rockchip,px30-cif-isp, rockchip,rk3399-cif-isp), `reg` (maxItems=1), `interrupts` (minItems=1, maxItems=3), `interrupt-names` (ordered-items=3; ordered isp, mi, mipi), `clocks` (minItems=3, ordered-items=4), `clock-names` (minItems=3, ordered-items=4; ordered isp, aclk, hclk, pclk), `fsl,blk-ctrl` (ref /schemas/types.yaml#/definitions/phandle-array; maxItems=1), `iommus` (maxItems=1), `phys` (maxItems=1), `phy-names` (const dphy), `power-domains` (minItems=1, ordered-items=2), `power-domain-names` (minItems=1, ordered-items=2; ordered isp, csi2), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 3 allOf composition block(s); 3 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 3 conditional site(s): allOf[0], allOf[1], allOf[2]. The file includes 2 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Helen Koike <helen.koike@collabora.com>.
- schema id: http://devicetree.org/schemas/media/rockchip-isp1.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, power-domains, ports`, optional top-level properties include `interrupt-names, fsl,blk-ctrl, iommus, phys, phy-names, power-domain-names`, and compatible coverage is `fsl,imx8mp-isp, rockchip,px30-cif-isp, rockchip,rk3399-cif-isp`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-isp1.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-isp1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-rga.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-rga.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-rga.yaml`, a devicetree binding schema. The schema title is `Rockchip 2D raster graphic acceleration controller (RGA)`. Description signal from the file: RGA is a standalone 2D raster graphic acceleration unit. It accelerates 2D graphics operations, such as point/line drawing, image scaling, rotation, BitBLT, alpha blending and image blur/sharpness..

## Purpose
The file defines the devicetree ABI for `Rockchip 2D raster graphic acceleration controller (RGA)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: rockchip,rk3288-rga, rockchip,rk3399-rga, rockchip,rk3228-rga, rockchip,rk3568-rga, rockchip,rk3588-rga.
- required node contract: compatible, reg, interrupts, clocks, clock-names, resets, reset-names.
- property surface: `compatible`, `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=3), `clock-names` (ordered-items=3; ordered aclk, hclk, sclk), `power-domains` (maxItems=1), `resets` (maxItems=3), `reset-names` (ordered-items=3; ordered core, axi, ahb).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Jacob Chen <jacob-chen@iotwrt.com>, Ezequiel Garcia <ezequiel@collabora.com>.
- schema id: http://devicetree.org/schemas/media/rockchip-rga.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, resets, reset-names`, optional top-level properties include `power-domains`, and compatible coverage is `rockchip,rk3288-rga, rockchip,rk3399-rga, rockchip,rk3228-rga, rockchip,rk3568-rga, rockchip,rk3588-rga`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-rga.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-rga.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-vpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-vpu.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-vpu.yaml`, a video codec/accelerator devicetree binding. The schema title is `Hantro G1 VPU codecs implemented on Rockchip SoCs`. Description signal from the file: Hantro G1 video encode and decode accelerators present on Rockchip SoCs..

## Purpose
The file defines the devicetree ABI for `Hantro G1 VPU codecs implemented on Rockchip SoCs`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: rockchip,rk3036-vpu, rockchip,rk3066-vpu, rockchip,rk3288-vpu, rockchip,rk3328-vpu, rockchip,rk3399-vpu, rockchip,px30-vpu, rockchip,rk3568-vpu, rockchip,rk3588-av1-vpu, rockchip,rk3128-vpu, rockchip,rk3188-vpu, rockchip,rk3228-vpu, rockchip,rk3588-vpu121.
- required node contract: compatible, reg, interrupts, interrupt-names, clocks, clock-names.
- property surface: `compatible`, `reg` (maxItems=1), `interrupts` (minItems=1, maxItems=2), `interrupt-names`, `clocks`, `clock-names`, `power-domains` (maxItems=1), `iommus` (maxItems=1), `resets` (ordered-items=4).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Ezequiel Garcia <ezequiel@collabora.com>.
- schema id: http://devicetree.org/schemas/media/rockchip-vpu.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, interrupt-names, clocks, clock-names`, optional top-level properties include `power-domains, iommus, resets`, and compatible coverage is `rockchip,rk3036-vpu, rockchip,rk3066-vpu, rockchip,rk3288-vpu, rockchip,rk3328-vpu, rockchip,rk3399-vpu, rockchip,px30-vpu, rockchip,rk3568-vpu, rockchip,rk3588-av1-vpu, rockchip,rk3128-vpu, rockchip,rk3188-vpu, rockchip,rk3228-vpu, rockchip,rk3588-vpu121`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-vpu.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/rockchip-vpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-csis.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-csis.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-csis.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Samsung S5P/Exynos SoC series MIPI CSI-2 receiver (MIPI CSIS)`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `Samsung S5P/Exynos SoC series MIPI CSI-2 receiver (MIPI CSIS)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,s5pv210-csis, samsung,exynos4210-csis, samsung,exynos4212-csis, samsung,exynos5250-csis.
- required node contract: compatible, reg, bus-width, clocks, clock-names, interrupts, vddio-supply, vddcore-supply.
- property surface: `compatible` (enum samsung,s5pv210-csis, samsung,exynos4210-csis, samsung,exynos4212-csis, samsung,exynos5250-csis), `reg` (maxItems=1), `#address-cells` (const 1), `#size-cells` (const 0), `bus-width` (ref /schemas/types.yaml#/definitions/uint32; enum 2, 4), `clocks` (maxItems=2), `clock-names` (ordered-items=2; ordered csis, sclk_csis), `clock-frequency` (The IP's main (system bus) clock frequency in Hz.), `interrupts` (maxItems=1), `phys` (maxItems=1), `phy-names` (ordered-items=1; ordered csis), `power-domains` (maxItems=1), `vddio-supply` (MIPI CSIS I/O and PLL voltage supply (e.g. 1.8V).), `vddcore-supply` (MIPI CSIS Core voltage supply (e.g. 1.1V).).
- child-node patterns: ^port@[34]$.
- referenced schemas: /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: endpoint subnodes; patternProperties: ^port@[34]$; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 1 allOf composition block(s); 2 anyOf branch(es); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. Regulator supply properties persist power-rail dependencies that board DTS files must wire correctly.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,exynos4210-csis.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- pattern children: ^port@[34]$.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, bus-width, clocks, clock-names, interrupts, vddio-supply, vddcore-supply`, optional top-level properties include `#address-cells, #size-cells, clock-frequency, phys, phy-names, power-domains`, and compatible coverage is `samsung,s5pv210-csis, samsung,exynos4210-csis, samsung,exynos4212-csis, samsung,exynos5250-csis`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-csis.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-csis.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-fimc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-fimc.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-fimc.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Samsung S5P/Exynos SoC Fully Integrated Mobile Camera`. Description signal from the file: Each FIMC device should have an alias in the aliases node, in the form of fimc<n>, where <n> is an integer specifying the IP block instance..

## Purpose
The file defines the devicetree ABI for `Samsung S5P/Exynos SoC Fully Integrated Mobile Camera`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,exynos4210-fimc, samsung,exynos4212-fimc, samsung,s5pv210-fimc.
- required node contract: compatible, reg, clocks, clock-names, samsung,pix-limits.
- property surface: `compatible` (enum samsung,exynos4210-fimc, samsung,exynos4212-fimc, samsung,s5pv210-fimc), `reg` (maxItems=1), `clocks` (maxItems=2), `clock-names` (ordered-items=2; ordered fimc, sclk_fimc), `clock-frequency` (Maximum FIMC local clock (LCLK) frequency.), `interrupts` (maxItems=1), `iommus` (maxItems=1), `power-domains` (maxItems=1), `samsung,cam-if` (The FIMC IP block includes the camera input interface.), `samsung,isp-wb` (The FIMC IP block has the ISP writeback input.), `samsung,lcd-wb` (The FIMC IP block has the LCD writeback input.), `samsung,mainscaler-ext` (FIMC IP supports extended image size and has CIEXTEN register.), `samsung,min-pix-alignment` (ref /schemas/types.yaml#/definitions/uint32-array; ordered-items=2), `samsung,min-pix-sizes` (ref /schemas/types.yaml#/definitions/uint32-array; maxItems=2), `samsung,pix-limits` (ref /schemas/types.yaml#/definitions/uint32-array; maxItems=4), `samsung,rotators` (ref /schemas/types.yaml#/definitions/uint32), and 1 more.
- referenced schemas: /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/phandle.
- Structural features: closed schema via `additionalProperties: false`; 1 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,exynos4210-fimc.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/phandle.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, clocks, clock-names, samsung,pix-limits`, optional top-level properties include `clock-frequency, interrupts, iommus, power-domains, samsung,cam-if, samsung,isp-wb, samsung,lcd-wb, samsung,mainscaler-ext, samsung,min-pix-alignment, samsung,min-pix-sizes, samsung,rotators, samsung,sysreg`, and compatible coverage is `samsung,exynos4210-fimc, samsung,exynos4212-fimc, samsung,s5pv210-fimc`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-fimc.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/phandle.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4210-fimc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-is.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-is.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-is.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Samsung Exynos4212/4412 SoC Imaging Subsystem (FIMC-IS)`. Description signal from the file: The FIMC-IS is a subsystem for processing image signal from an image sensor. The Exynos4x12 SoC series FIMC-IS V1.5 comprises of a dedicated ARM Cortex-A5 processor, ISP, DRC and FD IP blocks and peripheral devices such as UART, I2C and SPI bus controllers, PWM and ADC..

## Purpose
The file defines the devicetree ABI for `Samsung Exynos4212/4412 SoC Imaging Subsystem (FIMC-IS)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,exynos4212-fimc-is.
- required node contract: compatible, reg, #address-cells, clocks, clock-names, interrupts, ranges, samsung,pmu-syscon, #size-cells.
- property surface: `compatible` (enum samsung,exynos4212-fimc-is), `reg` (maxItems=1), `ranges`, `#address-cells` (const 1), `#size-cells` (const 1), `clocks` (maxItems=21), `clock-names` (ordered-items=21; ordered lite0, lite1, ppmuispx, ppmuispmx, isp, drc, fd, mcuisp, and 13 more), `interrupts` (maxItems=2), `iommus` (maxItems=4), `iommu-names` (ordered-items=4; ordered isp, drc, fd, mcuctl), `power-domains` (maxItems=1), `samsung,pmu-syscon` (ref /schemas/types.yaml#/definitions/phandle).
- child-node patterns: ^pmu@[0-9a-f]+$, ^i2c-isp@[0-9a-f]+$.
- referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/i2c/i2c-controller.yaml#.
- Structural features: endpoint subnodes; patternProperties: ^pmu@[0-9a-f]+$, ^i2c-isp@[0-9a-f]+$; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,exynos4212-fimc-is.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle, /schemas/i2c/i2c-controller.yaml#.
- pattern children: ^pmu@[0-9a-f]+$, ^i2c-isp@[0-9a-f]+$.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, #address-cells, clocks, clock-names, interrupts, ranges, samsung,pmu-syscon, #size-cells`, optional top-level properties include `iommus, iommu-names, power-domains`, and compatible coverage is `samsung,exynos4212-fimc-is`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-is.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/i2c/i2c-controller.yaml#.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-is.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-lite.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-lite.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-lite.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Samsung Exynos SoC series camera host interface (FIMC-LITE)`. Description signal from the file: Each FIMC device should have an alias in the aliases node, in the form of fimc-lite<n>, where <n> is an integer specifying the IP block instance..

## Purpose
The file defines the devicetree ABI for `Samsung Exynos SoC series camera host interface (FIMC-LITE)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,exynos4212-fimc-lite, samsung,exynos5250-fimc-lite.
- required node contract: compatible, reg, clocks, clock-names, interrupts.
- property surface: `compatible` (enum samsung,exynos4212-fimc-lite, samsung,exynos5250-fimc-lite), `reg` (maxItems=1), `clocks` (maxItems=1), `clock-names` (ordered-items=1; ordered flite), `interrupts` (maxItems=1), `iommus` (maxItems=1), `power-domains` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,exynos4212-fimc-lite.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, clocks, clock-names, interrupts`, optional top-level properties include `iommus, power-domains`, and compatible coverage is `samsung,exynos4212-fimc-lite, samsung,exynos5250-fimc-lite`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-lite.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos4212-fimc-lite.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos5250-gsc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos5250-gsc.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos5250-gsc.yaml`, a devicetree binding schema. The schema title is `Samsung Exynos SoC G-Scaler`. Description signal from the file: G-Scaler is used for scaling and color space conversion on Samsung Exynos SoCs. Each G-Scaler node should have a numbered alias in the aliases node, in the form of gscN, N = 0...3..

## Purpose
The file defines the devicetree ABI for `Samsung Exynos SoC G-Scaler`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,exynos5250-gsc, samsung,exynos5420-gsc, samsung,exynos5-gsc, samsung,exynos5433-gsc.
- required node contract: compatible, clocks, clock-names, interrupts, reg.
- property surface: `compatible`, `clocks` (minItems=1, maxItems=5), `clock-names` (minItems=1, maxItems=5), `interrupts` (maxItems=1), `iommus` (maxItems=1), `power-domains` (maxItems=1), `reg` (maxItems=1), `samsung,sysreg` (ref /schemas/types.yaml#/definitions/phandle).
- referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Structural features: closed schema via `additionalProperties: false`; 1 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Inki Dae <inki.dae@samsung.com>, Krzysztof Kozlowski <krzk@kernel.org>, Seung-Woo Kim <sw0312.kim@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,exynos5250-gsc.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, clocks, clock-names, interrupts, reg`, optional top-level properties include `iommus, power-domains, samsung,sysreg`, and compatible coverage is `samsung,exynos5250-gsc, samsung,exynos5420-gsc, samsung,exynos5-gsc, samsung,exynos5433-gsc`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos5250-gsc.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,exynos5250-gsc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,fimc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,fimc.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,fimc.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Samsung S5P/Exynos SoC Camera Subsystem (FIMC)`. Description signal from the file: The S5P/Exynos SoC Camera subsystem comprises of multiple sub-devices represented by separate device tree nodes. Currently this includes: Fully Integrated Mobile Camera (FIMC, in the S5P SoCs series known as CAMIF), MIPI CSIS, FIMC-LITE and FIMC-IS (ISP)..

## Purpose
The file defines the devicetree ABI for `Samsung S5P/Exynos SoC Camera Subsystem (FIMC)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,fimc.
- required node contract: compatible, #address-cells, #clock-cells, clocks, clock-names, clock-output-names, ranges, #size-cells.
- property surface: `compatible` (const samsung,fimc), `ranges`, `#address-cells` (const 1), `#size-cells` (const 1), `#clock-cells` (const 1), `clocks` (minItems=2, maxItems=4), `clock-names` (minItems=2, ordered-items=4; ordered sclk_cam0, sclk_cam1, pxl_async0, pxl_async1), `clock-output-names` (maxItems=2), `parallel-ports` (ref /schemas/graph.yaml#/properties/ports), `pinctrl-names` (minItems=1, ordered-items=4; ordered default, idle, active_a, active_b).
- child-node patterns: ^csis@[0-9a-f]+$, ^fimc@[0-9a-f]+$, ^fimc-is@[0-9a-f]+$, ^fimc-lite@[0-9a-f]+$.
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, samsung,exynos4210-csis.yaml#, samsung,exynos4210-fimc.yaml#, samsung,exynos4212-fimc-is.yaml#, samsung,exynos4212-fimc-lite.yaml#.
- Structural features: endpoint subnodes; patternProperties: ^csis@[0-9a-f]+$, ^fimc@[0-9a-f]+$, ^fimc-is@[0-9a-f]+$, ^fimc-lite@[0-9a-f]+$; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,fimc.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, samsung,exynos4210-csis.yaml#, samsung,exynos4210-fimc.yaml#, samsung,exynos4212-fimc-is.yaml#, samsung,exynos4212-fimc-lite.yaml#.
- pattern children: ^csis@[0-9a-f]+$, ^fimc@[0-9a-f]+$, ^fimc-is@[0-9a-f]+$, ^fimc-lite@[0-9a-f]+$.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, #address-cells, #clock-cells, clocks, clock-names, clock-output-names, ranges, #size-cells`, optional top-level properties include `parallel-ports, pinctrl-names`, and compatible coverage is `samsung,fimc`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,fimc.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, samsung,exynos4210-csis.yaml#, samsung,exynos4210-fimc.yaml#, samsung,exynos4212-fimc-is.yaml#, samsung,exynos4212-fimc-lite.yaml#.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,fimc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5c73m3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5c73m3.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5c73m3.yaml`, a devicetree binding schema. The schema title is `Samsung S5C73M3 8Mp camera ISP`. Description signal from the file: The S5C73M3 camera ISP supports MIPI CSI-2 and parallel (ITU-R BT.656) video data busses. The I2C bus is the main control bus and additionally the SPI bus is used, mostly for transferring the firmware to and from the device. Two slave device nodes corresponding to these control bus interfaces are required and should be placed under respective bus controller nodes..

## Purpose
The file defines the devicetree ABI for `Samsung S5C73M3 8Mp camera ISP`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,s5c73m3.
- required node contract: compatible, reg.
- property surface: `compatible` (const samsung,s5c73m3), `reg` (maxItems=1), `clocks` (maxItems=1), `clock-names` (ordered-items=1; ordered cis_extclk), `clock-frequency` (cis_extclk clock frequency.), `standby-gpios` (maxItems=1), `vdda-supply` (Analog power supply (1.2V).), `vdd-af-supply` (lens power supply (2.8V).), `vddio-cis-supply` (CIS I/O power supply (1.2V to 1.8V).), `vddio-host-supply` (Host I/O power supply (1.8V to 2.8V).), `vdd-int-supply` (Digital power supply (1.2V).), `vdd-reg-supply` (Regulator input power supply (2.8V).), `xshutdown-gpios` (maxItems=1), `port` (ref /schemas/graph.yaml#/$defs/port-base).
- referenced schemas: /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, /schemas/spi/spi-peripheral-props.yaml#.
- Structural features: single graph `port`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 2 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: unevaluatedProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[1]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. Regulator supply properties persist power-rail dependencies that board DTS files must wire correctly.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,s5c73m3.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, /schemas/spi/spi-peripheral-props.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg`, optional top-level properties include `clocks, clock-names, clock-frequency, standby-gpios, vdda-supply, vdd-af-supply, vddio-cis-supply, vddio-host-supply, vdd-int-supply, vdd-reg-supply, xshutdown-gpios, port`, and compatible coverage is `samsung,s5c73m3`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5c73m3.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, /schemas/spi/spi-peripheral-props.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5c73m3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5p-mfc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5p-mfc.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5p-mfc.yaml`, a video codec/accelerator devicetree binding. The schema title is `Samsung Exynos Multi Format Codec (MFC)`. Description signal from the file: Multi Format Codec (MFC) is the IP present in Samsung SoCs which supports high resolution decoding and encoding functionalities..

## Purpose
The file defines the devicetree ABI for `Samsung Exynos Multi Format Codec (MFC)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,exynos5433-mfc, samsung,mfc-v5, samsung,mfc-v6, samsung,mfc-v7, samsung,mfc-v8, samsung,mfc-v10, tesla,fsd-mfc, samsung,exynos3250-mfc.
- required node contract: compatible, reg, clocks, clock-names, interrupts.
- property surface: `compatible`, `reg` (maxItems=1), `clocks` (minItems=1, maxItems=3), `clock-names` (minItems=1, maxItems=3), `interrupts` (maxItems=1), `iommus` (minItems=1, maxItems=2), `iommu-names` (minItems=1, ordered-items=2; ordered left, right), `power-domains` (maxItems=1), `memory-region` (minItems=1, maxItems=2).
- Structural features: closed schema via `additionalProperties: false`; 6 allOf composition block(s); 6 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 6 conditional site(s): allOf[0], allOf[1], allOf[2], allOf[3], allOf[4], allOf[5]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. The `memory-region` property also persists reserved-memory relationships in the devicetree for firmware or DMA-visible buffers. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Marek Szyprowski <m.szyprowski@samsung.com>, Aakarsh Jain <aakarsh.jain@samsung.com>.
- schema id: http://devicetree.org/schemas/media/samsung,s5p-mfc.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, clocks, clock-names, interrupts`, optional top-level properties include `iommus, iommu-names, power-domains, memory-region`, and compatible coverage is `samsung,exynos5433-mfc, samsung,mfc-v5, samsung,mfc-v6, samsung,mfc-v7, samsung,mfc-v8, samsung,mfc-v10, tesla,fsd-mfc, samsung,exynos3250-mfc`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5p-mfc.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5p-mfc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5pv210-jpeg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5pv210-jpeg.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5pv210-jpeg.yaml`, a video codec/accelerator devicetree binding. The schema title is `Samsung S5PV210 and Exynos SoC JPEG codec`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `Samsung S5PV210 and Exynos SoC JPEG codec`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: samsung,s5pv210-jpeg, samsung,exynos3250-jpeg, samsung,exynos4210-jpeg, samsung,exynos4212-jpeg, samsung,exynos5420-jpeg, samsung,exynos5433-jpeg.
- required node contract: compatible, clocks, clock-names, interrupts, reg.
- property surface: `compatible` (enum samsung,s5pv210-jpeg, samsung,exynos3250-jpeg, samsung,exynos4210-jpeg, samsung,exynos4212-jpeg, samsung,exynos5420-jpeg, samsung,exynos5433-jpeg), `clocks` (minItems=1, maxItems=4), `clock-names` (minItems=1, maxItems=4), `interrupts` (maxItems=1), `iommus` (maxItems=1), `power-domains` (maxItems=1), `reg` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`; 3 allOf composition block(s); 3 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 3 conditional site(s): allOf[0], allOf[1], allOf[2]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Jacek Anaszewski <jacek.anaszewski@gmail.com>, Krzysztof Kozlowski <krzk@kernel.org>, Sylwester Nawrocki <s.nawrocki@samsung.com>, Andrzej Pietrasiewicz <andrzejtp2010@gmail.com>.
- schema id: http://devicetree.org/schemas/media/samsung,s5pv210-jpeg.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, clocks, clock-names, interrupts, reg`, optional top-level properties include `iommus, power-domains`, and compatible coverage is `samsung,s5pv210-jpeg, samsung,exynos3250-jpeg, samsung,exynos4210-jpeg, samsung,exynos4212-jpeg, samsung,exynos5420-jpeg, samsung,exynos5433-jpeg`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5pv210-jpeg.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/samsung,s5pv210-jpeg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/silabs,si470x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/silabs,si470x.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/silabs,si470x.yaml`, a media ancillary controller devicetree binding. The schema title is `Silicon Labs Si470x FM Radio Receiver`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `Silicon Labs Si470x FM Radio Receiver`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: silabs,si470x.
- required node contract: compatible, reg.
- property surface: `compatible` (const silabs,si470x), `reg` (maxItems=1), `interrupts` (maxItems=1), `reset-gpios` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Hans Verkuil <hverkuil@kernel.org>, Paweł Chmiel <pawel.mikolaj.chmiel@gmail.com>.
- schema id: http://devicetree.org/schemas/media/silabs,si470x.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg`, optional top-level properties include `interrupts, reset-gpios`, and compatible coverage is `silabs,si470x`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/silabs,si470x.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/silabs,si470x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/snps,dw-hdmi-rx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/snps,dw-hdmi-rx.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/snps,dw-hdmi-rx.yaml`, a devicetree binding schema. The schema title is `Synopsys DesignWare HDMI RX Controller`. Description signal from the file: Synopsys DesignWare HDMI Input Controller preset on RK3588 SoCs allowing devices to receive and decode high-resolution video streams from external sources like media players, cameras, laptops, etc..

## Purpose
The file defines the devicetree ABI for `Synopsys DesignWare HDMI RX Controller`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: rockchip,rk3588-hdmirx-ctrler, snps,dw-hdmi-rx.
- required node contract: compatible, reg, interrupts, interrupt-names, clocks, clock-names, power-domains, resets, pinctrl-0, hpd-gpios.
- property surface: `compatible` (ordered-items=2; ordered rockchip,rk3588-hdmirx-ctrler, snps,dw-hdmi-rx), `reg` (maxItems=1), `interrupts` (maxItems=3), `interrupt-names` (ordered-items=3; ordered cec, hdmi, dma), `clocks` (maxItems=7), `clock-names` (ordered-items=7; ordered aclk, audio, cr_para, pclk, ref, hclk_s_hdmirx, hclk_vo1), `power-domains` (maxItems=1), `resets` (maxItems=4), `reset-names` (ordered-items=4; ordered axi, apb, ref, biu), `memory-region` (maxItems=1), `hpd-gpios` (maxItems=1), `rockchip,grf` (ref /schemas/types.yaml#/definitions/phandle), `rockchip,vo1-grf` (ref /schemas/types.yaml#/definitions/phandle).
- referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. The `memory-region` property also persists reserved-memory relationships in the devicetree for firmware or DMA-visible buffers.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Dmitry Osipenko <dmitry.osipenko@collabora.com>.
- schema id: http://devicetree.org/schemas/media/snps,dw-hdmi-rx.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, interrupt-names, clocks, clock-names, power-domains, resets, pinctrl-0, hpd-gpios`, optional top-level properties include `reset-names, memory-region, rockchip,grf, rockchip,vo1-grf`, and compatible coverage is `rockchip,rk3588-hdmirx-ctrler, snps,dw-hdmi-rx`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/snps,dw-hdmi-rx.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/snps,dw-hdmi-rx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmi.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmi.yaml`, a media capture or video pipeline devicetree binding. The schema title is `STMicroelectronics STM32 Digital Camera Memory Interface (DCMI)`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `STMicroelectronics STM32 Digital Camera Memory Interface (DCMI)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: st,stm32-dcmi.
- required node contract: compatible, reg, interrupts, clocks, clock-names, resets, dmas, dma-names, port.
- property surface: `compatible` (const st,stm32-dcmi), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `clock-names` (ordered-items=1; ordered mclk), `dmas` (minItems=1, maxItems=2), `dma-names` (minItems=1, ordered-items=2; ordered tx, mdma_tx), `resets` (maxItems=1), `access-controllers` (minItems=1, maxItems=2), `power-domains` (maxItems=1), `sram` (ref /schemas/types.yaml#/definitions/phandle), `port` (ref /schemas/graph.yaml#/$defs/port-base).
- referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: single graph `port`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): properties/port/properties/endpoint/allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. DMA channel properties persist the binding between the hardware block and the DMA engine channels it relies on.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Hugues Fruchet <hugues.fruchet@foss.st.com>.
- schema id: http://devicetree.org/schemas/media/st,stm32-dcmi.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, resets, dmas, dma-names, port`, optional top-level properties include `access-controllers, power-domains, sram`, and compatible coverage is `st,stm32-dcmi`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmi.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmipp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmipp.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmipp.yaml`, a media capture or video pipeline devicetree binding. The schema title is `STMicroelectronics STM32 DCMIPP Digital Camera Memory Interface Pixel Processor`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `STMicroelectronics STM32 DCMIPP Digital Camera Memory Interface Pixel Processor`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: st,stm32mp13-dcmipp, st,stm32mp25-dcmipp.
- required node contract: compatible, reg, interrupts, clocks, resets, port.
- property surface: `compatible` (enum st,stm32mp13-dcmipp, st,stm32mp25-dcmipp), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (minItems=1, ordered-items=2), `clock-names` (minItems=1, ordered-items=2; ordered kclk, mclk), `resets` (maxItems=1), `power-domains` (maxItems=1), `access-controllers` (minItems=1, maxItems=2), `port` (ref /schemas/graph.yaml#/$defs/port-base).
- referenced schemas: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: single graph `port`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 1 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Hugues Fruchet <hugues.fruchet@foss.st.com>, Alain Volmat <alain.volmat@foss.st.com>.
- schema id: http://devicetree.org/schemas/media/st,stm32-dcmipp.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, resets, port`, optional top-level properties include `clock-names, power-domains, access-controllers`, and compatible coverage is `st,stm32mp13-dcmipp, st,stm32mp25-dcmipp`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmipp.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dcmipp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dma2d.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dma2d.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dma2d.yaml`, a devicetree binding schema. The schema title is `STMicroelectronics STM32 Chrom-Art Accelerator DMA2D`. Description signal from the file: Chrom-ART Accelerator(DMA2D), graphical hardware accelerator enabling enhanced graphical user interface with minimum CPU load It can perform the following operations. - Filling a part or the whole of a destination image with a specific color. - Copying a part or the whole of a source image into a part or the whole of a destination image. - Copying a part or the whole of a source image into a part or the whole of a de.

## Purpose
The file defines the devicetree ABI for `STMicroelectronics STM32 Chrom-Art Accelerator DMA2D`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: st,stm32-dma2d.
- required node contract: compatible, reg, interrupts, clocks, clock-names, resets.
- property surface: `compatible` (const st,stm32-dma2d), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `clock-names` (ordered-items=1; ordered dma2d), `resets` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Dillon Min <dillon.minfei@gmail.com>.
- schema id: http://devicetree.org/schemas/media/st,stm32-dma2d.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, resets`, optional top-level properties include `none declared`, and compatible coverage is `st,stm32-dma2d`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dma2d.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32-dma2d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-csi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-csi.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-csi.yaml`, a media capture or video pipeline devicetree binding. The schema title is `STMicroelectronics STM32 CSI controller`. Description signal from the file: The STM32 CSI controller, coupled with a D-PHY allows connecting a CSI-2 based camera to the DCMIPP camera pipeline..

## Purpose
The file defines the devicetree ABI for `STMicroelectronics STM32 CSI controller`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: st,stm32mp25-csi.
- required node contract: compatible, reg, interrupts, clocks, clock-names, resets, ports.
- property surface: `compatible` (enum st,stm32mp25-csi), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=3), `clock-names` (ordered-items=3; ordered pclk, txesc, csi2phy), `resets` (maxItems=1), `vdd-supply` (Digital core power supply (0.91V)), `vdda18-supply` (System analog power supply (1.8V)), `access-controllers` (minItems=1, maxItems=2), `power-domains` (maxItems=1), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. Regulator supply properties persist power-rail dependencies that board DTS files must wire correctly.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Alain Volmat <alain.volmat@foss.st.com>.
- schema id: http://devicetree.org/schemas/media/st,stm32mp25-csi.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, resets, ports`, optional top-level properties include `vdd-supply, vdda18-supply, access-controllers, power-domains`, and compatible coverage is `st,stm32mp25-csi`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-csi.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-csi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-video-codec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-video-codec.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-video-codec.yaml`, a video codec/accelerator devicetree binding. The schema title is `STMicroelectronics STM32MP25 VDEC video decoder & VENC video encoder`. Description signal from the file: The STMicroelectronics STM32MP25 SOCs embeds a VDEC video hardware decoder peripheral based on Verisilicon VC8000NanoD IP (former Hantro G1) and a VENC video hardware encoder peripheral based on Verisilicon VC8000NanoE IP (former Hantro H1)..

## Purpose
The file defines the devicetree ABI for `STMicroelectronics STM32MP25 VDEC video decoder & VENC video encoder`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: st,stm32mp25-vdec, st,stm32mp25-venc.
- required node contract: compatible, reg, interrupts, clocks.
- property surface: `compatible` (enum st,stm32mp25-vdec, st,stm32mp25-venc), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (maxItems=1), `access-controllers` (minItems=1, maxItems=2).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Hugues Fruchet <hugues.fruchet@foss.st.com>.
- schema id: http://devicetree.org/schemas/media/st,stm32mp25-video-codec.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks`, optional top-level properties include `access-controllers`, and compatible coverage is `st,stm32mp25-vdec, st,stm32mp25-venc`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-video-codec.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/st,stm32mp25-video-codec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,cal.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,cal.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,cal.yaml`, a devicetree binding schema. The schema title is `Texas Instruments DRA72x CAMERA ADAPTATION LAYER (CAL)`. Description signal from the file: The Camera Adaptation Layer (CAL) is a key component for image capture applications. The capture module provides the system interface and the processing capability to connect CSI2 image-sensor modules to the DRA72x device. CAL supports 2 camera port nodes on MIPI bus..

## Purpose
The file defines the devicetree ABI for `Texas Instruments DRA72x CAMERA ADAPTATION LAYER (CAL)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: ti,dra72-cal, ti,dra72-pre-es2-cal, ti,dra76-cal, ti,am654-cal.
- required node contract: compatible, reg, reg-names, interrupts, ti,camerrx-control.
- property surface: `compatible` (enum ti,dra72-cal, ti,dra72-pre-es2-cal, ti,dra76-cal, ti,am654-cal), `reg` (minItems=2, ordered-items=3), `reg-names` (minItems=2, ordered-items=3; ordered cal_top, cal_rx_core0, cal_rx_core1), `interrupts` (maxItems=1), `ti,camerrx-control` (ref /schemas/types.yaml#/definitions/phandle-array; ordered-items=1), `clocks` (maxItems=1), `clock-names` (const fck), `power-domains` (maxItems=1), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Benoit Parrot <bparrot@ti.com>.
- schema id: http://devicetree.org/schemas/media/ti,cal.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, reg-names, interrupts, ti,camerrx-control`, optional top-level properties include `clocks, clock-names, power-domains, ports`, and compatible coverage is `ti,dra72-cal, ti,dra72-pre-es2-cal, ti,dra76-cal, ti,am654-cal`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,cal.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,cal.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,j721e-csi2rx-shim.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,j721e-csi2rx-shim.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,j721e-csi2rx-shim.yaml`, a media capture or video pipeline devicetree binding. The schema title is `TI J721E CSI2RX Shim`. Description signal from the file: The TI J721E CSI2RX Shim is a wrapper around Cadence CSI2RX bridge that enables sending captured frames to memory over PSI-L DMA. In the J721E Technical Reference Manual (SPRUIL1B) it is referred to as "SHIM" under the CSI_RX_IF section..

## Purpose
The file defines the devicetree ABI for `TI J721E CSI2RX Shim`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: ti,j721e-csi2rx-shim.
- required node contract: compatible, reg, dmas, dma-names, power-domains, ranges, #address-cells, #size-cells.
- property surface: `compatible` (const ti,j721e-csi2rx-shim), `dmas` (maxItems=1), `dma-names` (ordered-items=1; ordered rx0), `reg` (maxItems=1), `power-domains` (maxItems=1), `ranges`, `#address-cells`, `#size-cells`.
- child-node patterns: ^csi-bridge@.
- referenced schemas: cdns,csi2rx.yaml#.
- Structural features: endpoint subnodes; patternProperties: ^csi-bridge@; closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. DMA channel properties persist the binding between the hardware block and the DMA engine channels it relies on.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Jai Luthra <jai.luthra@linux.dev>.
- schema id: http://devicetree.org/schemas/media/ti,j721e-csi2rx-shim.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: cdns,csi2rx.yaml#.
- pattern children: ^csi-bridge@.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, dmas, dma-names, power-domains, ranges, #address-cells, #size-cells`, optional top-level properties include `none declared`, and compatible coverage is `ti,j721e-csi2rx-shim`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,j721e-csi2rx-shim.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: cdns,csi2rx.yaml#.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,j721e-csi2rx-shim.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,omap3isp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,omap3isp.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,omap3isp.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Texas Instruments OMAP 3 Image Signal Processor (ISP)`. Description signal from the file: The OMAP 3 ISP is an image signal processor present in OMAP 3 SoCs..

## Purpose
The file defines the devicetree ABI for `Texas Instruments OMAP 3 Image Signal Processor (ISP)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: ti,omap3-isp.
- required node contract: compatible, reg, interrupts, iommus, syscon, ti,phy-type, #clock-cells.
- property surface: `compatible` (const ti,omap3-isp), `reg` (ordered-items=2), `interrupts` (maxItems=1), `iommus` (maxItems=1), `syscon` (ref /schemas/types.yaml#/definitions/phandle-array; ordered-items=1), `ti,phy-type` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `#clock-cells` (const 1), `vdd-csiphy1-supply` (Voltage supply of the CSI-2 PHY 1), `vdd-csiphy2-supply` (Voltage supply of the CSI-2 PHY 2), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time. Regulator supply properties persist power-rail dependencies that board DTS files must wire correctly. IOMMU phandles persist DMA translation requirements for the associated hardware.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Laurent Pinchart <laurent.pinchart@ideasonboard.com>, Sakari Ailus <sakari.ailus@iki.fi>.
- schema id: http://devicetree.org/schemas/media/ti,omap3isp.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle-array, /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, iommus, syscon, ti,phy-type, #clock-cells`, optional top-level properties include `vdd-csiphy1-supply, vdd-csiphy2-supply, ports`, and compatible coverage is `ti,omap3-isp`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,omap3isp.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,omap3isp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,vip.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,vip.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,vip.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Texas Instruments DRA7x Video Input Port (VIP)`. Description signal from the file: Video Input Port (VIP) can be found on devices such as DRA7xx and provides the system interface and the processing capability to connect parallel image-sensor as well as BT.656/1120 capable encoder chip to DRA7x device. Each VIP instance supports 2 independently configurable external video input capture slices (Slice 0 and Slice 1) each providing up to two video input ports (Port A and Port B)..

## Purpose
The file defines the devicetree ABI for `Texas Instruments DRA7x Video Input Port (VIP)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: ti,dra7-vip.
- required node contract: compatible, reg, interrupts, ti,ctrl-module, ports.
- property surface: `compatible` (enum ti,dra7-vip), `reg` (maxItems=1), `interrupts` (ordered-items=2), `ti,ctrl-module` (ref /schemas/types.yaml#/definitions/phandle-array; maxItems=1), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Yemike Abhilash Chandra <y-abhilashchandra@ti.com>.
- schema id: http://devicetree.org/schemas/media/ti,vip.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, ti,ctrl-module, ports`, optional top-level properties include `none declared`, and compatible coverage is `ti,dra7-vip`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,vip.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,vip.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,vpe.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,vpe.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,vpe.yaml`, a devicetree binding schema. The schema title is `Texas Instruments DRA7x Video Processing Engine (VPE)`. Description signal from the file: The Video Processing Engine (VPE) is a key component for image post processing applications. VPE consist of a single memory to memory path which can perform chroma up/down sampling, deinterlacing, scaling and color space conversion..

## Purpose
The file defines the devicetree ABI for `Texas Instruments DRA7x Video Processing Engine (VPE)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: ti,dra7-vpe.
- required node contract: compatible, reg, reg-names, interrupts.
- property surface: `compatible` (const ti,dra7-vpe), `reg` (ordered-items=4), `reg-names` (ordered-items=4; ordered vpe_top, sc, csc, vpdma), `interrupts` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present.
Key dependency signals in this file are:
- maintainers: Benoit Parrot <bparrot@ti.com>.
- schema id: http://devicetree.org/schemas/media/ti,vpe.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, reg-names, interrupts`, optional top-level properties include `none declared`, and compatible coverage is `ti,dra7-vpe`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,vpe.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/ti,vpe.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interface-devices.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interface-devices.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interface-devices.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Common Properties for Video Receiver and Transmitter Devices`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `Common Properties for Video Receiver and Transmitter Devices`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- property surface: `flash-leds` (ref /schemas/types.yaml#/definitions/phandle-array), `leds` (minItems=1, maxItems=1), `led-names` (enum privacy), `lens-focus` (ref /schemas/types.yaml#/definitions/phandle), `rotation` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 90, 180, 270), `orientation` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1, 2).
- referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint32.
- Structural features: no graph child-node or composition machinery beyond top-level property validation.
- Schema closure: inherits openness from composed references or leaves additional properties unconstrained where allowed.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file has no inline example block, so coverage depends on external DTS users and schemas that reference it.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Jacopo Mondi <jacopo@jmondi.org>, Sakari Ailus <sakari.ailus@linux.intel.com>.
- schema id: http://devicetree.org/schemas/media/video-interface-devices.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/phandle-array, /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint32.

## Risks And Edge Cases
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `none declared`, optional top-level properties include `flash-leds, leds, led-names, lens-focus, rotation, orientation`, and compatible coverage is `none declared`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interface-devices.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/phandle-array, /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint32.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interface-devices.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interfaces.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interfaces.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interfaces.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Common Properties for Video Receiver and Transmitter Interface Endpoints`. Description signal from the file: Video data pipelines usually consist of external devices, e.g. camera sensors, controlled over an I2C, SPI or UART bus, and SoC internal IP blocks, including video DMA engines and video data processors. SoC internal blocks are described by DT nodes, placed similarly to other SoC blocks. External devices are represented as child nodes of their respective bus controller nodes, e.g. I2C. Data interfaces on all video dev.

## Purpose
The file defines the devicetree ABI for `Common Properties for Video Receiver and Transmitter Interface Endpoints`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- property surface: `slave-mode` (Indicates that the link is run in slave mode. The default when this property is not specif), `bus-type` (ref /schemas/types.yaml#/definitions/uint32; enum 1, 2, 3, 4, 5, 6, 7), `bus-width` (ref /schemas/types.yaml#/definitions/uint32; maximum=64), `data-shift` (ref /schemas/types.yaml#/definitions/uint32; maximum=64), `hsync-active` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `vsync-active` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `data-active` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `data-enable-active` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `field-even-active` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `pclk-sample` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1, 2), `sync-on-green-active` (ref /schemas/types.yaml#/definitions/uint32; enum 0, 1), `data-lanes` (ref /schemas/types.yaml#/definitions/uint32-array; minItems=1, maxItems=8), `clock-lanes` (ref /schemas/types.yaml#/definitions/uint32; maximum=8), `clock-noncontinuous` (Allow MIPI CSI-2 non-continuous clock mode.), `link-frequencies` (ref /schemas/types.yaml#/definitions/uint64-array), `lane-polarities` (ref /schemas/types.yaml#/definitions/uint32-array; minItems=1, maxItems=9, item-enum=0/1), and 2 more.
- referenced schemas: /schemas/graph.yaml#/$defs/endpoint-base, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint64-array.
- Structural features: endpoint subnodes; 1 allOf composition block(s).
- Schema closure: inherits openness from composed references or leaves additional properties unconstrained where allowed.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file has no inline example block, so coverage depends on external DTS users and schemas that reference it.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Sakari Ailus <sakari.ailus@linux.intel.com>, Laurent Pinchart <laurent.pinchart@ideasonboard.com>.
- schema id: http://devicetree.org/schemas/media/video-interfaces.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/$defs/endpoint-base, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint64-array.

## Risks And Edge Cases
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `none declared`, optional top-level properties include `slave-mode, bus-type, bus-width, data-shift, hsync-active, vsync-active, data-active, data-enable-active, field-even-active, pclk-sample, sync-on-green-active, data-lanes, clock-lanes, clock-noncontinuous, link-frequencies, lane-polarities, and 2 more`, and compatible coverage is `none declared`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interfaces.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/$defs/endpoint-base, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint32-array, /schemas/types.yaml#/definitions/uint64-array.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-interfaces.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-mux.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-mux.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-mux.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Video Multiplexer`. Description signal from the file: Video multiplexers allow to select between multiple input ports. Video received on the active input port is passed through to the output port. Muxes described by this binding are controlled by a multiplexer controller..

## Purpose
The file defines the devicetree ABI for `Video Multiplexer`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: video-mux.
- required node contract: compatible, mux-controls.
- property surface: `compatible` (const video-mux), `mux-controls` (maxItems=1), `#address-cells` (const 1), `#size-cells` (const 0), `ports` (ref /schemas/graph.yaml#/properties/ports).
- child-node patterns: ^port@.
- referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; patternProperties: ^port@; closed schema via `additionalProperties: false`; 2 oneOf branch(es).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Sakari Ailus <sakari.ailus@linux.intel.com>, Laurent Pinchart <laurent.pinchart@ideasonboard.com>.
- schema id: http://devicetree.org/schemas/media/video-mux.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port.
- pattern children: ^port@.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, mux-controls`, optional top-level properties include `#address-cells, #size-cells, ports`, and compatible coverage is `video-mux`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-mux.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/video-mux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/xilinx/xlnx,csi2rxss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/xilinx/xlnx,csi2rxss.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/xilinx/xlnx,csi2rxss.yaml`, a media capture or video pipeline devicetree binding. The schema title is `Xilinx MIPI CSI-2 Receiver Subsystem`. Description signal from the file: The Xilinx MIPI CSI-2 Receiver Subsystem is used to capture MIPI CSI-2 traffic from compliant camera sensors and send the output as AXI4 Stream video data for image processing. The subsystem consists of a MIPI D-PHY in slave mode which captures the data packets. This is passed along the MIPI CSI-2 Rx IP which extracts the packet data. The optional Video Format Bridge (VFB) converts this data to AXI4 Stream video data.

## Purpose
The file defines the devicetree ABI for `Xilinx MIPI CSI-2 Receiver Subsystem`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: xlnx,mipi-csi2-rx-subsystem-5.0.
- required node contract: compatible, reg, interrupts, clocks, clock-names, ports.
- property surface: `compatible` (ordered-items=1), `reg` (maxItems=1), `interrupts` (maxItems=1), `clocks` (ordered-items=2), `clock-names` (ordered-items=2; ordered lite_aclk, video_aclk), `xlnx,csi-pxl-format` (ref /schemas/types.yaml#/definitions/uint32), `xlnx,vfb` (Present when Video Format Bridge is enabled in IP configuration), `xlnx,en-csi-v2-0` (Present if CSI v2 is enabled in IP configuration.), `xlnx,en-vcx` (When present, there are maximum 16 virtual channels, else only 4.), `xlnx,en-active-lanes` (Present if the number of active lanes can be re-configured at runtime in the Protocol Conf), `video-reset-gpios` (maxItems=1), `ports` (ref /schemas/graph.yaml#/properties/ports).
- referenced schemas: /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- Structural features: multi-port graph container `ports`; endpoint subnodes; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`; 2 allOf composition block(s); 2 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 2 conditional site(s): allOf[0], allOf[1]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with Linux devicetree validation for V4L2/media-controller style pipelines, platform drivers matching `compatible`, and common media graph parsing through `port`, `ports`, `endpoint`, and `remote-endpoint` links where present. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Vishal Sagar <vishal.sagar@amd.com>.
- schema id: http://devicetree.org/schemas/media/xilinx/xlnx,csi2rxss.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- graph endpoint mistakes can silently break media pipeline discovery even when the hardware resources validate.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts, clocks, clock-names, ports`, optional top-level properties include `xlnx,csi-pxl-format, xlnx,vfb, xlnx,en-csi-v2-0, xlnx,en-vcx, xlnx,en-active-lanes, video-reset-gpios`, and compatible coverage is `xlnx,mipi-csi2-rx-subsystem-5.0`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/xilinx/xlnx,csi2rxss.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/uint32, /schemas/graph.yaml#/properties/ports, /schemas/graph.yaml#/$defs/port-base, /schemas/media/video-interfaces.yaml#, /schemas/graph.yaml#/properties/port.
- media graph endpoints should be checked for matching `remote-endpoint`, lane counts, and bus types.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/media/xilinx/xlnx,csi2rxss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/arm,pl172.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/arm,pl172.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/arm,pl172.yaml`, a memory-controller devicetree binding. The schema title is `ARM PL172/PL175/PL176 MultiPort Memory Controller`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `ARM PL172/PL175/PL176 MultiPort Memory Controller`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: arm,pl172, arm,pl175, arm,pl176, arm,primecell.
- required node contract: compatible, reg, #address-cells, #size-cells, ranges, clocks, clock-names.
- property surface: `compatible` (ordered-items=2; ordered arm,primecell), `reg` (maxItems=1), `#address-cells` (const 2), `#size-cells` (const 1), `ranges`, `clocks` (maxItems=2), `clock-names` (ordered-items=2; ordered mpmcclk, apb_pclk), `clock-ranges`, `resets` (maxItems=1).
- child-node patterns: ^cs[0-9]$.
- referenced schemas: /schemas/mtd/mtd-physmap.yaml#, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/flag.
- Structural features: patternProperties: ^cs[0-9]$; closed schema via `additionalProperties: false`; closed schema via `unevaluatedProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Frank Li <Frank.Li@nxp.com>.
- schema id: http://devicetree.org/schemas/memory-controllers/arm,pl172.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/mtd/mtd-physmap.yaml#, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/flag.
- pattern children: ^cs[0-9]$.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, #address-cells, #size-cells, ranges, clocks, clock-names`, optional top-level properties include `clock-ranges, resets`, and compatible coverage is `arm,pl172, arm,pl175, arm,pl176, arm,primecell`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/arm,pl172.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/mtd/mtd-physmap.yaml#, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/flag.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/arm,pl172.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/arm,pl35x-smc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/arm,pl35x-smc.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/arm,pl35x-smc.yaml`, a memory-controller devicetree binding. The schema title is `Arm PL35x Series Static Memory Controller (SMC)`. Description signal from the file: The PL35x Static Memory Controller is a bus where you can connect two kinds of memory interfaces, which are NAND and memory mapped interfaces (such as SRAM or NOR) depending on the specific configuration. The TRM is available here: https://documentation-service.arm.com/static/5e8e2524fd977155116a58aa.

## Purpose
The file defines the devicetree ABI for `Arm PL35x Series Static Memory Controller (SMC)`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: arm,pl353-smc-r2p1, arm,pl354, arm,primecell.
- required node contract: compatible, reg, clock-names, clocks.
- property surface: `$nodename`, `compatible` (ordered-items=2; ordered arm,primecell), `#address-cells` (const 2), `#size-cells` (const 1), `reg` (ordered-items=1), `clocks` (minItems=1, maxItems=2), `clock-names` (minItems=1, maxItems=2), `ranges` (minItems=1, maxItems=8), `interrupts` (minItems=1, ordered-items=2).
- child-node patterns: @[0-7],[a-f0-9]+$.
- Structural features: patternProperties: @[0-7],[a-f0-9]+$; closed schema via `additionalProperties: false`; 1 allOf composition block(s); 1 conditional validation site(s).
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. 1 conditional site(s): allOf[0]. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings.
Key dependency signals in this file are:
- maintainers: Miquel Raynal <miquel.raynal@bootlin.com>.
- schema id: http://devicetree.org/schemas/memory-controllers/arm,pl35x-smc.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- pattern children: @[0-7],[a-f0-9]+$.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, clock-names, clocks`, optional top-level properties include `$nodename, #address-cells, #size-cells, ranges, interrupts`, and compatible coverage is `arm,pl353-smc-r2p1, arm,pl354, arm,primecell`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/arm,pl35x-smc.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/arm,pl35x-smc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,brcmstb-memc-ddr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,brcmstb-memc-ddr.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,brcmstb-memc-ddr.yaml`, a memory-controller devicetree binding. The schema title is `Memory controller (MEMC) for Broadcom STB`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `Memory controller (MEMC) for Broadcom STB`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: brcm,brcmstb-memc-ddr-rev-b.2.2, brcm,brcmstb-memc-ddr-rev-b.2.3, brcm,brcmstb-memc-ddr-rev-b.2.5, brcm,brcmstb-memc-ddr-rev-b.2.6, brcm,brcmstb-memc-ddr-rev-b.2.7, brcm,brcmstb-memc-ddr-rev-b.2.8, brcm,brcmstb-memc-ddr-rev-b.3.0, brcm,brcmstb-memc-ddr-rev-b.3.1, brcm,brcmstb-memc-ddr-rev-c.1.0, brcm,brcmstb-memc-ddr-rev-c.1.1, brcm,brcmstb-memc-ddr-rev-c.1.2, brcm,brcmstb-memc-ddr-rev-c.1.3, brcm,brcmstb-memc-ddr-rev-c.1.4, brcm,brcmstb-memc-ddr-rev-b.2.1, brcm,brcmstb-memc-ddr, brcm,brcmstb-memc-ddr-rev-b.2.0, and 2 more.
- required node contract: compatible, reg.
- property surface: `compatible`, `reg` (maxItems=1), `clock-frequency` (DDR PHY frequency in Hz).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings.
Key dependency signals in this file are:
- maintainers: Florian Fainelli <f.fainelli@gmail.com>.
- schema id: http://devicetree.org/schemas/memory-controllers/brcm,brcmstb-memc-ddr.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- incorrect DRAM timing values can describe unsafe controller programming even though the schema only checks shape and ranges.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg`, optional top-level properties include `clock-frequency`, and compatible coverage is `brcm,brcmstb-memc-ddr-rev-b.2.2, brcm,brcmstb-memc-ddr-rev-b.2.3, brcm,brcmstb-memc-ddr-rev-b.2.5, brcm,brcmstb-memc-ddr-rev-b.2.6, brcm,brcmstb-memc-ddr-rev-b.2.7, brcm,brcmstb-memc-ddr-rev-b.2.8, brcm,brcmstb-memc-ddr-rev-b.3.0, brcm,brcmstb-memc-ddr-rev-b.3.1, brcm,brcmstb-memc-ddr-rev-c.1.0, brcm,brcmstb-memc-ddr-rev-c.1.1, brcm,brcmstb-memc-ddr-rev-c.1.2, brcm,brcmstb-memc-ddr-rev-c.1.3, brcm,brcmstb-memc-ddr-rev-c.1.4, brcm,brcmstb-memc-ddr-rev-b.2.1, brcm,brcmstb-memc-ddr, brcm,brcmstb-memc-ddr-rev-b.2.0, and 2 more`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,brcmstb-memc-ddr.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,brcmstb-memc-ddr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,dpfe-cpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,dpfe-cpu.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,dpfe-cpu.yaml`, a memory-controller devicetree binding. The schema title is `DDR PHY Front End (DPFE) for Broadcom STB`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `DDR PHY Front End (DPFE) for Broadcom STB`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: brcm,bcm7271-dpfe-cpu, brcm,bcm7268-dpfe-cpu, brcm,dpfe-cpu.
- required node contract: compatible, reg, reg-names.
- property surface: `compatible` (ordered-items=2; ordered brcm,dpfe-cpu), `reg` (ordered-items=3), `reg-names` (ordered-items=3; ordered dpfe-cpu, dpfe-dmem, dpfe-imem).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>, Markus Mayer <mmayer@broadcom.com>.
- schema id: http://devicetree.org/schemas/memory-controllers/brcm,dpfe-cpu.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, reg-names`, optional top-level properties include `none declared`, and compatible coverage is `brcm,bcm7271-dpfe-cpu, brcm,bcm7268-dpfe-cpu, brcm,dpfe-cpu`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,dpfe-cpu.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/brcm,dpfe-cpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/calxeda-ddr-ctrlr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/calxeda-ddr-ctrlr.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/calxeda-ddr-ctrlr.yaml`, a memory-controller devicetree binding. The schema title is `Calxeda DDR memory controller`. Description signal from the file: The Calxeda DDR memory controller is initialised and programmed by the firmware, but an OS might want to read its registers for error reporting purposes and to learn about the DRAM topology..

## Purpose
The file defines the devicetree ABI for `Calxeda DDR memory controller`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: calxeda,hb-ddr-ctrl, calxeda,ecx-2000-ddr-ctrl.
- required node contract: compatible, reg, interrupts.
- property surface: `compatible` (enum calxeda,hb-ddr-ctrl, calxeda,ecx-2000-ddr-ctrl), `reg` (maxItems=1), `interrupts` (maxItems=1).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings.
Key dependency signals in this file are:
- maintainers: Andre Przywara <andre.przywara@arm.com>.
- schema id: http://devicetree.org/schemas/memory-controllers/calxeda-ddr-ctrlr.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- incorrect DRAM timing values can describe unsafe controller programming even though the schema only checks shape and ranges.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, reg, interrupts`, optional top-level properties include `none declared`, and compatible coverage is `calxeda,hb-ddr-ctrl, calxeda,ecx-2000-ddr-ctrl`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/calxeda-ddr-ctrlr.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/calxeda-ddr-ctrlr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/canaan,k210-sram.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/canaan,k210-sram.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/canaan,k210-sram.yaml`, a memory-controller devicetree binding. The schema title is `Canaan K210 SRAM memory controller`. Description signal from the file: The Canaan K210 SRAM memory controller is responsible for the system's 8 MiB of SRAM. The controller is initialised by the bootloader, which configures its clocks, before OS bringup..

## Purpose
The file defines the devicetree ABI for `Canaan K210 SRAM memory controller`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: canaan,k210-sram.
- required node contract: compatible, clocks, clock-names.
- property surface: `compatible` (enum canaan,k210-sram), `clocks` (minItems=1, ordered-items=3), `clock-names` (minItems=1, ordered-items=3; ordered sram0, sram1, aisram).
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings.
Key dependency signals in this file are:
- maintainers: Conor Dooley <conor@kernel.org>.
- schema id: http://devicetree.org/schemas/memory-controllers/canaan,k210-sram.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- ordered `*-names` arrays must stay aligned with `reg`, `clocks`, `interrupts`, resets, DMA, or power-domain entries.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, clocks, clock-names`, optional top-level properties include `none declared`, and compatible coverage is `canaan,k210-sram`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/canaan,k210-sram.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/canaan,k210-sram.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,ddr4.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,ddr4.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,ddr4.yaml`, a memory-controller devicetree binding. The schema title is `DDR4 SDRAM compliant to JEDEC JESD79-4D`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `DDR4 SDRAM compliant to JEDEC JESD79-4D`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: jedec,ddr4.
- required node contract: compatible, density, io-width.
- property surface: `compatible` (ordered-items=2; ordered jedec,ddr4).
- referenced schemas: jedec,sdram-props.yaml#.
- Structural features: closed schema via `unevaluatedProperties: false`; 1 allOf composition block(s).
- Schema closure: unevaluatedProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- schema id: http://devicetree.org/schemas/memory-controllers/ddr/jedec,ddr4.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: jedec,sdram-props.yaml#.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- incorrect DRAM timing values can describe unsafe controller programming even though the schema only checks shape and ranges.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, density, io-width`, optional top-level properties include `none declared`, and compatible coverage is `jedec,ddr4`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,ddr4.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: jedec,sdram-props.yaml#.
- cross-check JEDEC density, IO width, frequency, and timing values against the memory datasheet.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,ddr4.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2-timings.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2-timings.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2-timings.yaml`, a memory-controller devicetree binding. The schema title is `LPDDR2 SDRAM AC timing parameters for a given speed-bin`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `LPDDR2 SDRAM AC timing parameters for a given speed-bin`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: jedec,lpddr2-timings.
- required node contract: compatible, min-freq, max-freq.
- property surface: `compatible` (const jedec,lpddr2-timings), `max-freq` (ref /schemas/types.yaml#/definitions/uint32), `min-freq` (ref /schemas/types.yaml#/definitions/uint32), `tCKESR` (ref /schemas/types.yaml#/definitions/uint32), `tDQSCK-max` (ref /schemas/types.yaml#/definitions/uint32), `tDQSCK-max-derated` (ref /schemas/types.yaml#/definitions/uint32), `tFAW` (ref /schemas/types.yaml#/definitions/uint32), `tRAS-max-ns` (Row active time in nano seconds.), `tRAS-min` (ref /schemas/types.yaml#/definitions/uint32), `tRCD` (ref /schemas/types.yaml#/definitions/uint32), `tRPab` (ref /schemas/types.yaml#/definitions/uint32), `tRRD` (ref /schemas/types.yaml#/definitions/uint32), `tRTP` (ref /schemas/types.yaml#/definitions/uint32), `tWR` (ref /schemas/types.yaml#/definitions/uint32), `tWTR` (ref /schemas/types.yaml#/definitions/uint32), `tXP` (ref /schemas/types.yaml#/definitions/uint32), and 3 more.
- referenced schemas: /schemas/types.yaml#/definitions/uint32.
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- schema id: http://devicetree.org/schemas/memory-controllers/ddr/jedec,lpddr2-timings.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/uint32.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- incorrect DRAM timing values can describe unsafe controller programming even though the schema only checks shape and ranges.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, min-freq, max-freq`, optional top-level properties include `tCKESR, tDQSCK-max, tDQSCK-max-derated, tFAW, tRAS-max-ns, tRAS-min, tRCD, tRPab, tRRD, tRTP, tWR, tWTR, tXP, tZQCL, tZQCS, tZQinit`, and compatible coverage is `jedec,lpddr2-timings`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2-timings.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/uint32.
- cross-check JEDEC density, IO width, frequency, and timing values against the memory datasheet.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2-timings.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2.yaml`, a memory-controller devicetree binding. The schema title is `LPDDR2 SDRAM compliant to JEDEC JESD209-2`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `LPDDR2 SDRAM compliant to JEDEC JESD209-2`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: elpida,ECB240ABACN, elpida,B8132B2PB-6D-F, jedec,lpddr2-nvm, jedec,lpddr2-s2, jedec,lpddr2-s4.
- required node contract: compatible, density, io-width.
- property surface: `compatible`, `revision-id1` (ref /schemas/types.yaml#/definitions/uint32; maximum=255), `revision-id2` (ref /schemas/types.yaml#/definitions/uint32; maximum=255), `tRRD-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tWTR-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tXP-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tRTP-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tCKE-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tRPab-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tRCD-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tWR-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tRASmin-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tCKESR-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16), `tFAW-min-tck` (ref /schemas/types.yaml#/definitions/uint32; maximum=16).
- child-node patterns: ^lpddr2-timings.
- referenced schemas: jedec,sdram-props.yaml#, /schemas/types.yaml#/definitions/uint32, jedec,lpddr2-timings.yaml.
- Structural features: patternProperties: ^lpddr2-timings; closed schema via `unevaluatedProperties: false`; 1 allOf composition block(s).
- Schema closure: unevaluatedProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- schema id: http://devicetree.org/schemas/memory-controllers/ddr/jedec,lpddr2.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: jedec,sdram-props.yaml#, /schemas/types.yaml#/definitions/uint32, jedec,lpddr2-timings.yaml.
- pattern children: ^lpddr2-timings.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- incorrect DRAM timing values can describe unsafe controller programming even though the schema only checks shape and ranges.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, density, io-width`, optional top-level properties include `revision-id1, revision-id2, tRRD-min-tck, tWTR-min-tck, tXP-min-tck, tRTP-min-tck, tCKE-min-tck, tRPab-min-tck, tRCD-min-tck, tWR-min-tck, tRASmin-min-tck, tCKESR-min-tck, tFAW-min-tck`, and compatible coverage is `elpida,ECB240ABACN, elpida,B8132B2PB-6D-F, jedec,lpddr2-nvm, jedec,lpddr2-s2, jedec,lpddr2-s4`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: jedec,sdram-props.yaml#, /schemas/types.yaml#/definitions/uint32, jedec,lpddr2-timings.yaml.
- cross-check JEDEC density, IO width, frequency, and timing values against the memory datasheet.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr3-timings.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr3-timings.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr3-timings.yaml`, a memory-controller devicetree binding. The schema title is `LPDDR3 SDRAM AC timing parameters for a given speed-bin`. The file relies on its title, compatible values, property constraints, and examples rather than a long prose description.

## Purpose
The file defines the devicetree ABI for `LPDDR3 SDRAM AC timing parameters for a given speed-bin`. It tells dt-schema which node shape is valid, which resources the Linux driver can expect at probe time, and which child graph or memory subnodes are legal. The binding is declarative: its practical API is the set of properties, compatible strings, resource ordering rules, and referenced common schemas accepted for DTS authors.

## Important APIs, Types, And Schema Surface
- compatible strings: jedec,lpddr3-timings.
- required node contract: compatible, min-freq, max-freq.
- property surface: `compatible` (const jedec,lpddr3-timings), `reg` (maxItems=1), `max-freq` (ref /schemas/types.yaml#/definitions/uint32), `min-freq` (ref /schemas/types.yaml#/definitions/uint32), `tCKE` (ref /schemas/types.yaml#/definitions/uint32), `tCKESR` (ref /schemas/types.yaml#/definitions/uint32), `tFAW` (ref /schemas/types.yaml#/definitions/uint32), `tMRD` (ref /schemas/types.yaml#/definitions/uint32), `tR2R-C2C` (ref /schemas/types.yaml#/definitions/uint32), `tRAS` (ref /schemas/types.yaml#/definitions/uint32), `tRC` (ref /schemas/types.yaml#/definitions/uint32), `tRCD` (ref /schemas/types.yaml#/definitions/uint32), `tRFC` (ref /schemas/types.yaml#/definitions/uint32), `tRPab` (ref /schemas/types.yaml#/definitions/uint32), `tRPpb` (ref /schemas/types.yaml#/definitions/uint32), `tRRD` (ref /schemas/types.yaml#/definitions/uint32), and 6 more.
- referenced schemas: /schemas/types.yaml#/definitions/uint32.
- Structural features: closed schema via `additionalProperties: false`.
- Schema closure: additionalProperties=false.

## Control Flow
Validation flow is schema-driven: dt-schema loads this document, applies composed `$ref` schemas first, checks `compatible`, validates required properties and ordered item arrays such as resource names, then descends into child graph or pattern nodes. no `if`/`then` runtime-style branches; validation is declarative through required lists, refs, enums, and item counts. The file includes 1 example block(s), which act as executable fixtures for schema validation and show the intended node shape.

## State And Persistence Behavior
This YAML file has no executable runtime state, persistence layer, or mutable kernel data structure. Its persistent behavior is the ABI it defines for DTS files: required properties, ordered resource names, graph topology, phandles, and numeric constraints become the stable contract consumed by dt-schema and by Linux drivers at probe time.

## Dependencies And Integration Points
The binding integrates with devicetree memory-controller description, firmware-provided memory topology/timing data, child chip-select or SDRAM timing nodes where present, and platform drivers that match the declared `compatible` strings. Its `$ref` dependencies make the schema part of a wider validation graph rather than a standalone checker.
Key dependency signals in this file are:
- maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- schema id: http://devicetree.org/schemas/memory-controllers/ddr/jedec,lpddr3-timings.yaml#.
- meta-schema: http://devicetree.org/meta-schemas/core.yaml#.
- references: /schemas/types.yaml#/definitions/uint32.

## Risks And Edge Cases
- missing or misspelled required properties will fail dt_binding_check or prevent the platform driver from acquiring resources.
- compatible fallback ordering is ABI-sensitive and must match driver tables and SoC-specific resource counts.
- changes in referenced common schemas can tighten validation for this binding.
- incorrect DRAM timing values can describe unsafe controller programming even though the schema only checks shape and ranges.
- Numeric and array constraints should be treated as ABI, not style. In this file the required set is `compatible, min-freq, max-freq`, optional top-level properties include `reg, tCKE, tCKESR, tFAW, tMRD, tR2R-C2C, tRAS, tRC, tRCD, tRFC, tRPab, tRPpb, tRRD, tRTP, tW2W-C2C, tWR, and 3 more`, and compatible coverage is `jedec,lpddr3-timings`.

## Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr3-timings.yaml` should parse this YAML and validate the schema and any inline examples.
- run `make dtbs_check` against board DTS files that instantiate this binding.
- the example block should compile through dtc with the included dt-bindings headers available.
- dt-schema should resolve referenced schemas: /schemas/types.yaml#/definitions/uint32.
- cross-check JEDEC density, IO width, frequency, and timing values against the memory datasheet.
- Review any driver binding changes against existing in-tree DTS users before tightening enums, maxItems, or required properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr3-timings.yaml -->
