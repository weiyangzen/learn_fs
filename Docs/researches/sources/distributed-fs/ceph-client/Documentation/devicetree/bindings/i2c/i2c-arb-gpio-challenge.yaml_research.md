<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/i2c-arb-gpio-challenge.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/i2c-arb-gpio-challenge.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/i2c-arb-gpio-challenge.yaml` is a I2C topology/helper devicetree binding schema titled "GPIO-based I2C Arbitration Using a Challenge & Response Mechanism". This uses GPIO lines and a challenge & response mechanism to arbitrate who is the master of an I2C bus in a multimaster situation. In many cases using GPIOs to arbitrate is not needed and a design can use the standard I2C multi-master rules. Using GPIOs is generally useful in the case where there is a device on the bus that has errata and/or bugs that makes standard multimaster mode not feasible. Note that this scheme works well enough but has some downsides: * It is nonstandard (not using standard I2C multimaster)...
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/i2c/i2c-arb-gpio-challenge.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Doug Anderson <dianders@chromium.org>, Peter Rosin <peda@axentia.se>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `i2c-arb-gpio-challenge`.
- Required top-level properties: `compatible`, `i2c-arb`, `our-claim-gpios`, `their-claim-gpios`.
- Top-level schema references: `/schemas/types.yaml#/definitions/phandle`, `/schemas/i2c/i2c-controller.yaml`.
- Key property definitions:
  - `compatible`: constant `i2c-arb-gpio-challenge`.
  - `i2c-parent`: references `/schemas/types.yaml#/definitions/phandle`; The I2C bus that this multiplexer's master-side port is connected to..
  - `our-claim-gpios`: maxItems 1; The GPIO that we use to claim the bus..
  - `slew-delay-us`: Time to wait for a GPIO to go high..
  - `their-claim-gpios`: maxItems 8; minItems 1; The GPIOs that the other sides use to claim the bus. Note that some implementations may only support a single other master..
  - `wait-free-us`: We'll give up after this many microseconds..
  - `wait-retry-us`: We'll attempt another claim after this many microseconds..
  - `i2c-arb`: references `/schemas/i2c/i2c-controller.yaml`; type `object`; I2C arbitration bus node..

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
- Referenced schema `/schemas/types.yaml#/definitions/phandle`.
- Referenced schema `/schemas/i2c/i2c-controller.yaml`.
- 1 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

Linux devicetree validation for I2C adapter, mux, gate, tunnel, arbitration, or bitbang nodes; the I2C core binding `/schemas/i2c/i2c-controller.yaml` or `/schemas/i2c/i2c-mux.yaml` when referenced; GPIO descriptor lookup and polarity/open-drain semantics
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, i2c-arb, our-claim-gpios, their-claim-gpios) will fail schema validation and may also prevent the kernel driver from probing.
- GPIO polarity/open-drain/reset semantics are hardware-visible and can hold buses or devices in the wrong electrical state.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/i2c-arb-gpio-challenge.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/i2c-arb-gpio-challenge.yaml -->
