# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/arm,malidp.yaml

## Purpose
Arm Mali Display Processor (Mali-DP) is a DRM/display controller binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `arm,malidp.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The following bindings apply to a family of Display Processors sold as licensable IP by ARM Ltd. The bindings describe the Mali DP500, DP550 and DP650 processors that offer multiple composition layers, support for rotation and scaling output.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/display/arm,malidp.yaml#`, top-level `compatible` values `arm,mali-dp500`, `arm,mali-dp550`, `arm,mali-dp650`, required properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `port`, `arm,malidp-output-port-lines`, and top-level properties `compatible`, `reg`, `interrupts`, `interrupt-names`, `clock-names`, `clocks`, `memory-region`, `arm,malidp-output-port-lines`, `arm,malidp-arqos-value`, `port`.
Key property contracts include: `compatible` (enum `arm,mali-dp500`, `arm,mali-dp550`, `arm,mali-dp650`); `reg` (maxItems=1); `interrupts` (declared by schema); `interrupt-names` (declared by schema); `clock-names` (declared by schema); `clocks` (declared by schema); `arm,malidp-output-port-lines` (ref `/schemas/types.yaml#/definitions/uint8-array`; Number of output lines/bits for each colour channel.); `arm,malidp-arqos-value` (ref `/schemas/types.yaml#/definitions/uint32`; Quality-of-Service value for the display engine FIFOs, to write into the RQOS register of the DP500. See the ARM Mali-DP500 TRM for details on the encoding. If omitted, the RQOS register will not be changed.); `port` (ref `/schemas/graph.yaml#/properties/port`; Output endpoint of the controller, connecting the LCD panel signals.).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the DRM graph/OF graph endpoint model for connecting encoders, bridges, panels, PHYs, mixers, or display engines; driver matching through compatible strings such as `arm,mali-dp500`, `arm,mali-dp550`, `arm,mali-dp650`; provider bindings for `clocks`, `clock-names`, `interrupts`, `interrupt-names`, `port`, `memory-region`.
Referenced shared schemas include `/schemas/types.yaml#/definitions/uint8-array`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/graph.yaml#/properties/port`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- graph endpoint numbering and `remote-endpoint` links must match the adjacent display component or the DRM pipeline can bind incompletely
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/display/arm,malidp.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- boot/display smoke tests should confirm the DRM component graph binds all endpoints and exposes the expected connector or panel
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (119 lines). Maintainers listed by the binding: `Liviu Dudau <Liviu.Dudau@arm.com>`, `Andre Przywara <andre.przywara@arm.com>`.
