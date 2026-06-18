<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/microsoft,ftpm.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/microsoft,ftpm.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/microsoft,ftpm.yaml` is a Linux Devicetree YAML schema for trusted platform module device binding. It preserves the binding title `Microsoft firmware-based Trusted Platform Module (fTPM)` and documents: Commodity CPU architectures, such as ARM and Intel CPUs, have started to offer trusted computing features in their CPUs aimed at displacing dedicated trusted hardware. Unfortunately, these CPU architectures raise serious challenges to building trusted systems because they omit providing secure resources outside the CPU perimeter. Microsoft's firmware-based TPM 2.0 (fTPM) leverages ARM TrustZone to overcome these challenges and provide software with security guarantees similar to those of dedicated trusted hardware. https://www.microsoft.com/en-us/research/publication/ftpm-software-implement....

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`. Required keys across the schema are `compatible`, `linux,sml-base`, `linux,sml-size`. Compatible values exposed by the schema are `microsoft,ftpm`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, follows referenced common schemas `tpm-common.yaml#`, and then applies conditional branches `allOf`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `tpm-common.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`. The file has 1 example block(s) and source signal 47 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/tpm/microsoft,ftpm.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/microsoft,ftpm.yaml -->
