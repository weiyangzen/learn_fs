<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/realtek,rtl9301-i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/realtek,rtl9301-i2c.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/realtek,rtl9301-i2c.yaml` is a I2C controller devicetree binding schema titled "Realtek RTL I2C Controller". RTL9300 SoCs have two I2C controllers. Each of these has an SCL line (which if not-used for SCL can be a GPIO). There are 8 common SDA lines that can be assigned to either I2C controller. RTL9310 SoCs have equal capabilities but support 12 common SDA lines which can be assigned to either I2C controller. RTL9607C SoCs have equal capabilities but each controller only supports 1 SCL/SDA line.
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/i2c/realtek,rtl9301-i2c.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Chris Packham <chris.packham@alliedtelesis.co.nz>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `realtek,rtl9302b-i2c`, `realtek,rtl9302c-i2c`, `realtek,rtl9303-i2c`, `realtek,rtl9301-i2c`, `realtek,rtl9311-i2c`, `realtek,rtl9312-i2c`, `realtek,rtl9313-i2c`, `realtek,rtl9310-i2c`, `realtek,rtl9607-i2c`.
- Required top-level properties: `compatible`, `reg`.
- Top-level schema references: `/schemas/types.yaml#/definitions/uint32`, `/schemas/i2c/i2c-controller.yaml`.
- Child/pattern node schemas: `^i2c@[0-9ab]$`.
- Key property definitions:
  - `compatible`: structured schema with nested alternatives/items.
  - `reg`: structured schema with nested alternatives/items.
  - `clocks`: maxItems 1.
  - `#address-cells`: constant `1`.
  - `#size-cells`: constant `0`.
  - `realtek,scl`: references `/schemas/types.yaml#/definitions/uint32`; allowed values `0`, `1`; The SCL line number of this I2C controller..

## Control Flow

1. Kernel build or developer tooling invokes `dt_binding_check`/`dtbs_check` over this schema and matching DTS nodes.
2. The schema first applies the declared meta-schema and any `allOf`/`$ref` base schemas, then validates local `properties`, `required`, `patternProperties`, and property-count constraints.
3. Compatible strings, node names, register cells, clocks, interrupts, GPIOs, supplies, and child nodes are checked structurally; any `if`/`then`/`else`, `oneOf`, or dependency blocks further narrow the accepted combinations.
4. Examples embedded in the binding are compiled as miniature DTS fragments and validated against the same schema.
This file contains conditional or compositional validation blocks, so the effective allowed properties can depend on compatible value, child-node shape, or the presence of peer properties. Detected conditional/dependency markers: 6.

## State And Persistence Behavior

The file has no runtime state and performs no persistence. Its persistent effect is contractual: once DTS files use this binding, the compatible strings, property names, child-node layout, and examples become ABI-like data consumed by boot firmware, the kernel, and validation tooling. Changes that remove accepted compatibles, tighten required properties, or alter cell layouts can break existing device trees even though no code executes here.
Unknown property policy is `additionalProperties: False` and `unevaluatedProperties: <unspecified>`, so extensions are governed by those flags plus referenced schemas.

## Dependencies

- YAML 1.2 and the devicetree core meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Referenced schema `/schemas/types.yaml#/definitions/uint32`.
- Referenced schema `/schemas/i2c/i2c-controller.yaml`.
- 1 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

Linux devicetree validation for I2C adapter, mux, gate, tunnel, arbitration, or bitbang nodes; the I2C core binding `/schemas/i2c/i2c-controller.yaml` or `/schemas/i2c/i2c-mux.yaml` when referenced; common clock framework phandle/name validation
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, reg) will fail schema validation and may also prevent the kernel driver from probing.
- Conditional `if`/`then`/`oneOf` constraints can reject combinations that look locally valid unless tested against the full schema.
- Clock ordering and `clock-names` mismatches can pass simple DTS review but fail runtime probe or timing setup.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/realtek,rtl9301-i2c.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
- Add or preserve negative schema tests mentally during review for each conditional path: unsupported compatibles should reject gated properties and supported compatibles should accept them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/realtek,rtl9301-i2c.yaml -->
