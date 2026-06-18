<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/silabs,cp2112.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/silabs,cp2112.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/silabs,cp2112.yaml` is a I2C controller devicetree binding schema titled "CP2112 HID USB to SMBus/I2C Bridge". The CP2112 is a USB HID device which includes an integrated I2C controller and 8 GPIO pins. Its GPIO pins can each be configured as inputs, open-drain outputs, or push-pull outputs.
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/i2c/silabs,cp2112.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Danny Kaehn <danny.kaehn@plexus.com>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `usb10c4,ea90`.
- Required top-level properties: `compatible`, `reg`.
- Top-level schema references: `/schemas/i2c/i2c-controller.yaml#`.
- Child/pattern node schemas: `-hog(-[0-9]+)?$`.
- Key property definitions:
  - `compatible`: constant `usb10c4,ea90`.
  - `reg`: maxItems 1; The USB port number.
  - `interrupt-controller` is fixed to True.
  - `#interrupt-cells`: constant `2`.
  - `gpio-controller` is fixed to True.
  - `#gpio-cells`: constant `2`.
  - `gpio-line-names`: maxItems 8; minItems 1.
  - `i2c`: references `/schemas/i2c/i2c-controller.yaml#`; The SMBus/I2C controller node for the CP2112.

## Control Flow

1. Kernel build or developer tooling invokes `dt_binding_check`/`dtbs_check` over this schema and matching DTS nodes.
2. The schema first applies the declared meta-schema and any `allOf`/`$ref` base schemas, then validates local `properties`, `required`, `patternProperties`, and property-count constraints.
3. Compatible strings, node names, register cells, clocks, interrupts, GPIOs, supplies, and child nodes are checked structurally; any `if`/`then`/`else`, `oneOf`, or dependency blocks further narrow the accepted combinations.
4. Examples embedded in the binding are compiled as miniature DTS fragments and validated against the same schema.
The binding is mostly declarative: validation is driven by required properties and direct property schemas rather than runtime branches.

## State And Persistence Behavior

The file has no runtime state and performs no persistence. Its persistent effect is contractual: once DTS files use this binding, the compatible strings, property names, child-node layout, and examples become ABI-like data consumed by boot firmware, the kernel, and validation tooling. Changes that remove accepted compatibles, tighten required properties, or alter cell layouts can break existing device trees even though no code executes here.
Unknown property policy is `additionalProperties: False` and `unevaluatedProperties: <unspecified>`, so extensions are governed by those flags plus referenced schemas.

## Dependencies

- YAML 1.2 and the devicetree core meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Referenced schema `/schemas/i2c/i2c-controller.yaml#`.
- 1 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

Linux devicetree validation for I2C adapter, mux, gate, tunnel, arbitration, or bitbang nodes; the I2C core binding `/schemas/i2c/i2c-controller.yaml` or `/schemas/i2c/i2c-mux.yaml` when referenced; interrupt-controller and IRQ wiring validation; GPIO descriptor lookup and polarity/open-drain semantics
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, reg) will fail schema validation and may also prevent the kernel driver from probing.
- Interrupt cell count, interrupt names, or interrupt-controller flags must match the interrupt provider and driver expectations.
- GPIO polarity/open-drain/reset semantics are hardware-visible and can hold buses or devices in the wrong electrical state.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/silabs,cp2112.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/silabs,cp2112.yaml -->
