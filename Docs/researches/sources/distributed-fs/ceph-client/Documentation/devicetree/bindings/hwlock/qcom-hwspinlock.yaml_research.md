<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/qcom-hwspinlock.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/qcom-hwspinlock.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/qcom-hwspinlock.yaml` defines the hardware spinlock controller binding titled `Qualcomm Hardware Mutex Block`. Description from the schema: The hardware block provides mutexes utilized between different processors on the SoC as part of the communication protocol used by these processors. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 3 branches with 8 tokens: `qcom,sfpb-mutex`, `qcom,tcsr-mutex`, `qcom,apq8084-tcsr-mutex`, `qcom,ipq6018-tcsr-mutex`, `qcom,msm8226-tcsr-mutex`, `qcom,msm8994-tcsr-mutex`, `qcom,msm8974-tcsr-mutex`, `syscon`. Top-level properties are `compatible`, `reg`, `#hwlock-cells`. Required top-level properties are `compatible`, `reg`, `#hwlock-cells`. Pattern properties are none. The highest-risk API details are `#hwlock-cells`, lock-bank register size, reset/clock requirements, and SoC-specific lock counts.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including lock-bank registration, remote-processor lock ownership, and hardware lock acquisition/release state.

## Dependencies and Integration Points
Maintainers listed: Bjorn Andersson <bjorn.andersson@linaro.org>. Dependencies include dt-schema core/meta schemas only. Integration points include the Linux hwspinlock framework, remoteproc/IPC users, syscon/regmap access, interrupts where present, and SoC DTS lock-bank nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to `#hwlock-cells`, lock-bank register size, reset/clock requirements, and SoC-specific lock counts, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwlock/qcom-hwspinlock.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwlock/qcom-hwspinlock.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwlock/qcom-hwspinlock.yaml -->
