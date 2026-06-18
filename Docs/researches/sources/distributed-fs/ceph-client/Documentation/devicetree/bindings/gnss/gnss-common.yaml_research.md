<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/gnss-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/gnss-common.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GNSS receiver binding for Common Properties for Global Navigation Satellite Systems (GNSS) receiver devices. This document defines device tree properties common to Global Navigation Satellite System receivers.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gnss/gnss-common.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Common Properties for Global Navigation Satellite Systems (GNSS) receiver devices`.
- No top-level `required` list is declared; requirements are delegated to referenced schemas, branch logic, or child schemas.
- `$nodename`: pattern `^gnss(@.*)?$`.
- `lna-supply`: A separate regulator supplying power for the Low Noise Amplifier (LNA). This is an amplifier connected between the....
- `enable-gpios`: A GPIO line that will enable the GNSS receiver when asserted. If this line is active low, the GPIO phandle should...; maxItems 1.
- `timepulse-gpios`: Timepulse signal; maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates a serial or platform GNSS receiver node so the GNSS subsystem can bind transport, regulators, reset lines, and optional backup/enable controls consistently.

## State and persistence behavior
- The DT node records hardware wiring and optional regulator/reset/enable policy; live receiver state, fix data, and protocol state are handled by GNSS/serdev drivers.
- `additionalProperties` is `True`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- Integrates with provider/consumer property `enable-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Main risk is schema drift from the bound kernel driver or from DTS examples that are not covered by validation.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gnss/gnss-common.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/gnss-common.yaml -->
