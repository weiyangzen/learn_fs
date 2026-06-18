<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/qcom,fastrpc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/qcom,fastrpc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/qcom,fastrpc.yaml` defines the miscellaneous platform device binding titled `Qualcomm FastRPC Driver`. The FastRPC implements an IPC (Inter-Processor Communication) mechanism that allows for clients to transparently make remote method invocations across DSP and APPS boundaries. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 3 tokens: `qcom,kaanapali-fastrpc`, `qcom,fastrpc`, `qcom,glymur-fastrpc`. Top-level properties are `compatible`, `label`, `memory-region`, `qcom,glink-channels`, `qcom,non-secure-domain`, `qcom,smd-channels`, `qcom,vmids`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `label`, `#address-cells`, `#size-cells`. Pattern properties are `(compute-)?cb@[0-9]*$`. Nested required-property signals include `compatible`, `reg`, `label`, `#address-cells`, `#size-cells`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Srinivas Kandagatla <srinivas.kandagatla@linaro.org>. Direct schema dependencies include `/schemas/types.yaml#/definitions/string-array`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/qcom,fastrpc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/qcom,fastrpc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/qcom,fastrpc.yaml -->
