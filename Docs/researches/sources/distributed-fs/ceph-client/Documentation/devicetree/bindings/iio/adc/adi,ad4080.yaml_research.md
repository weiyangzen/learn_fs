<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4080.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4080.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4080.yaml` is a IIO ADC devicetree binding schema titled "Analog Devices AD4080 20-Bit, 40 MSPS, Differential SAR ADC". The AD4080 is a high speed, low noise, low distortion, 20-bit, Easy Drive, successive approximation register (SAR) analog-to-digital converter (ADC). Maintaining high performance (signal-to-noise and distortion (SINAD) ratio > 90 dBFS) at signal frequencies in excess of 1 MHz enables the AD4080 to service a wide variety of precision, wide bandwidth data acquisition applications. https://www.analog.com/media/en/technical-documentation/data-sheets/ad4080.pdf
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/iio/adc/adi,ad4080.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Antoniu Miclaus <antoniu.miclaus@analog.com>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `adi,ad4080`, `adi,ad4081`, `adi,ad4082`, `adi,ad4083`, `adi,ad4084`, `adi,ad4085`, `adi,ad4086`, `adi,ad4087`, `adi,ad4088`.
- Required top-level properties: `compatible`, `reg`, `clocks`, `clock-names`, `vdd33-supply`, `vrefin-supply`.
- Top-level schema references: `/schemas/spi/spi-peripheral-props.yaml#`, `/schemas/types.yaml#/definitions/uint32`.
- Key property definitions:
  - `compatible`: allowed values `adi,ad4080`, `adi,ad4081`, `adi,ad4082`, `adi,ad4083`, `adi,ad4084`, `adi,ad4085`, `adi,ad4086`, `adi,ad4087`, ....
  - `reg`: maxItems 1.
  - `clocks`: maxItems 1.
  - `clock-names`: structured schema with nested alternatives/items.
  - `spi-max-frequency`: Configuration of the SPI bus..
  - `vdd33-supply` is fixed to True.
  - `vdd11-supply` is fixed to True.
  - `vddldo-supply` is fixed to True.
  - `iovdd-supply` is fixed to True.
  - `vrefin-supply` is fixed to True.

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
- Referenced schema `/schemas/spi/spi-peripheral-props.yaml#`.
- Referenced schema `/schemas/types.yaml#/definitions/uint32`.
- 1 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

IIO ADC driver channel discovery and per-channel schema validation; common ADC channel properties such as `reg`, differential inputs, labels, references, supplies, and SPI/I2C transport constraints; common clock framework phandle/name validation; regulator supply lookup by the corresponding kernel driver
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, reg, clocks, clock-names, vdd33-supply, vrefin-supply) will fail schema validation and may also prevent the kernel driver from probing.
- Clock ordering and `clock-names` mismatches can pass simple DTS review but fail runtime probe or timing setup.
- Supply phandle omissions or wrong regulator names can defer or fail probe and may affect power sequencing.
- IIO channel numbering, differential input pairs, mount matrices, and reference supplies must match board wiring; schema validation cannot prove analog correctness.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/iio/adc/adi,ad4080.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adi,ad4080.yaml -->
