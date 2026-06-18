<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ti,fpc202.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ti,fpc202.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ti,fpc202.yaml` defines the miscellaneous platform device binding titled `TI FPC202 dual port controller with expanded IOs`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `ti,fpc202`. Top-level properties are `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `enable-gpios`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `#address-cells`, `#size-cells`. Pattern properties are `^i2c@[0-1]$`, `^led@1[4-b]$`. Nested required-property signals include `#address-cells`, `#size-cells`, `reg`, `compatible`, `gpio-controller`, `#gpio-cells`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Romain Gantois <romain.gantois@bootlin.com>. Direct schema dependencies include `/schemas/i2c/i2c-atr.yaml#`, `/schemas/i2c/i2c-controller.yaml#`, `/schemas/leds/common.yaml#`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/ti,fpc202.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/ti,fpc202.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ti,fpc202.yaml -->
