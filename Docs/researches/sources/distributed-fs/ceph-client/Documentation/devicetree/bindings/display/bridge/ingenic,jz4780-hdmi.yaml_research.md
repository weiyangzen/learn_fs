# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/ingenic,jz4780-hdmi.yaml

## Purpose
Ingenic JZ4780 HDMI Transmitter is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `ingenic,jz4780-hdmi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The HDMI Transmitter in the Ingenic JZ4780 is a Synopsys DesignWare HDMI 1.4 TX controller IP with accompanying PHY IP.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/ingenic,jz4780-hdmi.yaml#`, top-level `compatible` values `ingenic,jz4780-dw-hdmi`, required properties `compatible`, `clocks`, `clock-names`, `ports`, `reg-io-width`, and top-level properties `compatible`, `reg-io-width`, `clocks`, `clock-names`, `ports`.
Key property contracts include: `compatible` (const `ingenic,jz4780-dw-hdmi`); `clocks` (maxItems=2); `clock-names` (maxItems=2); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 1 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `ingenic,jz4780-dw-hdmi`; provider bindings for `clocks`, `clock-names`, `ports`.
Referenced shared schemas include `synopsys,dw-hdmi.yaml#`, `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/ingenic,jz4780-hdmi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (84 lines). Maintainers listed by the binding: `H. Nikolaus Schaller <hns@goldelico.com>`.
