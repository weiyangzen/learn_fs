<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm_tis-spi.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm_tis-spi.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm_tis-spi.yaml` is a Linux Devicetree YAML schema for trusted platform module device binding. It preserves the binding title `SPI-attached Trusted Platform Module conforming to TCG TIS specification` and documents: The Trusted Computing Group (TCG) has defined a multi-vendor standard for accessing a TPM chip. It can be transported over various buses, one of them being SPI. The standard is named: TCG PC Client Specific TPM Interface Specification (TIS) https://trustedcomputinggroup.org/resource/pc-client-work-group-pc-client-specific-tpm-interface-specification-tis/.

Important APIs/types/functions: this is a declarative dt-schema contract, so the important interface is the set of node properties rather than runtime functions. Top-level properties include `compatible`. Required keys across the schema are `compatible`, `reg`. Compatible values exposed by the schema are `atmel,attpm20p`, `infineon,slb9670`, `st,st33htpm-spi`, `st,st33zp24-spi`, `tcg,tpm_tis-spi`.

Control flow: validation starts from the node selected by `compatible`, checks common bus properties such as `compatible`, follows referenced common schemas `/schemas/spi/spi-peripheral-props.yaml#`, `tpm-common.yaml#`, and then applies conditional branches `allOf`=1, `if`=1, `then`=1. Kernel runtime flow is indirect: once a matching DT node passes schema validation, the corresponding platform, bus, thermal, timer, timestamp, TPM, or IIO trigger driver consumes the resources described here.

State and persistence behavior: the file stores no runtime state; it constrains persistent hardware description in DTS/DTB data. Persistent state is the fixed register layout, interrupt routing, clock/reset wiring, calibration cells, trip points, cooling maps, timer capabilities, timestamp line mappings, TPM transport properties, or trigger-source links encoded in the device tree. Driver probe state is recreated from those properties at boot or overlay application time.

Dependencies and integration points: schema validation depends on dt-schema core meta-schemas and referenced bindings `/schemas/spi/spi-peripheral-props.yaml#`, `tpm-common.yaml#`. The binding integrates with subsystem consumers through standard phandles and properties; notable local integration keys are `compatible`. The file has 2 example block(s) and source signal 76 lines with top-level schema blocks `properties`, `required`, `allOf`, `examples`.

Risks: schema regressions can silently allow invalid board descriptions or reject existing DTS files. The highest-risk areas are compatible fallback ordering, resource array cardinality, clock/reset name alignment, interrupt count and naming, provider cell counts, referenced common-schema compatibility, and conditional branches for SoC variants or transport-specific nodes. Strictness signals include `unevaluatedProperties`=False, limits `unevaluatedProperties=False`, `maximum=10000000`.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/tpm/tcg,tpm_tis-spi.yaml` from the kernel tree, plus broader `dtbs_check` on DTS files that instantiate the compatible strings. Useful failures are missing required properties, mismatched phandle cell counts, bad reg/interrupt/clock cardinality, invalid child-node names, and example DTS snippets rejected by the schema.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/tpm/tcg,tpm_tis-spi.yaml -->
