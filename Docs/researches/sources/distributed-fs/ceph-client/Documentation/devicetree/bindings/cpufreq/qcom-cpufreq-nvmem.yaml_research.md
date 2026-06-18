# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qcom-cpufreq-nvmem.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU frequency scaling binding:
Qualcomm Technologies, Inc. NVMEM CPUFreq. It lives under `cpufreq` bindings and gives dt-schema
a machine-readable contract for matching hardware nodes before those nodes reach kernel drivers.
The description says: In certain Qualcomm Technologies, Inc. SoCs such as QCS404, The CPU supply
voltage is dynamically configured by Core Power Reduction (CPR) depending on current CPU
frequency and efuse values. CPR provides a power domain with multiple levels that are selected
depending on the CPU OPP in use. The CPUFreq driver sets the CPR power domain level according to
the required OPPs defined in the CPU OPP tables. For old implementation efuses are parsed to
select the correct opp table and voltage and CPR is not supported/used.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpufreq/qcom-cpufreq-nvmem.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: No explicit compatible string was extracted from the parsed `compatible` schema; consumers rely on the surrounding schema constraints..
- Required properties: No top-level `required` list is declared..
- Top-level framework properties: No standard framework property from the clock/interrupt/reset/regulator shortlist is declared at top level..
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: `^opp-table(-[a-z0-9]+)?$`.
- Property detail signals: The schema relies mostly on common references and required property presence rather than rich per-property local constraints..

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 2
`allOf`, 0 `oneOf`, 0 `anyOf`, and 4 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. The top-level schema leaves extra properties
open with `additionalProperties: true`.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: `/schemas/opp/opp-v2-kryo-cpu.yaml#`, `/schemas/opp/opp-v2-qcom-level.yaml#`.
- Textual schema references: `/schemas/cpufreq/qcom-cpufreq-nvmem.yaml`, `/schemas/opp/opp-v2-kryo-cpu.yaml`, `/schemas/opp/opp-v2-qcom-level.yaml`.
Runtime integration is with cpufreq platform drivers, OPP tables, clocks, regulators, NVMEM,
firmware, and performance-domain providers. Board `.dts` files instantiate nodes that satisfy
this schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- Child-node patterns must match exact unit-address/name conventions; mismatched child names may
be rejected or left unvalidated depending on the property-closure mode.
- Because the top-level closure is not explicitly false, review should ensure common schemas still
prevent accidental typo properties from being accepted.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qcom-cpufreq-nvmem.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/qcom-cpufreq-nvmem.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: / {; model = "Qualcomm Technologies, Inc. QCS404 EVB 1000";; compatible = "qcom,qcs404-evb-1000", "qcom,qcs404-evb", "qcom,qcs404";; #address-cells = <2>;; #size-cells = <2>;
