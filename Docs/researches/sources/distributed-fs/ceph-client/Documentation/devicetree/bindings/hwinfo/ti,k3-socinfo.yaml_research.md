<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/ti,k3-socinfo.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/ti,k3-socinfo.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/ti,k3-socinfo.yaml` defines the hardware-identification binding titled `Texas Instruments K3 Multicore SoC platforms chipid module`. Description from the schema: Texas Instruments (ARM64) K3 Multicore SoC platforms chipid module is represented by CTRLMMR_xxx_JTAGID register which contains information about SoC id and revision. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an ordered fallback `items` sequence with 1 token: `ti,am654-chipid`. Top-level properties are `$nodename`, `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including read-only SoC ID or revision state exposed to platform code, sysfs/debugfs, or quirk selection paths.

## Dependencies and Integration Points
Maintainers listed: Tero Kristo <t-kristo@ti.com>, Nishanth Menon <nm@ti.com>. Dependencies include dt-schema core/meta schemas only. Integration points include SoC identification drivers, NVMEM/syscon/register readers, debugfs/sysfs exposure, and platform code that selects quirks by chip revision. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to stable register windows, syscon phandles, compatible fallbacks, and whether child nodes are allowed, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/ti,k3-socinfo.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwinfo/ti,k3-socinfo.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwinfo/ti,k3-socinfo.yaml -->
