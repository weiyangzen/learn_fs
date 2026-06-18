<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,bcm2835-system-timer.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,bcm2835-system-timer.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,bcm2835-system-timer.yaml` is a Linux Devicetree YAML schema for clocksource, clockevent, or system timer binding. It preserves the binding title `BCM2835 System Timer` and documents: The System Timer peripheral provides four 32-bit timer channels and a single 64-bit free running counter. Each channel has an output compare register, which is compared against the 32 least significant bits of the free running counter values, and generates an interrupt..

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `clock-frequency`, `compatible`, `interrupts`, `reg`. Required keys across the schema are `compatible`, `interrupts`, `reg`. Compatible values exposed by the schema are `brcm,bcm2835-system-timer`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, `reg`, `interrupts`, follows referenced common schemas none, and then applies conditional branches none. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings none. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`, `reg`, `interrupts`. The file has 1 example block(s) and source signal 50 lines with top-level schema blocks `properties`, `required`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `additionalProperties`=False, limits `additionalProperties=False`, `maxItems=1`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/timer/brcm,bcm2835-system-timer.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/timer/brcm,bcm2835-system-timer.yaml -->
