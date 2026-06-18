# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/qcom,llcc.yaml

## Purpose
LLCC (Last Level Cache Controller) provides last level of cache memory in SoC, that can be shared by multiple clients. It is a cache-controller binding used for cache-controller description for CPU/system cache drivers and cache hierarchy validation. The binding is maintained by Bjorn Andersson <andersson@kernel.org> and gives dt-schema a canonical contract for nodes matching `qcom,glymur-llcc`, `qcom,ipq5424-llcc`, `qcom,kaanapali-llcc`, `qcom,qcs615-llcc`, `qcom,qcs8300-llcc`, `qcom,qdu1000-llcc`, `qcom,sa8775p-llcc`, `qcom,sar1130p-llcc`, `qcom,sar2130p-llcc`, `qcom,sc7180-llcc`, plus 15 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum qcom,glymur-llcc, qcom,ipq5424-llcc, qcom,kaanapali-llcc, qcom,qcs615-llcc...), `reg` (items 1..14), `reg-names` (items 1..14), `interrupts` (items ?..1), `nvmem-cells`, `nvmem-cell-names`. Required properties are `compatible`, `reg`, `reg-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 10 `allOf` composition block(s), 10 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=cache/qcom,llcc.yaml`
- run `make dtbs_check` on DTS files using `qcom,glymur-llcc`, `qcom,ipq5424-llcc`, `qcom,kaanapali-llcc`, `qcom,qcs615-llcc`, `qcom,qcs8300-llcc`, `qcom,qdu1000-llcc`, `qcom,sa8775p-llcc`, `qcom,sar1130p-llcc`, `qcom,sar2130p-llcc`, `qcom,sc7180-llcc`, plus 15 more
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
