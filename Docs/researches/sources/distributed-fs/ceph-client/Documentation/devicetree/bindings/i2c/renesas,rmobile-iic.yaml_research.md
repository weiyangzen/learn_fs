<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/renesas,rmobile-iic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/renesas,rmobile-iic.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/renesas,rmobile-iic.yaml` is a I2C controller devicetree binding schema titled "Renesas R-Mobile I2C Bus Interface (IIC)". This file is the dt-schema contract for `Renesas R-Mobile I2C Bus Interface (IIC)`.
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/i2c/renesas,rmobile-iic.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Wolfram Sang <wsa+renesas@sang-engineering.com>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `renesas,iic-r8a73a4`, `renesas,iic-r8a7740`, `renesas,iic-sh73a0`, `renesas,rmobile-iic`, `renesas,iic-r8a7742`, `renesas,iic-r8a7743`, `renesas,iic-r8a7744`, `renesas,iic-r8a7745`, `renesas,iic-r8a7790`, `renesas,iic-r8a7791`, `renesas,iic-r8a7792`, `renesas,iic-r8a7793`, `renesas,iic-r8a7794`, `renesas,rcar-gen2-iic`, `renesas,iic-r8a774a1`, `renesas,iic-r8a774b1`, `renesas,iic-r8a774c0`, `renesas,iic-r8a774e1`, ....
- Required top-level properties: `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`, `#address-cells`, `#size-cells`.
- Top-level schema references: `/schemas/i2c/i2c-controller.yaml#`.
- Key property definitions:
  - `compatible`: structured schema with nested alternatives/items.
  - `reg`: maxItems 1.
  - `interrupts` is fixed to True.
  - `clocks`: maxItems 1.
  - `resets`: maxItems 1.
  - `dmas`: maxItems 4; minItems 2; Must contain a list of pairs of references to DMA specifiers, one for transmission, and one for reception..
  - `dma-names`: maxItems 4; minItems 2.
  - `clock-frequency`: Desired I2C bus clock frequency in Hz. The absence of this property indicates the default frequency 100 kHz..
  - `power-domains`: maxItems 1.

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
- Referenced schema `/schemas/i2c/i2c-controller.yaml#`.
- 1 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

Linux devicetree validation for I2C adapter, mux, gate, tunnel, arbitration, or bitbang nodes; the I2C core binding `/schemas/i2c/i2c-controller.yaml` or `/schemas/i2c/i2c-mux.yaml` when referenced; interrupt-controller and IRQ wiring validation; common clock framework phandle/name validation
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, reg, interrupts, clocks, power-domains, #address-cells) will fail schema validation and may also prevent the kernel driver from probing.
- Conditional `if`/`then`/`oneOf` constraints can reject combinations that look locally valid unless tested against the full schema.
- Interrupt cell count, interrupt names, or interrupt-controller flags must match the interrupt provider and driver expectations.
- Clock ordering and `clock-names` mismatches can pass simple DTS review but fail runtime probe or timing setup.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/renesas,rmobile-iic.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
- Add or preserve negative schema tests mentally during review for each conditional path: unsupported compatibles should reject gated properties and supported compatibles should accept them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/renesas,rmobile-iic.yaml -->
