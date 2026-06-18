# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/bridge/cdns,dsi.yaml

## Purpose
Cadence DSI bridge is a DRM display bridge binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `cdns,dsi.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. CDNS DSI is a bridge device which converts DPI to DSI

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/bridge/cdns,dsi.yaml#`, top-level `compatible` values `cdns,dsi`, `ti,j721e-dsi`, required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `phys`, `phy-names`, `ports`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `phys`, `phy-names`, `interrupts`, `resets`, `reset-names`, `ports`.
Key property contracts include: `compatible` (enum `cdns,dsi`, `ti,j721e-dsi`); `reg` (minItems=1); `clocks` (declared by schema); `clock-names` (declared by schema); `phys` (maxItems=1); `phy-names` (const `dphy`); `interrupts` (maxItems=1); `resets` (maxItems=1); `reset-names` (const `dsi_p_rst`); `ports` (ref `/schemas/graph.yaml#/properties/ports`).
It has 2 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `cdns,dsi`, `ti,j721e-dsi`; provider bindings for `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `phys`, `phy-names`, `ports`.
Referenced shared schemas include `/schemas/graph.yaml#/properties/ports`, `/schemas/graph.yaml#/properties/port`, `../dsi-controller.yaml#`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `unevaluatedProperties: false` closes the schema after referenced common bindings are applied
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- reset-name ordering is part of the driver contract

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/bridge/cdns,dsi.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 2 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (180 lines). Maintainers listed by the binding: `Boris Brezillon <boris.brezillon@bootlin.com>`.
