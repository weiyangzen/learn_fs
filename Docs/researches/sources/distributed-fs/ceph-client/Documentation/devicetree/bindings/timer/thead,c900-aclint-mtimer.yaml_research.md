<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/thead,c900-aclint-mtimer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/thead,c900-aclint-mtimer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/thead,c900-aclint-mtimer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `ACLINT Machine-level Timer Device`.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`, `interrupts-extended`, `reg`, `reg-names`. Required keys across the schema are `compatible`, `interrupts-extended`, `reg`, `reg-names`. Compatible values exposed by the schema are `sophgo,sg2042-aclint-mtimer`, `sophgo,sg2044-aclint-mtimer`, `thead,c900-aclint-mtimer`, `anlogic,dr1v90-aclint-mtimer`, `nuclei,ux900-aclint-mtimer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, follows referenced common schemas none, and then applies conditional branches `oneOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`. The file has 1 example block(s) and source signal 56 lines with top-level schema blocks `properties`, `required`, `oneOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `minItems=1`, `maxItems=4095`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/thead,c900-aclint-mtimer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/thead,c900-aclint-mtimer.yaml -->
