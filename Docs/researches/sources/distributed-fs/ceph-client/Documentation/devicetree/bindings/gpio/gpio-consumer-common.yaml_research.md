<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-consumer-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-consumer-common.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Common GPIO lines. Pay attention to using proper GPIO flag (e.g. GPIO_ACTIVE_LOW) for the GPIOs using inverted signal (e.g. RESETN).

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-consumer-common.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Common GPIO lines`.
- No top-level `required` list is declared; requirements are delegated to referenced schemas, branch logic, or child schemas.
- `enable-gpios`: GPIO connected to the enable control pin.; maxItems 1.
- `reset-gpios`: GPIO (or GPIOs for power sequence) connected to the device reset pin (e.g. RESET or RESETN)..
- `powerdown-gpios`: GPIO connected to the power down pin (hardware power down or power cut, e.g. PD or PWDN).; maxItems 1.
- `pwdn-gpios`: Use powerdown-gpios; maxItems 1.
- `wakeup-gpios`: GPIO connected to the pin waking up the device from suspend or other power-saving modes.; maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `True`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- Integrates with provider/consumer property `reset-gpios`.
- Integrates with provider/consumer property `enable-gpios`.

## Risks and edge cases
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-consumer-common.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-consumer-common.yaml -->
