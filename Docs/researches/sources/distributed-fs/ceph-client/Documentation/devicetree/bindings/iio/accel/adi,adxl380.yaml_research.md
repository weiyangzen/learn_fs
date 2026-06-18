<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/accel/adi,adxl380.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/accel/adi,adxl380.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/accel/adi,adxl380.yaml` is a IIO accelerometer devicetree binding schema titled "Analog Devices ADXL380/382 3-Axis Digital Accelerometer". The ADXL380/ADXL382 and ADXL318/ADXL319 are low noise density, low power, 3-axis accelerometers with selectable measurement ranges. The ADXL380 and ADXL318 support the ±4 g, ±8 g, and ±16 g ranges, while the ADXL382 and ADXL319 support ±15 g, ±30 g, and ±60 g ranges. https://www.analog.com/en/products/adxl318.html https://www.analog.com/en/products/adxl380.html
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/iio/accel/adi,adxl380.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Ramona Gradinariu <ramona.gradinariu@analog.com>, Antoniu Miclaus <antoniu.miclaus@analog.com>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `adi,adxl318`, `adi,adxl319`, `adi,adxl380`, `adi,adxl382`.
- Required top-level properties: `compatible`, `reg`, `interrupts`, `interrupt-names`, `vddio-supply`, `vsupply-supply`.
- Top-level schema references: `/schemas/spi/spi-peripheral-props.yaml#`.
- Key property definitions:
  - `compatible`: allowed values `adi,adxl318`, `adi,adxl319`, `adi,adxl380`, `adi,adxl382`.
  - `reg`: maxItems 1.
  - `interrupts`: maxItems 2; minItems 1.
  - `interrupt-names`: minItems 1.
  - `vddio-supply` is fixed to True.
  - `vsupply-supply` is fixed to True.

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
- 2 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

IIO accelerometer drivers and sensor child-node validation; bus-specific SPI/I2C core properties plus interrupt, regulator, and mount-matrix conventions; interrupt-controller and IRQ wiring validation; regulator supply lookup by the corresponding kernel driver
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, reg, interrupts, interrupt-names, vddio-supply, vsupply-supply) will fail schema validation and may also prevent the kernel driver from probing.
- Conditional `if`/`then`/`oneOf` constraints can reject combinations that look locally valid unless tested against the full schema.
- Interrupt cell count, interrupt names, or interrupt-controller flags must match the interrupt provider and driver expectations.
- Supply phandle omissions or wrong regulator names can defer or fail probe and may affect power sequencing.
- IIO channel numbering, differential input pairs, mount matrices, and reference supplies must match board wiring; schema validation cannot prove analog correctness.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/iio/accel/adi,adxl380.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
- Add or preserve negative schema tests mentally during review for each conditional path: unsupported compatibles should reject gated properties and supported compatibles should accept them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/accel/adi,adxl380.yaml -->
