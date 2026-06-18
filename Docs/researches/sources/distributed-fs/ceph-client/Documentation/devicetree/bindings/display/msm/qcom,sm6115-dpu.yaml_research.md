<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6115-dpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6115-dpu.yaml

Purpose: Devicetree binding schema for Qualcomm Display DPU on SM6115, defining the SoC-specific Qualcomm DPU display-controller node under an MDSS parent. It accepts compatible values `qcom,sm6115-dpu`. It narrows the common DPU contract to this hardware generation by fixing register regions, clock inputs, and clock-name ordering.

Important APIs/types/functions: this is declarative JSON schema, not executable code. The key contract is `$id`, `$schema`, `$ref` to `/schemas/display/msm/dpu-common.yaml#`, local `properties` (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), required fields (`compatible`, `reg`, `reg-names`, `clocks`, `clock-names`), and the `unevaluatedProperties: false` gate. Compatible matching is the schema entry point used by dt-schema and by DTS authors to select the matching DPU hardware description.

Control flow: validation first applies the common DPU schema, then checks the local `compatible` value, `reg`/`reg-names` tuples, `clocks`, and `clock-names`. Example nodes show the expected runtime graph shape: the display controller is a child of `mdss`, receives MDSS interrupts, binds power/OPP data where present, and exposes `ports`/`endpoint` links toward DSI or other display interfaces. There are 1 example block(s) that exercise the schema in dt-binding checks.

State and persistence behavior: the file persists no runtime state. It constrains source-controlled DTS data that becomes part of the kernel device tree; the resulting boot-time node supplies immutable register, clock, interrupt, power-domain, and graph topology data to the MSM DRM/DPU drivers. Any stateful display behavior is in the drivers and hardware, outside this binding.

Dependencies/integration points: integrates with `/schemas/display/msm/dpu-common.yaml#`, the containing Qualcomm MDSS schema for the same SoC family, Linux dt-schema validation, display graph `ports`, clock-controller bindings, interrupt-controller bindings, power-domain/OPP bindings, and the DRM MSM DPU driver that consumes compatible-specific catalog data. Local properties are intentionally limited so common DPU behavior remains centralized.

Risks: clock and register ordering are ABI-like details; changing them can silently misbind driver resources even when property names still look valid. Compatible fallback lists must match driver catalog support exactly. Endpoint numbering must match the DPU interface catalog and the enclosing MDSS child-node examples. Overly broad compatibles can accept DTS files for unsupported hardware, while overly strict property closure can reject valid future extensions.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6115-dpu.yaml` and validate real board DTS files with `make dtbs_check`. Useful negative checks are missing `reg-names`, reordered clocks, unsupported compatible strings, missing graph endpoints, and accidental extra properties blocked by `unevaluatedProperties: false`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sm6115-dpu.yaml -->
