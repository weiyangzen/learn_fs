<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/fsi-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/fsi-controller.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FSI bus/controller/peripheral binding for FSI Controller Common Properties. FSI (FRU (Field Replaceable Unit) Service Interface) is a two wire bus. The FSI bus is connected to a CFAM (Common FRU Access Macro) which contains various engines such as I2C controllers, SPI controllers, etc.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fsi/fsi-controller.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `FSI Controller Common Properties`.
- No top-level `required` list is declared; requirements are delegated to referenced schemas, branch logic, or child schemas.
- `#address-cells`: const `2`.
- `#size-cells`: const `0`.
- `#interrupt-cells`: const `1`.
- `bus-frequency`: constraints via minimum, maximum.
- `interrupt-controller` is accepted as a flag/property marker.
- `no-scan-on-init`: The FSI controller cannot scan the bus during initialization.; ref `/schemas/types.yaml#/definitions/flag`.
- Pattern child/property schemas: `cfam@[0-9a-f],[0-9a-f]`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the FSI topology visible to service processors; runtime probing follows FSI master/controller discovery into child engines such as SBEFIFO, SCOM, OCC, or SPI bridges.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent topology is represented by DT child nodes and addressing cells; mutable FSI engine state remains in bus and device drivers.
- `additionalProperties` is `True`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`.

## Risks and edge cases
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fsi/fsi-controller.yaml` plus `make dtbs_check` on boards using the compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/fsi-controller.yaml -->
