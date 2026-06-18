<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nxp,imx95-scmi-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nxp,imx95-scmi-pinctrl.yaml

## Purpose
This YAML binding defines the Device Tree contract for the firmware service node for i.MX System Control and Management Interface (SCMI) Pinctrl Protocol. i.MX System Control and Management Interface (SCMI) Pinctrl Protocol

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/firmware/nxp,imx95-scmi-pinctrl.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `i.MX System Control and Management Interface (SCMI) Pinctrl Protocol`.
- No top-level `required` list is declared; requirements are delegated to referenced schemas, branch logic, or child schemas.
- Pattern child/property schemas: `grp$`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates firmware-service discovery; runtime clients bind through firmware, mailbox, SCMI, SMC, or memory-region integration depending on the declared properties.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The binding persists no state by itself; it names firmware endpoints, shared memory, clocks, resets, power domains, or secure-call channels consumed by platform drivers at boot/probe.
- `additionalProperties` is `True`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- References shared schemas: `/schemas/pinctrl/pinctrl.yaml`, `/schemas/types.yaml#/definitions/uint32-matrix`.

## Risks and edge cases
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Firmware bindings are sensitive to ABI drift because OS drivers and secure/remote firmware must agree on mailbox, shared-memory, SMC, or SCMI protocol details.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/firmware/nxp,imx95-scmi-pinctrl.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nxp,imx95-scmi-pinctrl.yaml -->
