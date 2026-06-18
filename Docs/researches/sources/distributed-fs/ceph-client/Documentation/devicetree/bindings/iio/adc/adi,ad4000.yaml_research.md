<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4000.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4000.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4000.yaml` is a IIO ADC devicetree binding schema titled "Analog Devices AD4000 and similar Analog to Digital Converters". Analog Devices AD4000 family of Analog to Digital Converters with SPI support. Specifications can be found at: https://www.analog.com/media/en/technical-documentation/data-sheets/ad4000-4004-4008.pdf https://www.analog.com/media/en/technical-documentation/data-sheets/ad4001-4005.pdf https://www.analog.com/media/en/technical-documentation/data-sheets/ad4002-4006-4010.pdf https://www.analog.com/media/en/technical-documentation/data-sheets/ad4003-4007-4011.pdf https://www.analog.com/media/en/technical-documentation/da...
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/iio/adc/adi,ad4000.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Marcelo Schmitt <marcelo.schmitt@analog.com>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `adi,ad4000`, `adi,ad4001`, `adi,ad4002`, `adi,ad4003`, `adi,ad4020`, `adi,adaq4001`, `adi,adaq4003`, `adi,ad7687`, `adi,ad7691`, `adi,ad7942`, `adi,ad7946`, `adi,ad7983`, `adi,ad4004`, `adi,ad4008`, `adi,ad4005`, `adi,ad4006`, `adi,ad4010`, `adi,ad4007`, ....
- Required top-level properties: `compatible`, `reg`, `vdd-supply`, `vio-supply`, `ref-supply`.
- Top-level schema references: `/schemas/spi/spi-peripheral-props.yaml#`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint16`.
- Key property definitions:
  - `compatible`: structured schema with nested alternatives/items.
  - `reg`: maxItems 1.
  - `interrupts`: maxItems 1; The SDO pin can also function as a busy indicator. This node should be connected to an interrupt that is triggered when the SDO line goes low while the SDI line is high and the CNV line is low ("3-wire" mode) or the SDI ....
  - `vdd-supply`: A 1.8V supply that powers the chip (VDD)..
  - `spi-max-frequency`: declared without extra local constraints.
  - `adi,sdi-pin`: references `/schemas/types.yaml#/definitions/string`; allowed values `high`, `low`, `cs`, `sdi`; Describes how the ADC SDI pin is wired. A value of "sdi" indicates that the ADC SDI is connected to host SDO. "high" indicates that the ADC SDI pin is hard-wired to logic high (VIO). "low" indicates that it is hard-wired....
  - `#daisy-chained-devices` is fixed to True.
  - `vio-supply`: A 1.8V to 5.5V supply for the digital inputs and outputs (VIO)..
  - `ref-supply`: A 2.5 to 5V supply for the external reference voltage (REF)..
  - `cnv-gpios`: maxItems 1; When provided, this property indicates the GPIO that is connected to the CNV pin..

## Control Flow

1. Kernel build or developer tooling invokes `dt_binding_check`/`dtbs_check` over this schema and matching DTS nodes.
2. The schema first applies the declared meta-schema and any `allOf`/`$ref` base schemas, then validates local `properties`, `required`, `patternProperties`, and property-count constraints.
3. Compatible strings, node names, register cells, clocks, interrupts, GPIOs, supplies, and child nodes are checked structurally; any `if`/`then`/`else`, `oneOf`, or dependency blocks further narrow the accepted combinations.
4. Examples embedded in the binding are compiled as miniature DTS fragments and validated against the same schema.
This file contains conditional or compositional validation blocks, so the effective allowed properties can depend on compatible value, child-node shape, or the presence of peer properties. Detected conditional/dependency markers: 8.

## State And Persistence Behavior

The file has no runtime state and performs no persistence. Its persistent effect is contractual: once DTS files use this binding, the compatible strings, property names, child-node layout, and examples become ABI-like data consumed by boot firmware, the kernel, and validation tooling. Changes that remove accepted compatibles, tighten required properties, or alter cell layouts can break existing device trees even though no code executes here.
Unknown property policy is `additionalProperties: <unspecified>` and `unevaluatedProperties: False`, so extensions are governed by those flags plus referenced schemas.

## Dependencies

- YAML 1.2 and the devicetree core meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Referenced schema `/schemas/spi/spi-peripheral-props.yaml#`.
- Referenced schema `/schemas/types.yaml#/definitions/string`.
- Referenced schema `/schemas/types.yaml#/definitions/uint16`.
- 2 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

IIO ADC driver channel discovery and per-channel schema validation; common ADC channel properties such as `reg`, differential inputs, labels, references, supplies, and SPI/I2C transport constraints; interrupt-controller and IRQ wiring validation; regulator supply lookup by the corresponding kernel driver; GPIO descriptor lookup and polarity/open-drain semantics
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, reg, vdd-supply, vio-supply, ref-supply) will fail schema validation and may also prevent the kernel driver from probing.
- Conditional `if`/`then`/`oneOf` constraints can reject combinations that look locally valid unless tested against the full schema.
- Interrupt cell count, interrupt names, or interrupt-controller flags must match the interrupt provider and driver expectations.
- GPIO polarity/open-drain/reset semantics are hardware-visible and can hold buses or devices in the wrong electrical state.
- Supply phandle omissions or wrong regulator names can defer or fail probe and may affect power sequencing.
- IIO channel numbering, differential input pairs, mount matrices, and reference supplies must match board wiring; schema validation cannot prove analog correctness.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/iio/adc/adi,ad4000.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
- Add or preserve negative schema tests mentally during review for each conditional path: unsupported compatibles should reject gated properties and supported compatibles should accept them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4000.yaml -->
