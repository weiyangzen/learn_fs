# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/crypto/qcom-qce.yaml

## Purpose
Qualcomm crypto engine driver is a crypto accelerator or security engine binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `qcom-qce.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. This document defines the binding for the QCE crypto controller found on Qualcomm parts.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/crypto/qcom-qce.yaml#`, top-level `compatible` values `qcom,crypto-v5.1`, `qcom,crypto-v5.4`, `qcom,ipq4019-qce`, `qcom,sm8150-qce`, `qcom,qce`, `qcom,ipq6018-qce`, `qcom,ipq8074-qce`, `qcom,ipq9574-qce`, `qcom,msm8996-qce`, `qcom,qcm2290-qce`, `qcom,sdm845-qce`, `qcom,sm6115-qce`, `qcom,kaanapali-qce`, `qcom,qcs615-qce`, and 11 more, required properties `compatible`, `reg`, `dmas`, `dma-names`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `iommus`, `interconnects`, `interconnect-names`, `dmas`, `dma-names`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `clocks` (maxItems=3; minItems=1); `clock-names` (maxItems=3; minItems=1); `dmas` (declared by schema); `dma-names` (declared by schema).
It has 3 `allOf` conditional block(s), so some constraints are selected by compatible string or by the presence of related properties.

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include the Linux crypto engine driver matched through `of_match_table` compatible strings; driver matching through compatible strings such as `qcom,crypto-v5.1`, `qcom,crypto-v5.4`, `qcom,ipq4019-qce`, `qcom,sm8150-qce`, and 21 more; provider bindings for `clocks`, `clock-names`, `dmas`, `dma-names`, `iommus`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- conditional `allOf` branches make required clocks/resets/ports variant-dependent, so examples for one SoC may not validate for another
- clock count and `clock-names` order are schema-validated and must match what the driver requests

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/crypto/qcom-qce.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is successful crypto driver probe plus crypto self-tests or AF_ALG requests on hardware-backed algorithms
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (178 lines). Maintainers listed by the binding: `Bjorn Andersson <andersson@kernel.org>`, `Konrad Dybcio <konradybcio@kernel.org>`.
