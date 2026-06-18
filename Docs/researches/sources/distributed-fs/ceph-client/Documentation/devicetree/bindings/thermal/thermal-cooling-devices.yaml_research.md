<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-cooling-devices.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-cooling-devices.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-cooling-devices.yaml` is a Linux Devicetree YAML schema for generic thermal cooling-device capability schema. It preserves the binding title `Thermal cooling device` and documents: Thermal management is achieved in devicetree by describing the sensor hardware and the software abstraction of cooling devices and thermal zones required to take appropriate action to mitigate thermal overload. The following node types are used to completely describe a thermal management system in devicetree: - thermal-sensor: device that measures temperature, has SoC-specific bindings - cooling-device: device used to dissipate heat either passively or actively - thermal-zones: a container of the following node types used to describe all thermal data for the platform This binding describes....

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `#cooling-cells`. Required keys across the schema are none. Compatible values exposed by the schema are none. Provider cell contracts are `#cooling-cells const `2``.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `#cooling-cells`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `#cooling-cells`. The file has 1 example block(s) and source signal 122 lines with top-level schema blocks `properties`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=True, limits `additionalProperties=True`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/thermal/thermal-cooling-devices.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/thermal/thermal-cooling-devices.yaml -->
