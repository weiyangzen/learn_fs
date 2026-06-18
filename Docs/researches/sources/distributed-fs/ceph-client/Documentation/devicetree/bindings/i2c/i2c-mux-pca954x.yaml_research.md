<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/i2c-mux-pca954x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/i2c-mux-pca954x.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/i2c-mux-pca954x.yaml` is a I2C topology/helper devicetree binding schema titled "NXP PCA954x I2C and compatible bus switches". The NXP PCA954x and compatible devices are I2C bus multiplexer/switches that share the same functionality and register layout. The devices usually have 4 or 8 child buses, which are attached to the parent bus by using the SMBus "Send Byte" command.
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/i2c/i2c-mux-pca954x.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Laurent Pinchart <laurent.pinchart@ideasonboard.com>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `maxim,max7356`, `maxim,max7357`, `maxim,max7358`, `maxim,max7367`, `maxim,max7368`, `maxim,max7369`, `nxp,pca9540`, `nxp,pca9542`, `nxp,pca9543`, `nxp,pca9544`, `nxp,pca9545`, `nxp,pca9546`, `nxp,pca9547`, `nxp,pca9548`, `nxp,pca9846`, `nxp,pca9847`, `nxp,pca9848`, `nxp,pca9849`, ....
- Required top-level properties: `compatible`, `reg`.
- Top-level schema references: `/schemas/mux/mux-controller.yaml#/properties/idle-state`, `/schemas/i2c/i2c-mux.yaml#`.
- Key property definitions:
  - `compatible`: structured schema with nested alternatives/items.
  - `reg`: maxItems 1.
  - `interrupts`: maxItems 1.
  - `reset-gpios`: maxItems 1.
  - `idle-state`: references `/schemas/mux/mux-controller.yaml#/properties/idle-state`; if present, overrides i2c-mux-idle-disconnect.
  - `vdd-supply`: A voltage regulator supplying power to the chip. On PCA9846 the regulator supplies power to VDD2 (core logic) and optionally to VDD1..
  - `#interrupt-cells`: constant `2`.
  - `interrupt-controller` is fixed to True.
  - `i2c-mux-idle-disconnect`: type `boolean`; Forces mux to disconnect all children in idle state. This is necessary for example, if there are several multiplexers on the bus and the devices behind them use same I2C addresses..
  - `maxim,isolate-stuck-channel`: type `boolean`; Allows to use non faulty channels while a stuck channel is isolated from the upstream bus. If not set all channels are isolated from the upstream bus until the fault is cleared..

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
- Referenced schema `/schemas/mux/mux-controller.yaml#/properties/idle-state`.
- Referenced schema `/schemas/i2c/i2c-mux.yaml#`.
- 1 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

Linux devicetree validation for I2C adapter, mux, gate, tunnel, arbitration, or bitbang nodes; the I2C core binding `/schemas/i2c/i2c-controller.yaml` or `/schemas/i2c/i2c-mux.yaml` when referenced; interrupt-controller and IRQ wiring validation; regulator supply lookup by the corresponding kernel driver; GPIO descriptor lookup and polarity/open-drain semantics
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, reg) will fail schema validation and may also prevent the kernel driver from probing.
- Conditional `if`/`then`/`oneOf` constraints can reject combinations that look locally valid unless tested against the full schema.
- Interrupt cell count, interrupt names, or interrupt-controller flags must match the interrupt provider and driver expectations.
- GPIO polarity/open-drain/reset semantics are hardware-visible and can hold buses or devices in the wrong electrical state.
- Supply phandle omissions or wrong regulator names can defer or fail probe and may affect power sequencing.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/i2c-mux-pca954x.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
- Add or preserve negative schema tests mentally during review for each conditional path: unsupported compatibles should reject gated properties and supported compatibles should accept them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/i2c-mux-pca954x.yaml -->
