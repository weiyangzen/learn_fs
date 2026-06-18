<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/qcom,scm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/qcom,scm.yaml

## Purpose
This YAML binding defines the Device Tree contract for the firmware service node for QCOM Secure Channel Manager (SCM). Qualcomm processors include an interface to communicate to the secure firmware. This interface allows for clients to request different types of actions. These can include CPU power up/down, HDCP requests, loading of firmware, and other assorted actions.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/firmware/qcom,scm.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `QCOM Secure Channel Manager (SCM)`.
- Compatible strings or compatible constants enumerated by the schema include `qcom,scm-apq8064`, `qcom,scm-apq8084`, `qcom,scm-eliza`, `qcom,scm-glymur`, `qcom,scm-ipq4019`, `qcom,scm-ipq5018`, `qcom,scm-ipq5210`, `qcom,scm-ipq5332`, `qcom,scm-ipq5424`, `qcom,scm-ipq6018`, `qcom,scm-ipq806x`, `qcom,scm-ipq8074`, ....
- Top-level required properties: `compatible`.
- `compatible`: 2 ordered items.
- `clocks`: maxItems 3; minItems 1.
- `clock-names`: maxItems 3; minItems 1.
- `dma-coherent` is accepted as a flag/property marker.
- `interconnects`: maxItems 1.
- `interconnect-names`: maxItems 1.
- `#reset-cells`: const `1`.
- `interrupts`: The wait-queue interrupt that firmware raises as part of handshake protocol to handle sleeping SCM calls.; maxItems 1.
- `memory-region`: Phandle to the memory region reserved for the shared memory bridge to TZ.; maxItems 1.
- `qcom,sdi-enabled`: Indicates that the SDI (Secure Debug Image) has been enabled by TZ by default and it needs to be disabled. If not....
- `qcom,dload-mode`: TCSR hardware block; 1 ordered items; ref `/schemas/types.yaml#/definitions/phandle-array`.
- Uses top-level `allOf` with 5 branch(es) for variant-specific validation.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates firmware-service discovery; runtime clients bind through firmware, mailbox, SCMI, SMC, or memory-region integration depending on the declared properties.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The binding persists no state by itself; it names firmware endpoints, shared memory, clocks, resets, power domains, or secure-call channels consumed by platform drivers at boot/probe.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/phandle-array`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Integrates with provider/consumer property `memory-region`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Firmware bindings are sensitive to ABI drift because OS drivers and secure/remote firmware must agree on mailbox, shared-memory, SMC, or SCMI protocol details.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/firmware/qcom,scm.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `qcom,scm-apq8064`, `qcom,scm-apq8084`, `qcom,scm-eliza`, `qcom,scm-glymur`, `qcom,scm-ipq4019`, `qcom,scm-ipq5018`, ....
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/qcom,scm.yaml -->
