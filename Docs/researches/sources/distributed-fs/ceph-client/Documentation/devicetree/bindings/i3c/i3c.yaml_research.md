<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i3c/i3c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i3c/i3c.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i3c/i3c.yaml` is a I3C devicetree binding schema titled "I3C bus". I3C busses can be described with a node for the primary I3C controller device and a set of child nodes for each I2C or I3C slave on the bus. Each of them may, during the life of the bus, request mastership.
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/i3c/i3c.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>, Miquel Raynal <miquel.raynal@bootlin.com>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: not a top-level compatible binding.
- Node-name rule: `^i3c@[0-9a-f]+$`.
- Required top-level properties: `#address-cells`, `#size-cells`.
- Top-level schema references: `/schemas/types.yaml#/definitions/uint32`.
- Child/pattern node schemas: `@[0-9a-f]+$`, `@[0-9a-f]+,[0-9a-f]+$`.
- Key property definitions:
  - `#address-cells`: constant `3`; Each I2C device connected to the bus should be described in a subnode. All I3C devices are supposed to support DAA (Dynamic Address Assignment), and are thus discoverable. So, by default, I3C devices do not have to be de....
  - `#size-cells`: constant `0`.
  - `$nodename`: declared without extra local constraints.
  - `i3c-scl-hz`: Frequency of the SCL signal used for I3C transfers. When undefined, the default value should be 12.5MHz. May not be supported by all controllers..
  - `i2c-scl-hz`: Frequency of the SCL signal used for I2C transfers. When undefined, the default should be to look at LVR (Legacy Virtual Register) values of I2C devices described in the device tree to determine the maximum I2C frequency....
  - `mctp-controller`: type `boolean`; Indicates that the system is accessible via this bus as an endpoint for MCTP over I3C transport..

## Control Flow

1. Kernel build or developer tooling invokes `dt_binding_check`/`dtbs_check` over this schema and matching DTS nodes.
2. The schema first applies the declared meta-schema and any `allOf`/`$ref` base schemas, then validates local `properties`, `required`, `patternProperties`, and property-count constraints.
3. Compatible strings, node names, register cells, clocks, interrupts, GPIOs, supplies, and child nodes are checked structurally; any `if`/`then`/`else`, `oneOf`, or dependency blocks further narrow the accepted combinations.
4. Examples embedded in the binding are compiled as miniature DTS fragments and validated against the same schema.
The binding is mostly declarative: validation is driven by required properties and direct property schemas rather than runtime branches.

## State And Persistence Behavior

The file has no runtime state and performs no persistence. Its persistent effect is contractual: once DTS files use this binding, the compatible strings, property names, child-node layout, and examples become ABI-like data consumed by boot firmware, the kernel, and validation tooling. Changes that remove accepted compatibles, tighten required properties, or alter cell layouts can break existing device trees even though no code executes here.
Unknown property policy is `additionalProperties: True` and `unevaluatedProperties: <unspecified>`, so extensions are governed by those flags plus referenced schemas.

## Dependencies

- YAML 1.2 and the devicetree core meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Referenced schema `/schemas/types.yaml#/definitions/uint32`.
- 1 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

Linux I3C master/bus registration and mixed I2C/I3C child-node description; I3C dynamic address assignment, static-address handoff, and bus-frequency policy where modeled
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Missing required properties (#address-cells, #size-cells) will fail schema validation and may also prevent the kernel driver from probing.
- I3C address-cell encoding and assigned-address handling are easy to corrupt because I2C legacy and I3C PID fields share `reg` encodings.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i3c/i3c.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i3c/i3c.yaml -->
