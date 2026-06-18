<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nvidia,tegra186-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nvidia,tegra186-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for NVIDIA Tegra GPIO Controller (Tegra186 and later). Tegra186 contains two GPIO controllers; a main controller and an "AON" controller. This binding document applies to both controllers. The register layouts for the controllers share many similarities, but also some significant differences. Hence, this document describes closely related but different bindings and compatible values. The Tegra186 GPIO controller allows software to set the IO direction of, and read/write the value of, numerous GPIO signals. Routing of GPIO signals to package balls is under the control.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/nvidia,tegra186-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `NVIDIA Tegra GPIO Controller (Tegra186 and later)`.
- Compatible strings or compatible constants enumerated by the schema include `nvidia,tegra186-gpio`, `nvidia,tegra186-gpio-aon`, `nvidia,tegra194-gpio`, `nvidia,tegra194-gpio-aon`, `nvidia,tegra234-gpio`, `nvidia,tegra234-gpio-aon`, `nvidia,tegra256-gpio`, `nvidia,tegra264-gpio`, `nvidia,tegra264-gpio-uphy`, `nvidia,tegra264-gpio-aon`.
- Top-level required properties: `compatible`, `reg`, `reg-names`, `interrupts`.
- `compatible`: enum `nvidia,tegra186-gpio`, `nvidia,tegra186-gpio-aon`, `nvidia,tegra194-gpio`, `nvidia,tegra194-gpio-aon`, `nvidia,tegra234-gpio`, `nvidia,tegra234-gpio-aon`, `nvidia,tegra256-gpio`, `nvidia,tegra264-gpio`, ....
- `reg-names`: minItems 1; 2 ordered items.
- `reg`: minItems 1; 2 ordered items.
- `interrupts`: The interrupt outputs from the HW block, one per set of ports, in the order the HW manual describes them. The....
- `wakeup-parent`: Phandle to the parent interrupt controller used for wake-up. On Tegra, this typically references the PMC interrupt....
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-ranges`: maxItems 1.
- `#gpio-cells`: Indicates how many cells are used in a consumer's GPIO specifier. In the specifier: - The first cell is the pin...; const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: Indicates how many cells are used in a consumer's interrupt specifier. In the specifier: - The first cell is the...; const `2`.
- Uses top-level `allOf` with 3 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/nvidia,tegra186-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `nvidia,tegra186-gpio`, `nvidia,tegra186-gpio-aon`, `nvidia,tegra194-gpio`, `nvidia,tegra194-gpio-aon`, `nvidia,tegra234-gpio`, `nvidia,tegra234-gpio-aon`, ....
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nvidia,tegra186-gpio.yaml -->
