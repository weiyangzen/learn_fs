# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-qcom-hw.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU frequency scaling binding:
Qualcomm Technologies, Inc. CPUFREQ. It lives under `cpufreq` bindings and gives dt-schema a
machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: CPUFREQ HW is a hardware engine used by some Qualcomm Technologies, Inc.
(QTI) SoCs to manage frequency in hardware. It is capable of controlling frequency for multiple
clusters.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpufreq/cpufreq-qcom-hw.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `qcom,cpufreq-hw`, `qcom,cpufreq-epss`, `qcom,qcm2290-cpufreq-hw`, `qcom,qcs615-cpufreq-hw`, `qcom,sc7180-cpufreq-hw`, `qcom,sc8180x-cpufreq-hw`, `qcom,sdm670-cpufreq-hw`, `qcom,sdm845-cpufreq-hw`, `qcom,sm6115-cpufreq-hw`, `qcom,sm6350-cpufreq-hw`, `qcom,sm8150-cpufreq-hw`, `qcom,eliza-cpufreq-epss`, `qcom,milos-cpufreq-epss`, `qcom,qcs8300-cpufreq-epss`, plus 14 more.
- Required properties: `compatible`, `reg`, `clocks`, `clock-names`, `#freq-domain-cells`.
- Top-level framework properties: `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#freq-domain-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (min 1 items); `reg-names` (min 1 items); `interrupts` (1-4 items); `interrupt-names` (min 1 items); `#clock-cells` (const `1`); `#freq-domain-cells` (const `1`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 1
`allOf`, 1 `oneOf`, 0 `anyOf`, and 5 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. `additionalProperties: false` closes the top-
level node to undeclared keys.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: No `$ref` dependencies were found in the parsed schema..
- Example/header integration: `dt-bindings/clock/qcom,gcc-sdm845.h`, `dt-bindings/clock/qcom,rpmh.h`.
Runtime integration is with cpufreq platform drivers, OPP tables, clocks, regulators, NVMEM,
firmware, and performance-domain providers. Board `.dts` files instantiate nodes that satisfy
this schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `clocks`, `clock-
names`, `#freq-domain-cells` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-qcom-hw.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/cpufreq-qcom-hw.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: #include <dt-bindings/clock/qcom,gcc-sdm845.h>; #include <dt-bindings/clock/qcom,rpmh.h>; // Example 1: Dual-cluster, Quad-core per cluster. CPUs within a cluster; // switch DCVS state together.; cpus {
