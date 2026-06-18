<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adc.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adc.yaml` is a IIO ADC devicetree binding schema titled "IIO Common Properties for ADC Channels". A few properties are defined in a common way ADC channels.
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/iio/adc/adc.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Jonathan Cameron <jic23@kernel.org>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: not a top-level compatible binding.
- Node-name rule: `^channel(@[0-9a-f]+)?$`.
- Required top-level properties: none declared.
- Top-level schema references: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.
- Key property definitions:
  - `reg`: maxItems 1.
  - `$nodename`: A channel index should match reg..
  - `label`: Unique name to identify which channel this is..
  - `bipolar`: references `/schemas/types.yaml#/definitions/flag`; If provided, the channel is to be used in bipolar mode..
  - `diff-channels`: references `/schemas/types.yaml#/definitions/uint32-array`; maxItems 2; minItems 2; Many ADCs have dual Muxes to allow different input pins to be routed to both the positive and negative inputs of a differential ADC. The first value specifies the positive input pin, the second specifies the negative inp....
  - `single-channel`: references `/schemas/types.yaml#/definitions/uint32`; When devices combine single-ended and differential channels, allow the channel for a single element to be specified, independent of reg (as for differential channels). If this and diff-channels are not present reg shall ....
  - `common-mode-channel`: references `/schemas/types.yaml#/definitions/uint32`; Some ADCs have differential input pins that can be used to measure single-ended or pseudo-differential inputs. This property can be used in addition to single-channel to signal software that this channel is not different....
  - `settling-time-us`: Time between enabling the channel and first stable readings..
  - `oversampling-ratio`: references `/schemas/types.yaml#/definitions/uint32`; Oversampling is used as replacement of or addition to the low-pass filter. In some cases, the desired filtering characteristics are a function the device design and can interact with other characteristics such as settlin....

## Control Flow

1. Kernel build or developer tooling invokes `dt_binding_check`/`dtbs_check` over this schema and matching DTS nodes.
2. The schema first applies the declared meta-schema and any `allOf`/`$ref` base schemas, then validates local `properties`, `required`, `patternProperties`, and property-count constraints.
3. Compatible strings, node names, register cells, clocks, interrupts, GPIOs, supplies, and child nodes are checked structurally; any `if`/`then`/`else`, `oneOf`, or dependency blocks further narrow the accepted combinations.
4. Examples embedded in the binding are compiled as miniature DTS fragments and validated against the same schema.
This file contains conditional or compositional validation blocks, so the effective allowed properties can depend on compatible value, child-node shape, or the presence of peer properties. Detected conditional/dependency markers: 0.

## State And Persistence Behavior

The file has no runtime state and performs no persistence. Its persistent effect is contractual: once DTS files use this binding, the compatible strings, property names, child-node layout, and examples become ABI-like data consumed by boot firmware, the kernel, and validation tooling. Changes that remove accepted compatibles, tighten required properties, or alter cell layouts can break existing device trees even though no code executes here.
Unknown property policy is `additionalProperties: True` and `unevaluatedProperties: <unspecified>`, so extensions are governed by those flags plus referenced schemas.

## Dependencies

- YAML 1.2 and the devicetree core meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Referenced schema `/schemas/types.yaml#/definitions/flag`.
- Referenced schema `/schemas/types.yaml#/definitions/uint32-array`.
- Referenced schema `/schemas/types.yaml#/definitions/uint32`.

## Integration Points

IIO ADC driver channel discovery and per-channel schema validation; common ADC channel properties such as `reg`, differential inputs, labels, references, supplies, and SPI/I2C transport constraints
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Conditional `if`/`then`/`oneOf` constraints can reject combinations that look locally valid unless tested against the full schema.
- IIO channel numbering, differential input pairs, mount matrices, and reference supplies must match board wiring; schema validation cannot prove analog correctness.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/iio/adc/adc.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Add or preserve negative schema tests mentally during review for each conditional path: unsupported compatibles should reject gated properties and supported compatibles should accept them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/adc/adc.yaml -->
