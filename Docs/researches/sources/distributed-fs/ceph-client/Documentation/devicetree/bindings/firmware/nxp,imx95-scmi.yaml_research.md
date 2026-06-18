<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nxp,imx95-scmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nxp,imx95-scmi.yaml

## Purpose
This YAML binding defines the Device Tree contract for the firmware service node for i.MX95 System Control and Management Interface(SCMI) Vendor Protocols Extension. i.MX95 System Control and Management Interface(SCMI) Vendor Protocols Extension

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/firmware/nxp,imx95-scmi.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `i.MX95 System Control and Management Interface(SCMI) Vendor Protocols Extension`.
- No top-level `required` list is declared; requirements are delegated to referenced schemas, branch logic, or child schemas.
- `protocol@80`: SCMI LMM protocol which is for boot, shutdown, and reset of other logical machines (LM). It is usually used to...; ref `/schemas/firmware/arm,scmi.yaml#/$defs/protocol-node`.
- `protocol@81`: constraints via allOf, additionalProperties, properties.
- `protocol@82`: SCMI CPU Protocol which allows an agent to start or stop a CPU. It is used to manage auxiliary CPUs in a LM.; ref `/schemas/firmware/arm,scmi.yaml#/$defs/protocol-node`.
- `protocol@84`: ref `/schemas/firmware/arm,scmi.yaml#/$defs/protocol-node`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates firmware-service discovery; runtime clients bind through firmware, mailbox, SCMI, SMC, or memory-region integration depending on the declared properties.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- The binding persists no state by itself; it names firmware endpoints, shared memory, clocks, resets, power domains, or secure-call channels consumed by platform drivers at boot/probe.
- `additionalProperties` is `True`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- References shared schemas: `/schemas/firmware/arm,scmi.yaml#/$defs/protocol-node`, `/schemas/input/input.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.

## Risks and edge cases
- Firmware bindings are sensitive to ABI drift because OS drivers and secure/remote firmware must agree on mailbox, shared-memory, SMC, or SCMI protocol details.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/firmware/nxp,imx95-scmi.yaml` plus `make dtbs_check` on boards using the compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nxp,imx95-scmi.yaml -->
