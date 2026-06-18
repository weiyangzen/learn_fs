<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/hpe,gxp-i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/hpe,gxp-i2c.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/hpe,gxp-i2c.yaml` is a I2C controller devicetree binding schema titled "HPE GXP SoC I2C Controller". This file is the dt-schema contract for `HPE GXP SoC I2C Controller`.
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/i2c/hpe,gxp-i2c.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Nick Hawkins <nick.hawkins@hpe.com>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `hpe,gxp-i2c`.
- Required top-level properties: `compatible`, `reg`, `interrupts`.
- Top-level schema references: `/schemas/i2c/i2c-controller.yaml#`, `/schemas/types.yaml#/definitions/phandle`.
- Key property definitions:
  - `compatible`: constant `hpe,gxp-i2c`.
  - `reg`: maxItems 1.
  - `interrupts`: maxItems 1.
  - `clock-frequency`: declared without extra local constraints.
  - `hpe,sysreg`: references `/schemas/types.yaml#/definitions/phandle`; Phandle to the global status and enable interrupt registers shared between each I2C engine controller instance. It enables the I2C engine controller to act as both a master or slave by being able to arm and respond to in....

## Control Flow

1. Kernel build or developer tooling invokes `dt_binding_check`/`dtbs_check` over this schema and matching DTS nodes.
2. The schema first applies the declared meta-schema and any `allOf`/`$ref` base schemas, then validates local `properties`, `required`, `patternProperties`, and property-count constraints.
3. Compatible strings, node names, register cells, clocks, interrupts, GPIOs, supplies, and child nodes are checked structurally; any `if`/`then`/`else`, `oneOf`, or dependency blocks further narrow the accepted combinations.
4. Examples embedded in the binding are compiled as miniature DTS fragments and validated against the same schema.
This file contains conditional or compositional validation blocks, so the effective allowed properties can depend on compatible value, child-node shape, or the presence of peer properties. Detected conditional/dependency markers: 0.

## State And Persistence Behavior

The file has no runtime state and performs no persistence. Its persistent effect is contractual: once DTS files use this binding, the compatible strings, property names, child-node layout, and examples become ABI-like data consumed by boot firmware, the kernel, and validation tooling. Changes that remove accepted compatibles, tighten required properties, or alter cell layouts can break existing device trees even though no code executes here.
Unknown property policy is `additionalProperties: <unspecified>` and `unevaluatedProperties: False`, so extensions are governed by those flags plus referenced schemas.

## Dependencies

- YAML 1.2 and the devicetree core meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Referenced schema `/schemas/i2c/i2c-controller.yaml#`.
- Referenced schema `/schemas/types.yaml#/definitions/phandle`.
- 1 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

Linux devicetree validation for I2C adapter, mux, gate, tunnel, arbitration, or bitbang nodes; the I2C core binding `/schemas/i2c/i2c-controller.yaml` or `/schemas/i2c/i2c-mux.yaml` when referenced; interrupt-controller and IRQ wiring validation; common clock framework phandle/name validation
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, reg, interrupts) will fail schema validation and may also prevent the kernel driver from probing.
- Conditional `if`/`then`/`oneOf` constraints can reject combinations that look locally valid unless tested against the full schema.
- Interrupt cell count, interrupt names, or interrupt-controller flags must match the interrupt provider and driver expectations.
- Clock ordering and `clock-names` mismatches can pass simple DTS review but fail runtime probe or timing setup.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/hpe,gxp-i2c.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
- Add or preserve negative schema tests mentally during review for each conditional path: unsupported compatibles should reject gated properties and supported compatibles should accept them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/hpe,gxp-i2c.yaml -->
