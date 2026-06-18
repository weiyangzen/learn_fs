<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i3c/mipi-i3c-hci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i3c/mipi-i3c-hci.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i3c/mipi-i3c-hci.yaml` is a I3C devicetree binding schema titled "MIPI I3C HCI". MIPI I3C Host Controller Interface The MIPI I3C HCI (Host Controller Interface) specification defines a common software driver interface to support compliant MIPI I3C host controller hardware implementations from multiple vendors. The hardware is self-advertising for differences in implementation capabilities, including the spec version it is based on, so there isn't much to describe here (yet). For details, please see: https://www.mipi.org/specifications/i3c-hci
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/i3c/mipi-i3c-hci.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Nicolas Pitre <npitre@baylibre.com>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: not a top-level compatible binding.
- Required top-level properties: `compatible`, `reg`, `interrupts`.
- Top-level schema references: `/schemas/i3c/i3c.yaml#`.
- Key property definitions:
  - `compatible`: constant `mipi-i3c-hci`.
  - `reg`: maxItems 1.
  - `interrupts`: maxItems 1.

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
- Referenced schema `/schemas/i3c/i3c.yaml#`.
- 1 embedded example block(s), which depend on referenced dt-bindings headers or provider labels when included in the example text.

## Integration Points

Linux I3C master/bus registration and mixed I2C/I3C child-node description; I3C dynamic address assignment, static-address handoff, and bus-frequency policy where modeled; interrupt-controller and IRQ wiring validation
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Missing required properties (compatible, reg, interrupts) will fail schema validation and may also prevent the kernel driver from probing.
- Conditional `if`/`then`/`oneOf` constraints can reject combinations that look locally valid unless tested against the full schema.
- Interrupt cell count, interrupt names, or interrupt-controller flags must match the interrupt provider and driver expectations.
- I3C address-cell encoding and assigned-address handling are easy to corrupt because I2C legacy and I3C PID fields share `reg` encodings.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i3c/mipi-i3c-hci.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Ensure every `examples:` fragment in this file validates cleanly, including included headers, provider phandles, and child nodes.
- Add or preserve negative schema tests mentally during review for each conditional path: unsupported compatibles should reject gated properties and supported compatibles should accept them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i3c/mipi-i3c-hci.yaml -->
