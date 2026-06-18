<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/thead,th1520-aon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/thead,th1520-aon.yaml

## Purpose
This YAML binding defines the Device Tree contract for the firmware service node for T-HEAD TH1520 AON (Always-On) Firmware. The Always-On (AON) subsystem in the TH1520 SoC is responsible for managing low-power states, system wakeup events, and power management tasks. It is designed to operate independently in a dedicated power domain, allowing it to remain functional even during the SoC's deep sleep states. At the heart of the AON subsystem is the E902, a low-power core that executes firmware responsible for coordinating tasks such as power domain control, clock management, and system wakeup signaling. Communication between the main.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/firmware/thead,th1520-aon.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `T-HEAD TH1520 AON (Always-On) Firmware`.
- Compatible strings or compatible constants enumerated by the schema include `thead,th1520-aon`.
- Top-level required properties: `compatible`, `mboxes`, `mbox-names`, `#power-domain-cells`.
- `compatible`: const `thead,th1520-aon`.
- `mboxes`: maxItems 1.
- `mbox-names`: 1 ordered items.
- `resets`: maxItems 1.
- `reset-names`: 1 ordered items.
- `#power-domain-cells`: const `1`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates firmware-service discovery; runtime clients bind through firmware, mailbox, SCMI, SMC, or memory-region integration depending on the declared properties.

## State and persistence behavior
- The binding persists no state by itself; it names firmware endpoints, shared memory, clocks, resets, power domains, or secure-call channels consumed by platform drivers at boot/probe.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `resets`.
- Integrates with provider/consumer property `mboxes`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Firmware bindings are sensitive to ABI drift because OS drivers and secure/remote firmware must agree on mailbox, shared-memory, SMC, or SCMI protocol details.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/firmware/thead,th1520-aon.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `thead,th1520-aon`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/thead,th1520-aon.yaml -->
