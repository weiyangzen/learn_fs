<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4134.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4134.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4134.yaml` is a IIO ADC devicetree binding schema titled "Analog Devices AD4134 ADC". The AD4134 is a quad channel, low noise, simultaneous sampling, precision analog-to-digital converter (ADC). Specifications can be found at: https://www.analog.com/media/en/technical-documentation/data-sheets/ad4134.pdf
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/iio/adc/adi,ad4134.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Marcelo Schmitt <marcelo.schmitt@analog.com>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `adi,ad4134`.
- Required top-level properties: `compatible`, `reg`, `avdd5-supply`, `dvdd5-supply`, `iovdd-supply`, `refin-supply`, `clocks`, `clock-names`.
- Top-level schema references: `/schemas/spi/spi-peripheral-props.yaml#`, `/schemas/regulator/regulator.yaml#`, `/schemas/types.yaml#/definitions/string`.
- Key property definitions:
  - `compatible`: allowed values `adi,ad4134`.
  - `reg`: maxItems 1.
  - `clocks`: maxItems 1; Required external clock source. Can specify either a crystal or CMOS clock source. If an external crystal is set, connect the CLKSEL pin to IOVDD. Otherwise, connect the CLKSEL pin to IOGND and the external CMOS clock si....
  - `clock-names`: allowed values `xtal`, `clkin`.
  - `reset-gpios`: maxItems 1.
  - `spi-max-frequency`: declared without extra local constraints.
  - `avdd5-supply`: A 5V supply that powers the chip's analog circuitry..
  - `dvdd5-supply`: A 5V supply that powers the chip's digital circuitry..
  - `iovdd-supply`: A 1.8V supply that sets the logic levels for the digital interface pins..
  - `refin-supply`: A 4.096V or 5V supply that serves as reference for ADC conversions..

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
- Referenced schema `/schemas/spi/spi-peripheral-props.yaml#`.
- Referenced schema `/schemas/regulator/regulator.yaml#`.
- Referenced schema `/schemas/types.yaml#/definitions/string`.
- 1 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

IIO ADC driver channel discovery and per-channel schema validation; common ADC channel properties such as `reg`, differential inputs, labels, references, supplies, and SPI/I2C transport constraints; common clock framework phandle/name validation; regulator supply lookup by the corresponding kernel driver; GPIO descriptor lookup and polarity/open-drain semantics
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, reg, avdd5-supply, dvdd5-supply, iovdd-supply, refin-supply) will fail schema validation and may also prevent the kernel driver from probing.
- Conditional `if`/`then`/`oneOf` constraints can reject combinations that look locally valid unless tested against the full schema.
- Clock ordering and `clock-names` mismatches can pass simple DTS review but fail runtime probe or timing setup.
- GPIO polarity/open-drain/reset semantics are hardware-visible and can hold buses or devices in the wrong electrical state.
- Supply phandle omissions or wrong regulator names can defer or fail probe and may affect power sequencing.
- IIO channel numbering, differential input pairs, mount matrices, and reference supplies must match board wiring; schema validation cannot prove analog correctness.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/iio/adc/adi,ad4134.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
- Add or preserve negative schema tests mentally during review for each conditional path: unsupported compatibles should reject gated properties and supported compatibles should accept them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4134.yaml -->
