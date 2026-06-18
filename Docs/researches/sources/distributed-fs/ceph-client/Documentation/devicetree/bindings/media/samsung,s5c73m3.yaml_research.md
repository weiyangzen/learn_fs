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
