<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvdec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvdec.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvdec.yaml` defines the Tegra host1x media engine binding titled `NVIDIA Tegra NVDEC`. Description from the schema: NVDEC is the hardware video decoder present on NVIDIA Tegra210 and newer chips. It is located on the Host1x bus and typically programmed through Host1x channels. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `nvidia,tegra210-nvdec`, `nvidia,tegra186-nvdec`, `nvidia,tegra194-nvdec`. Top-level properties are `$nodename`, `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`, `iommus`, `dma-coherent`, `interconnects`, `interconnect-names`, `nvidia,host1x-class`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains`. Pattern properties are none. The highest-risk API details are host1x child placement, memory/IOMMU attachment, clock/reset names, and engine-specific compatible fallbacks.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device power state, MMU/IOMMU attachment, firmware or command submission setup, runtime PM, and DRM/media device registration.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <treding@gmail.com>, Mikko Perttunen <mperttunen@nvidia.com>. Dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include the Tegra host1x bus, DRM/media engines, power domains, resets, clocks, IOMMU, and host1x channel clients. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to host1x child placement, memory/IOMMU attachment, clock/reset names, and engine-specific compatible fallbacks, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvdec.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvdec.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpu/host1x/nvidia,tegra210-nvdec.yaml -->
