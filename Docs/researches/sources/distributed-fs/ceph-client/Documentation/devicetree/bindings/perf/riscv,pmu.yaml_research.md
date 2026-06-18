<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/riscv,pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/riscv,pmu.yaml

## Purpose
RISC-V SBI PMU events is a performance monitoring unit binding. The SBI PMU extension allows supervisor software to configure, start and stop any performance counter at anytime. Thus, a user can leverage all capabilities of performance analysis tools, such as perf, if the SBI PMU extension is enabled. The following constraints apply:    The platform must provide information about PMU event to counter mappings   either via device tree or another way, specific to the platform.   Without the event to counter mappings, the SBI PMU extension cannot be used.    Platforms should provide information about the PMU event selector values   that should be encoded in the expected value of MHPMEVENTx while configuring   MHPMCOUNTERx for that specific event. The can either be done via device tree   or another way, specific to the platform.   The exact value to be written to MHPMEVENTx is completely dependent on the   platform.    For information on the SBI specification see the section "Performance   Monitoring Unit Extension" of:     https://github.com/riscv-non-isa/riscv-sbi-doc/blob/master/riscv-sbi.adoc Maintainers: Atish Patra <atishp@rivosinc.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/perf/riscv,pmu.yaml#`. compatible values `riscv,pmu`. required properties `compatible`. notable properties `compatible`, `riscv,event-to-mhpmevent`, `riscv,event-to-mhpmcounters`, `riscv,raw-event-to-mhpmcounters`. schema refs `uint32-matrix`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; dependency rules for `riscv,event-to-mhpmevent`; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: compatible strings and node topology. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `uint32-matrix`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/riscv,pmu.yaml` and `make dtbs_check` against boards using this binding; the 2 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/perf/riscv,pmu.yaml -->
