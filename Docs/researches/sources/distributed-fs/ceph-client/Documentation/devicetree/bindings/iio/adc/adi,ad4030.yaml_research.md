<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4030.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4030.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4030.yaml` is a IIO ADC devicetree binding schema titled "Analog Devices AD4030 and AD4630 ADC families". Analog Devices AD4030 single channel and AD4630/AD4632 dual channel precision SAR ADC families * https://www.analog.com/media/en/technical-documentation/data-sheets/ad4030-24-4032-24.pdf * https://www.analog.com/media/en/technical-documentation/data-sheets/ad4630-24_ad4632-24.pdf * https://www.analog.com/media/en/technical-documentation/data-sheets/ad4630-16-4632-16.pdf * https://www.analog.com/media/en/technical-documentation/data-sheets/adaq4216.pdf * https://www.analog.com/media/en/technical-documentation/data-s...
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/iio/adc/adi,ad4030.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Michael Hennerich <michael.hennerich@analog.com>, Nuno Sa <nuno.sa@analog.com>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `adi,ad4030-24`, `adi,ad4032-24`, `adi,ad4630-16`, `adi,ad4630-24`, `adi,ad4632-16`, `adi,ad4632-24`, `adi,adaq4216`, `adi,adaq4224`.
- Required top-level properties: `compatible`, `reg`, `vdd-5v-supply`, `vdd-1v8-supply`, `vio-supply`, `cnv-gpios`.
- Top-level schema references: `/schemas/spi/spi-peripheral-props.yaml#`.
- Key property definitions:
  - `compatible`: allowed values `adi,ad4030-24`, `adi,ad4032-24`, `adi,ad4630-16`, `adi,ad4630-24`, `adi,ad4632-16`, `adi,ad4632-24`, `adi,adaq4216`, `adi,adaq4224`.
  - `reg`: maxItems 1.
  - `interrupts`: maxItems 1; The BUSY pin is used to signal that the conversions results are available to be transferred when in SPI Clocking Mode. This nodes should be connected to an interrupt that is triggered when the BUSY line goes low..
  - `interrupt-names`: constant `busy`.
  - `reset-gpios`: maxItems 1; The Reset Input (/RST). Used for asynchronous device reset..
  - `spi-max-frequency`: declared without extra local constraints.
  - `spi-rx-bus-width`: maxItems 2.
  - `vdd-5v-supply` is fixed to True.
  - `vdd-1v8-supply` is fixed to True.
  - `vio-supply` is fixed to True.

## Control Flow

1. Kernel build or developer tooling invokes `dt_binding_check`/`dtbs_check` over this schema and matching DTS nodes.
2. The schema first applies the declared meta-schema and any `allOf`/`$ref` base schemas, then validates local `properties`, `required`, `patternProperties`, and property-count constraints.
3. Compatible strings, node names, register cells, clocks, interrupts, GPIOs, supplies, and child nodes are checked structurally; any `if`/`then`/`else`, `oneOf`, or dependency blocks further narrow the accepted combinations.
4. Examples embedded in the binding are compiled as miniature DTS fragments and validated against the same schema.
This file contains conditional or compositional validation blocks, so the effective allowed properties can depend on compatible value, child-node shape, or the presence of peer properties. Detected conditional/dependency markers: 4.

## State And Persistence Behavior

The file has no runtime state and performs no persistence. Its persistent effect is contractual: once DTS files use this binding, the compatible strings, property names, child-node layout, and examples become ABI-like data consumed by boot firmware, the kernel, and validation tooling. Changes that remove accepted compatibles, tighten required properties, or alter cell layouts can break existing device trees even though no code executes here.
Unknown property policy is `additionalProperties: <unspecified>` and `unevaluatedProperties: False`, so extensions are governed by those flags plus referenced schemas.

## Dependencies

- YAML 1.2 and the devicetree core meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Referenced schema `/schemas/spi/spi-peripheral-props.yaml#`.
- 3 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

IIO ADC driver channel discovery and per-channel schema validation; common ADC channel properties such as `reg`, differential inputs, labels, references, supplies, and SPI/I2C transport constraints; interrupt-controller and IRQ wiring validation; regulator supply lookup by the corresponding kernel driver; GPIO descriptor lookup and polarity/open-drain semantics
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, reg, vdd-5v-supply, vdd-1v8-supply, vio-supply, cnv-gpios) will fail schema validation and may also prevent the kernel driver from probing.
- Conditional `if`/`then`/`oneOf` constraints can reject combinations that look locally valid unless tested against the full schema.
- Interrupt cell count, interrupt names, or interrupt-controller flags must match the interrupt provider and driver expectations.
- GPIO polarity/open-drain/reset semantics are hardware-visible and can hold buses or devices in the wrong electrical state.
- Supply phandle omissions or wrong regulator names can defer or fail probe and may affect power sequencing.
- IIO channel numbering, differential input pairs, mount matrices, and reference supplies must match board wiring; schema validation cannot prove analog correctness.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/iio/adc/adi,ad4030.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
- Add or preserve negative schema tests mentally during review for each conditional path: unsupported compatibles should reject gated properties and supported compatibles should accept them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4030.yaml -->
