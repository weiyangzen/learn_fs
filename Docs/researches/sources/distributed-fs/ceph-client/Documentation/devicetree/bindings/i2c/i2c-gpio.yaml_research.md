<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/i2c-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/i2c-gpio.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/i2c-gpio.yaml` is a I2C controller devicetree binding schema titled "GPIO bitbanged I2C". This file is the dt-schema contract for `GPIO bitbanged I2C`.
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/i2c/i2c-gpio.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Wolfram Sang <wsa@kernel.org>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `i2c-gpio`.
- Required top-level properties: `compatible`, `sda-gpios`, `scl-gpios`.
- Top-level schema references: `/schemas/i2c/i2c-controller.yaml#`.
- Key property definitions:
  - `compatible`: structured schema with nested alternatives/items.
  - `sda-gpios`: maxItems 1; gpio used for the sda signal, this should be flagged as active high using open drain with (GPIO_ACTIVE_HIGH|GPIO_OPEN_DRAIN) from <dt-bindings/gpio/gpio.h> since the signal is by definition open drain..
  - `scl-gpios`: maxItems 1; gpio used for the scl signal, this should be flagged as active high using open drain with (GPIO_ACTIVE_HIGH|GPIO_OPEN_DRAIN) from <dt-bindings/gpio/gpio.h> since the signal is by definition open drain..
  - `i2c-gpio,sda-output-only`: type `boolean`; sda as output only.
  - `i2c-gpio,scl-output-only`: type `boolean`; scl as output only.
  - `i2c-gpio,delay-us`: delay between GPIO operations (may depend on each platform).
  - `i2c-gpio,timeout-ms`: timeout to get data.
  - `gpios`: maxItems 2; minItems 2; sda and scl gpio, alternative for {sda,scl}-gpios.
  - `i2c-gpio,sda-open-drain`: type `boolean`; deprecated; this means that something outside of our control has put the GPIO line used for SDA into open drain mode, and that something is not the GPIO chip. It is essentially an inconsistency flag..
  - `i2c-gpio,scl-open-drain`: type `boolean`; deprecated; this means that something outside of our control has put the GPIO line used for SCL into open drain mode, and that something is not the GPIO chip. It is essentially an inconsistency flag..
- Dependency/mutual-exclusion rules are present for: `i2c-gpio,sda-has-no-pullup`, `i2c-gpio,scl-has-no-pullup`.

## Control Flow

1. Kernel build or developer tooling invokes `dt_binding_check`/`dtbs_check` over this schema and matching DTS nodes.
2. The schema first applies the declared meta-schema and any `allOf`/`$ref` base schemas, then validates local `properties`, `required`, `patternProperties`, and property-count constraints.
3. Compatible strings, node names, register cells, clocks, interrupts, GPIOs, supplies, and child nodes are checked structurally; any `if`/`then`/`else`, `oneOf`, or dependency blocks further narrow the accepted combinations.
4. Examples embedded in the binding are compiled as miniature DTS fragments and validated against the same schema.
This file contains conditional or compositional validation blocks, so the effective allowed properties can depend on compatible value, child-node shape, or the presence of peer properties. Detected conditional/dependency markers: 1.

## State And Persistence Behavior

The file has no runtime state and performs no persistence. Its persistent effect is contractual: once DTS files use this binding, the compatible strings, property names, child-node layout, and examples become ABI-like data consumed by boot firmware, the kernel, and validation tooling. Changes that remove accepted compatibles, tighten required properties, or alter cell layouts can break existing device trees even though no code executes here.
Unknown property policy is `additionalProperties: <unspecified>` and `unevaluatedProperties: False`, so extensions are governed by those flags plus referenced schemas.

## Dependencies

- YAML 1.2 and the devicetree core meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Referenced schema `/schemas/i2c/i2c-controller.yaml#`.

## Integration Points

Linux devicetree validation for I2C adapter, mux, gate, tunnel, arbitration, or bitbang nodes; the I2C core binding `/schemas/i2c/i2c-controller.yaml` or `/schemas/i2c/i2c-mux.yaml` when referenced; GPIO descriptor lookup and polarity/open-drain semantics
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, sda-gpios, scl-gpios) will fail schema validation and may also prevent the kernel driver from probing.
- Conditional `if`/`then`/`oneOf` constraints can reject combinations that look locally valid unless tested against the full schema.
- GPIO polarity/open-drain/reset semantics are hardware-visible and can hold buses or devices in the wrong electrical state.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/i2c-gpio.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
- Add or preserve negative schema tests mentally during review for each conditional path: unsupported compatibles should reject gated properties and supported compatibles should accept them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/i2c-gpio.yaml -->
