<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nvidia,tegra186-bpmp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nvidia,tegra186-bpmp.yaml

## Purpose
This YAML binding defines the Device Tree contract for the firmware service node for NVIDIA Tegra Boot and Power Management Processor (BPMP). The BPMP is a specific processor in Tegra chip, which is designed for booting process handling and offloading the power management, clock management, and reset control tasks from the CPU. The binding document defines the resources that would be used by the BPMP firmware driver, which can create the interprocessor communication (IPC) between the CPU and BPMP. This node is a mailbox consumer. See the following files for details of the mailbox subsystem, and the specifiers implemented by the relevant provider(s): -.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/firmware/nvidia,tegra186-bpmp.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `NVIDIA Tegra Boot and Power Management Processor (BPMP)`.
- Compatible strings or compatible constants enumerated by the schema include `nvidia,tegra194-bpmp`, `nvidia,tegra234-bpmp`, `nvidia,tegra264-bpmp`, `nvidia,tegra186-bpmp`.
- Top-level required properties: `compatible`, `mboxes`, `#clock-cells`, `#power-domain-cells`, `#reset-cells`.
- `compatible`: constraints via oneOf.
- `mboxes`: A phandle and channel specifier for the mailbox used to communicate with the BPMP.; maxItems 1.
- `shmem`: List of the phandle to the TX and RX shared memory area that the IPC between CPU and BPMP is based on.; maxItems 2; minItems 2.
- `memory-region`: phandle to reserved memory region used for IPC between CPU-NS and BPMP.; maxItems 1.
- `#clock-cells`: const `1`.
- `#power-domain-cells`: const `1`.
- `#reset-cells`: const `1`.
- `interconnects`: 4 ordered items.
- `interconnect-names`: 4 ordered items.
- `iommus`: maxItems 1.
- `i2c`: generic schema entry.
- `thermal`: generic schema entry.
- Uses top-level `oneOf` with 2 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates firmware-service discovery; runtime clients bind through firmware, mailbox, SCMI, SMC, or memory-region integration depending on the declared properties.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The binding persists no state by itself; it names firmware endpoints, shared memory, clocks, resets, power domains, or secure-call channels consumed by platform drivers at boot/probe.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `mboxes`.
- Integrates with provider/consumer property `shmem`.
- Integrates with provider/consumer property `memory-region`.
- Integrates with provider/consumer property `iommus`.
- Includes 2 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Firmware bindings are sensitive to ABI drift because OS drivers and secure/remote firmware must agree on mailbox, shared-memory, SMC, or SCMI protocol details.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/firmware/nvidia,tegra186-bpmp.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `nvidia,tegra194-bpmp`, `nvidia,tegra234-bpmp`, `nvidia,tegra264-bpmp`, `nvidia,tegra186-bpmp`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nvidia,tegra186-bpmp.yaml -->
