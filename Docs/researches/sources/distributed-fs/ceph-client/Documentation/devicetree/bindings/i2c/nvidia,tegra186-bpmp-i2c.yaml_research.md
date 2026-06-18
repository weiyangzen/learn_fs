<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/nvidia,tegra186-bpmp-i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/nvidia,tegra186-bpmp-i2c.yaml

## Purpose

`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/nvidia,tegra186-bpmp-i2c.yaml` is a I2C controller devicetree binding schema titled "NVIDIA Tegra186 (and later) BPMP I2C controller". In Tegra186 and later, the BPMP (Boot and Power Management Processor) owns certain HW devices, such as the I2C controller for the power management I2C bus. Software running on other CPUs must perform IPC to the BPMP in order to execute transactions on that I2C bus. This binding describes an I2C bus that is accessed in such a fashion. The BPMP I2C node must be located directly inside the main BPMP node. See ../firmware/nvidia,tegra186-bpmp.yaml for details of the BPMP binding. This node represents an I2C controller.
It is consumed by Linux devicetree schema tooling to validate DTS nodes against the binding contract identified by `http://devicetree.org/schemas/i2c/nvidia,tegra186-bpmp-i2c.yaml#` and the meta-schema `http://devicetree.org/meta-schemas/core.yaml#`. Maintainers: Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com>.

## Important APIs, Types, And Functions

This YAML file does not define executable APIs, classes, or functions. Its important interface is the dt-schema vocabulary exposed to DTS authors and kernel binding checks:

- Compatible contract: `nvidia,tegra186-bpmp-i2c`.
- Required top-level properties: `compatible`, `#address-cells`, `#size-cells`, `nvidia,bpmp-bus-id`.
- Top-level schema references: `/schemas/types.yaml#/definitions/uint32`, `/schemas/i2c/i2c-controller.yaml`.
- Key property definitions:
  - `compatible`: constant `nvidia,tegra186-bpmp-i2c`.
  - `nvidia,bpmp-bus-id`: references `/schemas/types.yaml#/definitions/uint32`; Indicates the I2C bus number this DT node represents, as defined by the BPMP firmware..

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
- Referenced schema `/schemas/types.yaml#/definitions/uint32`.
- Referenced schema `/schemas/i2c/i2c-controller.yaml`.

## Integration Points

Linux devicetree validation for I2C adapter, mux, gate, tunnel, arbitration, or bitbang nodes; the I2C core binding `/schemas/i2c/i2c-controller.yaml` or `/schemas/i2c/i2c-mux.yaml` when referenced
It also integrates with `Documentation/devicetree/bindings/` review rules: compatible strings identify hardware, common schemas supply shared bus/channel semantics, and examples act as regression inputs for schema validation.

## Risks

- Compatible-string mistakes silently bind the wrong driver or fail driver matching even when the node otherwise validates.
- Missing required properties (compatible, #address-cells, #size-cells, nvidia,bpmp-bus-id) will fail schema validation and may also prevent the kernel driver from probing.
- Conditional `if`/`then`/`oneOf` constraints can reject combinations that look locally valid unless tested against the full schema.
- Because devicetree bindings are treated as stable ABI, tightening this schema requires checking existing in-tree and downstream DTS users.

## Test Signals

- Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/nvidia,tegra186-bpmp-i2c.yaml` in a kernel tree containing this binding.
- Run `make dtbs_check` for boards using the listed compatible strings or child-node patterns.
- Search DTS users of the compatible strings and verify required properties, register cells, clocks, interrupts, supplies, and reset/GPIO lines are present and ordered as the binding expects.
- Add or preserve negative schema tests mentally during review for each conditional path: unsupported compatibles should reject gated properties and supported compatibles should accept them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/nvidia,tegra186-bpmp-i2c.yaml -->
