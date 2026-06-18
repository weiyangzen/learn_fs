# Research: subset-b-000560

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apm.yaml` defines the root platform compatible binding titled `APM X-Gene SoC Platforms`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 2 accepted compatible sequences and lists 4 compatible tokens including `apm,mustang`, `apm,xgene-storm`, `apm,merlin`, `apm,xgene-shadowcat`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Khuong Dinh <khuong@os.amperecomputing.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/apm.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple.yaml` defines the root platform compatible binding titled `Apple ARM Machine`. ARM platforms using SoCs designed by Apple Inc., branded "Apple Silicon". This currently includes devices based on the "A7" SoC: - iPhone 5s - iPad Air (1) - iPad mini 2 - iPad mini 3 Devices based on the "A8" SoC: - iPhone 6 - iPhone 6 Plus - iPad mini 4 - iPod touch 6 - Apple TV HD Device based on the "A8X" SoC: - iPad Air 2 Devices based on the "A9" SoC: - iPhone 6s - iPhone 6s Plus - iPhone SE (2016) - iPad 5 Devices based on the "A9X" SoC: - iPad Pro (9.7-inch) - iPad Pro (12.9-inch) Devices based on the "A10" SoC: - iPhone 7 - iPhone 7 Plus - iPod touch 7 - iPad 6 - iPad 7 Devices based on the "A10X" SoC: - Apple TV 4K (1st generation) - iPad Pro (2nd Generation) (10.5 Inch) - iPad... The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 18 accepted compatible sequences and lists 111 compatible tokens including `apple,j71`, `apple,j72`, `apple,j73`, `apple,j85`, `apple,j85m`, `apple,j86`, `apple,j86m`, `apple,j87`, `apple,j87m`, `apple,n51` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Hector Martin <marcan@marcan.st>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/apple.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple/apple,pmgr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple/apple,pmgr.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple/apple,pmgr.yaml` defines the MMIO controller or bus binding titled `Apple SoC Power Manager (PMGR)`. Apple SoCs include PMGR blocks responsible for power management, which can control various clocks, resets, power states, and performance features. This node represents the PMGR as a syscon, with sub-nodes representing individual features. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `$nodename`, `compatible`, `reg`, `#address-cells`, `#size-cells` with required set `compatible`, `reg`. The `compatible` property uses `oneOf` with 2 accepted compatible sequences and lists 12 compatible tokens including `apple,s5l8960x-pmgr`, `apple,t7000-pmgr`, `apple,s8000-pmgr`, `apple,t8010-pmgr`, `apple,t8015-pmgr`, `apple,t8103-pmgr`, `apple,t8112-pmgr`, `apple,t6000-pmgr`, `apple,pmgr`, `syscon` and more. Pattern properties are `power-controller@[0-9a-f]+$`.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Hector Martin <marcan@marcan.st>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/power/apple,pmgr-pwrstate.yaml#`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/apple/apple,pmgr.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple/apple,pmgr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,cci-400.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,cci-400.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,cci-400.yaml` defines the MMIO controller or bus binding titled `ARM CCI Cache Coherent Interconnect`. ARM multi-cluster systems maintain intra-cluster coherency through a cache coherent interconnect (CCI) that is capable of monitoring bus transactions and manage coherency, TLB invalidations and memory barriers. It allows snooping and distributed virtual memory message broadcast across clusters, through memory mapped interface, with a global control register space and multiple sets of interface control registers, one per slave interface. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `$nodename`, `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges` with required set `#address-cells`, `#size-cells`, `compatible`, `ranges`, `reg`. The `compatible` property uses `enum` list and lists 3 compatible tokens including `arm,cci-400`, `arm,cci-500`, `arm,cci-550`. Pattern properties are `^slave-if@[0-9a-f]+$`, `^pmu@[0-9a-f]+$`.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Lorenzo Pieralisi <lorenzo.pieralisi@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,cci-400.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,cci-400.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-catu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-catu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-catu.yaml` defines the CoreSight trace/debug binding titled `Arm Coresight Address Translation Unit (CATU)`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. The CoreSight Address Translation Unit (CATU) translates addresses between an AXI master and system memory. The CATU is normally used along with the TMC to implement scattering of virtual trace buffers in physical memory. The CATU translates contiguous Virtual Addresses (VAs) from an AXI master into non-contiguou... The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses ordered `items` sequence for 2 compatible tokens and defines properties `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `power-domains`, `in-ports`. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `in-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mathieu Poirier <mathieu.poirier@linaro.org>, Mike Leach <mike.leach@linaro.org>, Leo Yan <leo.yan@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/arm/primecell.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Top-level conditionals: `allOf`. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-catu.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-catu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-cpu-debug.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-cpu-debug.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-cpu-debug.yaml` defines the CoreSight trace/debug binding titled `CoreSight CPU Debug Component`. CoreSight CPU debug component are compliant with the ARMv8 architecture reference manual (ARM DDI 0487A.k) Chapter 'Part H: External debug'. The external debug module is mainly used for two modes: self-hosted debug and external debug, and it can be accessed from mmio region from Coresight and eventually the debug module connects with CPU for debugging. And the debug module provides sample-based profiling extension, which can be used to sample CPU program counter, secure state and exception level, etc; usually every CPU has one dedicated debug module to be connected. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses ordered `items` sequence for 2 compatible tokens and defines properties `compatible`, `reg`, `clocks`, `clock-names`, `cpu`, `power-domains`. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `cpu`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mathieu Poirier <mathieu.poirier@linaro.org>, Mike Leach <mike.leach@linaro.org>, Leo Yan <leo.yan@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/arm/primecell.yaml#`, `/schemas/types.yaml#/definitions/phandle`. Top-level conditionals: `allOf`. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-cpu-debug.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-cpu-debug.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-cti.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-cti.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-cti.yaml` defines the CoreSight trace/debug binding titled `ARM Coresight Cross Trigger Interface (CTI) device.`. The CoreSight Embedded Cross Trigger (ECT) consists of CTI devices connected to one or more CoreSight components and/or a CPU, with CTIs interconnected in a star topology via the Cross Trigger Matrix (CTM), which is not programmable. The ECT components are not part of the trace generation data path and are thus not part of the CoreSight graph. The CTI component properties define the connections between the individual CTI and the components it is directly connected to, consisting of input and output hardware trigger signals. CTIs can have a maximum number of input and output hardware trigger signals (8 each for v1 CTI, 32 each for v2 CTI). The number is defined at design time, the maximum... The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses `oneOf` with 2 accepted compatible sequences for 3 compatible tokens and defines properties `$nodename`, `compatible`, `reg`, `cpu`, `power-domains`, `label`, `arm,cti-ctm-id`, `arm,cs-dev-assoc`, `#size-cells`, `#address-cells`, `access-controllers`. Required properties are `compatible`, `reg`, `clocks`, `clock-names`; graph-related pattern properties are `^trig-conns@([0-9]+)$`.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mike Leach <mike.leach@linaro.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/arm/primecell.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Top-level conditionals: `allOf`, `if`, `then`. Examples present: 4 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-cti.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-cti.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dummy-sink.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dummy-sink.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dummy-sink.yaml` defines the CoreSight trace/debug binding titled `ARM Coresight Dummy sink component`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. The Coresight dummy sink component is for the specific coresight sink devices kernel don't have permission to access or configure, e.g., CoreSight EUD on Qualcomm platforms. It is a mini-USB hub implemented to support the USB-based debug and trace capabilities. For this device, a dummy driver is needed to registe... The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses `enum` list for 1 compatible token and defines properties `compatible`, `label`, `in-ports`. Required properties are `compatible`, `in-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mike Leach <mike.leach@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>, James Clark <james.clark@linaro.org>, Mao Jinlong <jinlong.mao@oss.qualcomm.com>, Hao Zhang <quic_hazha@quicinc.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-dummy-sink.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dummy-sink.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dummy-source.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dummy-source.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dummy-source.yaml` defines the CoreSight trace/debug binding titled `ARM Coresight Dummy source component`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. The Coresight dummy source component is for the specific coresight source devices kernel don't have permission to access or configure. For some SOCs, there would be Coresight source trace components on sub-processor which are connected to AP processor via debug bus. For these devices, a dummy driver is needed to... The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses `enum` list for 1 compatible token and defines properties `compatible`, `label`, `arm,static-trace-id`, `out-ports`. Required properties are `compatible`, `out-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mike Leach <mike.leach@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>, James Clark <james.clark@linaro.org>, Mao Jinlong <jinlong.mao@oss.qualcomm.com>, Hao Zhang <quic_hazha@quicinc.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/uint32`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-dummy-source.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dummy-source.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dynamic-funnel.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dynamic-funnel.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dynamic-funnel.yaml` defines the CoreSight trace/debug binding titled `Arm CoreSight Programmable Trace Bus Funnel`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. The Coresight funnel merges 2-8 trace sources into a single trace stream with programmable enable and priority of input ports. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses ordered `items` sequence for 2 compatible tokens and defines properties `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `label`, `in-ports`, `out-ports`, `access-controllers`. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `in-ports`, `out-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mathieu Poirier <mathieu.poirier@linaro.org>, Mike Leach <mike.leach@linaro.org>, Leo Yan <leo.yan@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/arm/primecell.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Top-level conditionals: `allOf`. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-dynamic-funnel.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dynamic-funnel.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dynamic-replicator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dynamic-replicator.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dynamic-replicator.yaml` defines the CoreSight trace/debug binding titled `Arm Coresight Programmable Trace Bus Replicator`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. The Coresight replicator splits a single trace stream into two trace streams for systems that have more than one trace sink component. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses ordered `items` sequence for 2 compatible tokens and defines properties `compatible`, `reg`, `clocks`, `clock-names`, `label`, `power-domains`, `qcom,replicator-loses-context`, `in-ports`, `out-ports`. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `in-ports`, `out-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mathieu Poirier <mathieu.poirier@linaro.org>, Mike Leach <mike.leach@linaro.org>, Leo Yan <leo.yan@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/arm/primecell.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Top-level conditionals: `allOf`. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-dynamic-replicator.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-dynamic-replicator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-etb10.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-etb10.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-etb10.yaml` defines the CoreSight trace/debug binding titled `Arm CoreSight Embedded Trace Buffer`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. The CoreSight Embedded Trace Buffer stores traces in a dedicated SRAM that is used as a circular buffer. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses ordered `items` sequence for 2 compatible tokens and defines properties `compatible`, `reg`, `clocks`, `clock-names`, `label`, `power-domains`, `in-ports`. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `in-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mathieu Poirier <mathieu.poirier@linaro.org>, Mike Leach <mike.leach@linaro.org>, Leo Yan <leo.yan@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/arm/primecell.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Top-level conditionals: `allOf`. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-etb10.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-etb10.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-etm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-etm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-etm.yaml` defines the CoreSight trace/debug binding titled `Arm CoreSight Embedded Trace MacroCell`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. The Embedded Trace Macrocell (ETM) is a real-time trace module providing instruction and data tracing of a processor. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses `oneOf` with 2 accepted compatible sequences for 4 compatible tokens and defines properties `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `arm,coresight-loses-context-with-cpu`, `label`, `arm,cp14`, `qcom,skip-power-up`, `cpu`, `out-ports`, `access-controllers`. Required properties are `compatible`, `clocks`, `clock-names`, `cpu`, `out-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mathieu Poirier <mathieu.poirier@linaro.org>, Mike Leach <mike.leach@linaro.org>, Leo Yan <leo.yan@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/arm/primecell.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle`. Top-level conditionals: `allOf`. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-etm.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-etm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-static-funnel.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-static-funnel.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-static-funnel.yaml` defines the CoreSight trace/debug binding titled `Arm CoreSight Static Trace Bus Funnel`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. The Coresight static funnel merges 2-8 trace sources into a single trace stream. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses single `const` for 1 compatible token and defines properties `compatible`, `power-domains`, `label`, `in-ports`, `out-ports`. Required properties are `compatible`, `in-ports`, `out-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mathieu Poirier <mathieu.poirier@linaro.org>, Mike Leach <mike.leach@linaro.org>, Leo Yan <leo.yan@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-static-funnel.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-static-funnel.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-static-replicator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-static-replicator.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-static-replicator.yaml` defines the CoreSight trace/debug binding titled `Arm CoreSight Static Trace Bus Replicator`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. The Coresight replicator splits a single trace stream into two trace streams for systems that have more than one trace sink component. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses single `const` for 1 compatible token and defines properties `compatible`, `power-domains`, `clocks`, `clock-names`, `label`, `in-ports`, `out-ports`. Required properties are `compatible`, `in-ports`, `out-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mathieu Poirier <mathieu.poirier@linaro.org>, Mike Leach <mike.leach@linaro.org>, Leo Yan <leo.yan@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-static-replicator.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-static-replicator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-stm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-stm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-stm.yaml` defines the CoreSight trace/debug binding titled `Arm CoreSight System Trace MacroCell`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. The STM is a trace source that is integrated into a CoreSight system, designed primarily for high-bandwidth trace of instrumentation embedded into software. This instrumentation is made up of memory-mapped writes to the STM Advanced eXtensible Interface (AXI) slave, which carry information about the behavior of t... The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses ordered `items` sequence for 2 compatible tokens and defines properties `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `power-domains`, `out-ports`, `access-controllers`. Required properties are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `out-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mathieu Poirier <mathieu.poirier@linaro.org>, Mike Leach <mike.leach@linaro.org>, Leo Yan <leo.yan@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/arm/primecell.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Top-level conditionals: `allOf`. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-stm.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-stm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-tmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-tmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-tmc.yaml` defines the CoreSight trace/debug binding titled `Arm CoreSight Trace Memory Controller`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. Trace Memory Controller is used for Embedded Trace Buffer(ETB), Embedded Trace FIFO(ETF) and Embedded Trace Router(ETR) configurations. The configuration mode (ETB, ETF, ETR) is discovered at boot time when the device is probed. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses ordered `items` sequence for 2 compatible tokens and defines properties `compatible`, `reg`, `clocks`, `clock-names`, `label`, `iommus`, `power-domains`, `arm,buffer-size`, `arm,scatter-gather`, `arm,max-burst-size`, `in-ports`, `out-ports`, `memory-region`, `memory-region-names`, `access-controllers`. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `in-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mathieu Poirier <mathieu.poirier@linaro.org>, Mike Leach <mike.leach@linaro.org>, Leo Yan <leo.yan@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/arm/primecell.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/uint32`. Top-level conditionals: `allOf`. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-tmc.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-tmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-tpiu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-tpiu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-tpiu.yaml` defines the CoreSight trace/debug binding titled `Arm CoreSight Trace Port Interface Unit`. CoreSight components are compliant with the ARM CoreSight architecture specification and can be connected in various topologies to suit a particular SoCs tracing needs. These trace components can generally be classified as sinks, links and sources. Trace data produced by one or more sources flows through the intermediate links connecting the source to the currently selected sink. The CoreSight Trace Port Interface Unit captures trace data from the trace bus and outputs it to an external trace port. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding exports a CoreSight node contract around `compatible`, AMBA/PrimeCell resources, and graph ports. It uses ordered `items` sequence for 2 compatible tokens and defines properties `compatible`, `reg`, `clocks`, `clock-names`, `label`, `power-domains`, `in-ports`, `access-controllers`. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `in-ports`; graph-related pattern properties are none.

## Control Flow, State, and Persistence
The schema models trace topology rather than imperative flow. Validation first matches the CoreSight `compatible`, then applies common graph/PrimeCell constraints through `$ref` and `allOf`, and finally checks `in-ports`/`out-ports`, clocks, register windows, CPU associations, or memory regions depending on the component. Runtime trace routing is handled by CoreSight drivers; the YAML persists only ABI shape and endpoint wiring expectations.

## Dependencies and Integration Points
Maintainers: Mathieu Poirier <mathieu.poirier@linaro.org>, Mike Leach <mike.leach@linaro.org>, Leo Yan <leo.yan@linaro.org>, Suzuki K Poulose <suzuki.poulose@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/arm/primecell.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`. Top-level conditionals: `allOf`. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,coresight-tpiu.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,coresight-tpiu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,corstone1000.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,corstone1000.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,corstone1000.yaml` defines the root platform compatible binding titled `ARM Corstone1000`. ARM's Corstone1000 includes pre-verified Corstone SSE-710 subsystem that provides a flexible compute architecture that combines Cortex‑A and Cortex‑M processors. Support for Cortex‑A32, Cortex‑A35, Cortex‑A53 and Cortex-A320 processors. Two expansion systems for M-Class (or other) processors for adding sensors, connectivity, video, audio and machine learning at the edge System and security IPs to build a secure SoC for a range of rich IoT applications, for example gateways, smart cameras and embedded systems. Integrated Secure Enclave providing hardware Root of Trust and supporting seamless integration of the optional CryptoCell™-312 cryptographic accelerator. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 3 accepted compatible sequences and lists 3 compatible tokens including `arm,corstone1000-mps3`, `arm,corstone1000-fvp`, `arm,corstone1000-a320-fvp`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Abdellatif El Khlifi <abdellatif.elkhlifi@arm.com>, Hugues Kamba Mpiana <hugues.kambampiana@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,corstone1000.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,corstone1000.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,embedded-trace-extension.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,embedded-trace-extension.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,embedded-trace-extension.yaml` defines the devicetree schema binding titled `ARM Embedded Trace Extensions`. Arm Embedded Trace Extension(ETE) is a per CPU trace component that allows tracing the CPU execution. It overlaps with the CoreSight ETMv4 architecture and has extended support for future architecture changes. The trace generated by the ETE could be stored via legacy CoreSight components (e.g, TMC-ETR) or other means (e.g, using a per CPU buffer Arm Trace Buffer Extension (TRBE)). Since the ETE can be connected to legacy CoreSight components, a node must be listed per instance, along with any optional connection graph as per the coresight bindings. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `$nodename`, `compatible`, `cpu`, `power-domains`, `out-ports` with required set `compatible`, `cpu`. The `compatible` property uses ordered `items` sequence and lists 1 compatible token including `arm,embedded-trace-extension`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Suzuki K Poulose <suzuki.poulose@arm.com>, Mathieu Poirier <mathieu.poirier@linaro.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/phandle`. Top-level conditionals: no top-level conditionals. Examples present: 2 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,embedded-trace-extension.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,embedded-trace-extension.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,integrator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,integrator.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,integrator.yaml` defines the root platform compatible binding titled `ARM Integrator Boards`. These were the first ARM platforms officially supported by ARM Ltd. They are ARMv4, ARMv5 and ARMv6-capable using different core tiles, so the system is modular and can host a variety of CPU tiles called "core tiles" and referred to in the device tree as "core modules". The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 3 accepted compatible sequences and lists 3 compatible tokens including `arm,integrator-ap`, `arm,integrator-cp`, `arm,integrator-sp`. Top-level schema properties are `$nodename`, `compatible`; required properties are `compatible`, `core-module@10000000`.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Linus Walleij <linusw@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,integrator.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,integrator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,juno-fpga-apb-regs.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,juno-fpga-apb-regs.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,juno-fpga-apb-regs.yaml` defines the MMIO controller or bus binding titled `ARM Juno FPGA APB Registers`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells` with required set `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`. The `compatible` property uses ordered `items` sequence and lists 3 compatible tokens including `arm,juno-fpga-apb-regs`, `syscon`, `simple-mfd`. Pattern properties are `^led@[0-9a-f]+,[0-9a-f]$`.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Sudeep Holla <sudeep.holla@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/leds/register-bit-led.yaml#`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,juno-fpga-apb-regs.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,juno-fpga-apb-regs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,morello.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,morello.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,morello.yaml` defines the root platform compatible binding titled `ARM Morello Platforms`. The Morello architecture is an experimental extension to Armv8.2-A, which extends the AArch64 state with the principles proposed in version 7 of the Capability Hardware Enhanced RISC Instructions (CHERI) ISA. ARM's Morello Platforms are built as a research project to explore capability architectures based on arm. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 1 accepted compatible sequence and lists 3 compatible tokens including `arm,morello-sdp`, `arm,morello-fvp`, `arm,morello`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Vincenzo Frascino <vincenzo.frascino@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,morello.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,morello.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,realview.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,realview.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,realview.yaml` defines the root platform compatible binding titled `ARM RealView Boards`. The ARM RealView series of reference designs were built to explore the Arm11, Cortex-A8, and Cortex-A9 CPUs. This included new features compared to the earlier CPUs such as TrustZone and multicore (MPCore). The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 5 accepted compatible sequences and lists 5 compatible tokens including `arm,realview-eb`, `arm,realview-pb1176`, `arm,realview-pb11mp`, `arm,realview-pba8`, `arm,realview-pbx`. Top-level schema properties are `$nodename`, `compatible`, `soc`; required properties are `compatible`, `soc`.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Linus Walleij <linusw@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,realview.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,realview.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,scu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,scu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,scu.yaml` defines the MMIO device binding titled `ARM Snoop Control Unit (SCU)`. As part of the MPCore complex, Cortex-A5 and Cortex-A9 are provided with a Snoop Control Unit. The register range is usually 256 (0x100) bytes. References: - Cortex-A9: see DDI0407E Cortex-A9 MPCore Technical Reference Manual Revision r2p0 - Cortex-A5: see DDI0434B Cortex-A5 MPCore Technical Reference Manual Revision r0p1 - ARM11 MPCore: see DDI0360F ARM 11 MPCore Processor Technical Reference Manial Revision r2p0 The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg` with required set `compatible`, `reg`. The `compatible` property uses `enum` list and lists 3 compatible tokens including `arm,cortex-a9-scu`, `arm,cortex-a5-scu`, `arm,arm11mp-scu`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Linus Walleij <linusw@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,scu.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,scu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,trace-buffer-extension.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,trace-buffer-extension.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,trace-buffer-extension.yaml` defines the root platform compatible binding titled `ARM Trace Buffer Extensions`. Arm Trace Buffer Extension (TRBE) is a per CPU component for storing trace generated on the CPU to memory. It is accessed via CPU system registers. The software can verify if it is permitted to use the component by checking the TRBIDR register. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 1 compatible token including `arm,trace-buffer-extension`. Top-level schema properties are `$nodename`, `compatible`, `interrupts`; required properties are `compatible`, `interrupts`.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Anshuman Khandual <anshuman.khandual@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,trace-buffer-extension.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,trace-buffer-extension.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,versatile-sysreg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,versatile-sysreg.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,versatile-sysreg.yaml` defines the MMIO device binding titled `Arm Versatile system registers`. This is a system control registers block, providing multiple low level platform functions like board detection and identification, software interrupt generation, MMC and NOR Flash control, etc. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `panel` with required set `compatible`, `reg`. The `compatible` property uses ordered `items` sequence and lists 3 compatible tokens including `arm,versatile-sysreg`, `syscon`, `simple-mfd`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Linus Walleij <linusw@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,versatile-sysreg.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,versatile-sysreg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,versatile.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,versatile.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,versatile.yaml` defines the root platform compatible binding titled `ARM Versatile Boards`. The ARM Versatile boards are two variants of ARM926EJ-S evaluation boards with various pluggable interface boards, in essence the Versatile PB version is a superset of the Versatile AB version. The root node in the Versatile platforms must contain a core module child node. They are always at physical address 0x10000000 in all the Versatile variants. When fitted with the IB2 Interface Board, the Versatile AB will present an optional system controller node which controls the extra peripherals on the interface board. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 2 accepted compatible sequences and lists 2 compatible tokens including `arm,versatile-ab`, `arm,versatile-pb`. Top-level schema properties are `$nodename`, `compatible`; required properties are `compatible`, `core-module@10000000`.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Linus Walleij <linusw@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,versatile.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,versatile.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,vexpress-juno.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,vexpress-juno.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,vexpress-juno.yaml` defines the devicetree schema binding titled `ARM Versatile Express and Juno Boards`. ARM's Versatile Express platform were built as reference designs for exploring multicore Cortex-A class systems. The Versatile Express family contains both 32 bit (Aarch32) and 64 bit (Aarch64) systems. The board consist of a motherboard and one or more daughterboards (tiles). The motherboard provides a set of peripherals. Processor and RAM "live" on the tiles. The motherboard and each core tile should be described by a separate Device Tree source file, with the tile's description including the motherboard file using an include directive. As the motherboard can be initialized in one of two different configurations ("memory maps"), care must be taken to include the correct one. When a new... The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `$nodename`, `compatible`, `arm,vexpress,position`, `arm,vexpress,dcc` with required set none declared at the top level. The `compatible` property uses `oneOf` with 13 accepted compatible sequences and lists 16 compatible tokens including `arm,vexpress,v2p-ca9`, `arm,vexpress`, `arm,vexpress,v2p-ca5s`, `arm,vexpress,v2p-ca15`, `arm,vexpress,v2p-ca15,tc1`, `arm,vexpress,v2p-ca15_a7`, `arm,vexpress,v2f-1xv7,ca53x2`, `arm,vexpress,v2f-1xv7`, `arm,juno`, `arm,juno-r1` and more. Pattern properties are `^bus@[0-9a-f]+$`.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Sudeep Holla <sudeep.holla@arm.com>, Linus Walleij <linusw@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/simple-bus.yaml`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`. Top-level conditionals: `allOf`. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,vexpress-juno.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,vexpress-juno.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,vexpress-scc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,vexpress-scc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,vexpress-scc.yaml` defines the MMIO device binding titled `ARM Versatile Express Serial Configuration Controller`. Test chips for ARM Versatile Express platform implement SCC (Serial Configuration Controller) interface, used to set initial conditions for the test chip. In some cases its registers are also mapped in normal address space and can be used to obtain runtime information about the chip internals (like silicon temperature sensors) and as interface to other subsystems like platform configuration control and power management. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `interrupts` with required set `compatible`. The `compatible` property uses ordered `items` sequence and lists 2 compatible tokens including `arm,vexpress-scc,v2p-ca15_a7`, `arm,vexpress-scc`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Liviu Dudau <liviu.dudau@arm.com>, Sudeep Holla <sudeep.holla@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,vexpress-scc.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,vexpress-scc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/aspeed/aspeed,sbc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/aspeed/aspeed,sbc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/aspeed/aspeed,sbc.yaml` defines the MMIO device binding titled `ASPEED Secure Boot Controller`. The ASPEED SoCs have a register bank for interacting with the secure boot controller. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg` with required set `compatible`, `reg`. The `compatible` property uses ordered `items` sequence and lists 1 compatible token including `aspeed,ast2600-sbc`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Joel Stanley <joel@jms.id.au>, Andrew Jeffery <andrew@aj.id.au>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/aspeed/aspeed,sbc.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/aspeed/aspeed,sbc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/aspeed/aspeed.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/aspeed/aspeed.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/aspeed/aspeed.yaml` defines the root platform compatible binding titled `Aspeed SoC based boards`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 3 accepted compatible sequences and lists 91 compatible tokens including `delta,ahe50dc-bmc`, `facebook,galaxy100-bmc`, `facebook,wedge100-bmc`, `facebook,wedge40-bmc`, `microsoft,olympus-bmc`, `quanta,q71l-bmc`, `tyan,palmetto-bmc`, `yadro,vesnin-bmc`, `aspeed,ast2400`, `amd,daytonax-bmc` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Joel Stanley <joel@jms.id.au>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/aspeed/aspeed.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/aspeed/aspeed.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,at91rm9200-sdramc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,at91rm9200-sdramc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,at91rm9200-sdramc.yaml` defines the MMIO device binding titled `Microchip (Atmel) SDRAM / DDR Controller (RAMC / DDRAMC / UDDRC)`. The SDRAM/DDR Controller (often called RAMC or DDRAMC) in various Atmel/Microchip ARM9 and Cortex-A5/A7 SoCs manages external SDRAM / DDR memory. It is typically exposed as a syscon node for register access from other drivers (e.g. for initialization or mode configuration). No interrupts or clocks are usually required in the binding. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `clocks`, `clock-names` with required set `compatible`, `reg`. The `compatible` property uses `oneOf` with 3 accepted compatible sequences and lists 9 compatible tokens including `atmel,at91rm9200-sdramc`, `syscon`, `microchip,sama7d65-uddrc`, `microchip,sama7g5-uddrc`, `atmel,at91sam9260-sdramc`, `atmel,at91sam9g45-ddramc`, `atmel,sama5d3-ddramc`, `microchip,sam9x60-ddramc`, `microchip,sam9x7-ddramc`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Nicolas Ferre <nicolas.ferre@microchip.com>, Claudiu Beznea <claudiu.beznea@tuxon.dev>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/atmel,at91rm9200-sdramc.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,at91rm9200-sdramc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,at91rm9200-st.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,at91rm9200-st.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,at91rm9200-st.yaml` defines the MMIO controller or bus binding titled `Atmel System Timer`. The System Timer (ST) module in AT91RM9200 provides periodic tick and alarm capabilities. It is exposed as a simple multi-function device (simple-mfd + syscon) because it shares its register space and interrupt with other System Controller blocks. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `interrupts`, `clocks`, `#address-cells`, `#size-cells` with required set `compatible`, `reg`, `interrupts`, `clocks`. The `compatible` property uses ordered `items` sequence and lists 3 compatible tokens including `atmel,at91rm9200-st`, `syscon`, `simple-mfd`. Pattern properties are `^watchdog@[0-9a-f]+$`.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Nicolas Ferre <nicolas.ferre@microchip.com>, Claudiu Beznea <claudiu.beznea@tuxon.dev>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/watchdog/atmel,at91rm9200-wdt.yaml#`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/atmel,at91rm9200-st.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,at91rm9200-st.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,at91sam9260-pit.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,at91sam9260-pit.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,at91sam9260-pit.yaml` defines the MMIO device binding titled `Atmel AT91SAM9260 Periodic Interval Timer (PIT)`. The Periodic Interval Timer (PIT) is part of the System Controller of various Microchip 32-bit ARM-based SoCs (formerly Atmel AT91 series). It is a simple down-counter timer used mainly as the kernel tick source. The PIT is clocked from the slow clock and shares a single IRQ line with other System Controller peripherals. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `interrupts`, `clocks` with required set `compatible`, `reg`, `interrupts`. The `compatible` property uses single `const` and lists 1 compatible token including `atmel,at91sam9260-pit`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Nicolas Ferre <nicolas.ferre@microchip.com>, Claudiu Beznea <claudiu.beznea@tuxon.dev>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/atmel,at91sam9260-pit.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,at91sam9260-pit.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,sama5d2-secumod.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,sama5d2-secumod.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,sama5d2-secumod.yaml` defines the MMIO device binding titled `Microchip AT91 Security Module (SECUMOD)`. The Security Module also offers the PIOBU pins which can be used as GPIO pins. Note that they maintain their voltage during Backup/Self-refresh. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `gpio-controller`, `#gpio-cells` with required set `compatible`, `reg`. The `compatible` property uses `oneOf` with 2 accepted compatible sequences and lists 4 compatible tokens including `atmel,sama5d2-secumod`, `syscon`, `microchip,sama7d65-secumod`, `microchip,sama7g5-secumod`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Nicolas Ferre <nicolas.ferre@microchip.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/atmel,sama5d2-secumod.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,sama5d2-secumod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel-at91.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel-at91.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel-at91.yaml` defines the root platform compatible binding titled `Atmel AT91.`. Boards with a SoC of the Atmel AT91 or SMART family shall have the following The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 36 accepted compatible sequences and lists 108 compatible tokens including `atmel,at91rm9200`, `atmel,at91sam9260`, `atmel,at91sam9261`, `atmel,at91sam9263`, `atmel,at91sam9g20`, `atmel,at91sam9g45`, `atmel,at91sam9n12`, `atmel,at91sam9rl`, `atmel,at91sam9xe`, `atmel,at91sam9x60` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>, Claudiu Beznea <claudiu.beznea@microchip.com>, Nicolas Ferre <nicolas.ferre@microchip.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/atmel-at91.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel-at91.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/axiado.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/axiado.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/axiado.yaml` defines the root platform compatible binding titled `Axiado Platforms`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 1 accepted compatible sequence and lists 2 compatible tokens including `axiado,ax3000-evk`, `axiado,ax3000`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Harshit Shah <hshah@axiado.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/axiado.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/axiado.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/axis.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/axis.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/axis.yaml` defines the root platform compatible binding titled `Axis ARTPEC platforms`. ARM platforms using SoCs designed by Axis branded as "ARTPEC". The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 3 accepted compatible sequences and lists 6 compatible tokens including `axis,artpec6-dev-board`, `axis,artpec6`, `axis,artpec8-grizzly`, `axis,artpec8`, `axis,artpec9-alfred`, `axis,artpec9`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Jesper Nilsson <jesper.nilsson@axis.com>, Lars Persson <lars.persson@axis.com>, linux-arm-kernel@axis.com. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/axis.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/axis.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/axxia.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/axxia.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/axxia.yaml` defines the root platform compatible binding titled `Axxia AXM55xx`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 2 compatible tokens including `lsi,axm5516-amarillo`, `lsi,axm5516`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Anders Berg <anders.berg@lsi.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/axxia.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/axxia.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/bcm2835.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/bcm2835.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/bcm2835.yaml` defines the root platform compatible binding titled `Broadcom BCM2711/BCM2835 Platforms`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 5 accepted compatible sequences and lists 26 compatible tokens including `raspberrypi,400`, `raspberrypi,4-compute-module`, `raspberrypi,4-model-b`, `brcm,bcm2711`, `raspberrypi,5-model-b`, `brcm,bcm2712`, `raspberrypi,model-a`, `raspberrypi,model-a-plus`, `raspberrypi,model-b`, `raspberrypi,model-b-i2c0` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Eric Anholt <eric@anholt.net>, Stefan Wahren <wahrenst@gmx.net>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/bcm2835.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/bcm2835.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm11351.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm11351.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm11351.yaml` defines the root platform compatible binding titled `Broadcom BCM11351`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 2 compatible tokens including `brcm,bcm28155-ap`, `brcm,bcm11351`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Florian Fainelli <f.fainelli@gmail.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/brcm,bcm11351.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm11351.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm21664.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm21664.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm21664.yaml` defines the root platform compatible binding titled `Broadcom BCM21664`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 2 compatible tokens including `brcm,bcm21664-garnet`, `brcm,bcm21664`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Florian Fainelli <f.fainelli@gmail.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/brcm,bcm21664.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm21664.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm23550.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm23550.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm23550.yaml` defines the root platform compatible binding titled `Broadcom BCM23550`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 2 compatible tokens including `brcm,bcm23550-sparrow`, `brcm,bcm23550`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Florian Fainelli <f.fainelli@gmail.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/brcm,bcm23550.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm23550.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm4708.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm4708.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm4708.yaml` defines the root platform compatible binding titled `Broadcom BCM4708`. Broadcom BCM4708/47081/4709/47094/53012 Wi-Fi/network SoCs based on the iProc architecture (Northstar). The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 7 accepted compatible sequences and lists 55 compatible tokens including `asus,rt-ac56u`, `asus,rt-ac68u`, `buffalo,wxr-1750dhp`, `buffalo,wzr-1166dhp`, `buffalo,wzr-1166dhp2`, `buffalo,wzr-1750dhp`, `linksys,ea6300-v1`, `linksys,ea6500-v2`, `luxul,xap-1510-v1`, `luxul,xwc-1000` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Florian Fainelli <f.fainelli@gmail.com>, Hauke Mehrtens <hauke@hauke-m.de>, Rafal Milecki <zajec5@gmail.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/brcm,bcm4708.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm4708.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm53573.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm53573.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm53573.yaml` defines the root platform compatible binding titled `Broadcom BCM53573 SoCs family`. Broadcom BCM53573 / BCM47189 Wi-Fi SoCs derived from Northstar. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 2 accepted compatible sequences and lists 8 compatible tokens including `tenda,ac6-v1`, `tenda,w15e-v1`, `brcm,bcm53573`, `brcm,bcm947189acdbmr`, `luxul,xap-810-v1`, `luxul,xap-1440-v1`, `tenda,ac9`, `brcm,bcm47189`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Rafał Miłecki <rafal@milecki.pl>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/brcm,bcm53573.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcm53573.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcmbca.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcmbca.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcmbca.yaml` defines the root platform compatible binding titled `Broadcom Broadband SoC`. Broadcom Broadband SoCs include family of high performance DSL/PON/Wireless chips that can be used as home gateway, router and WLAN AP for residential, enterprise and carrier applications. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 17 accepted compatible sequences and lists 41 compatible tokens including `brcm,bcm947622`, `brcm,bcm47622`, `brcm,bcmbca`, `netgear,r8000p`, `tplink,archer-c2300-v1`, `zyxel,ex3510b`, `brcm,bcm4906`, `brcm,bcm4908`, `asus,gt-ac5300`, `brcm,bcm94908` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: William Zhang <william.zhang@broadcom.com>, Anand Gore <anand.gore@broadcom.com>, Kursad Oney <kursad.oney@broadcom.com>, Rafał Miłecki <rafal@milecki.pl>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/brcm,bcmbca.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,bcmbca.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,cygnus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,cygnus.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,cygnus.yaml` defines the root platform compatible binding titled `Broadcom Cygnus`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 9 compatible tokens including `brcm,bcm11300`, `brcm,bcm11320`, `brcm,bcm11350`, `brcm,bcm11360`, `brcm,bcm58300`, `brcm,bcm58302`, `brcm,bcm58303`, `brcm,bcm58305`, `brcm,cygnus`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Ray Jui <rjui@broadcom.com>, Scott Branden <sbranden@broadcom.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/brcm,cygnus.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,cygnus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,hr2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,hr2.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,hr2.yaml` defines the root platform compatible binding titled `Broadcom Hurricane 2`. Broadcom Hurricane 2 family of SoCs are used for switching control. These SoCs are based on Broadcom's iProc SoC architecture and feature a single core Cortex A9 ARM CPUs, DDR2/DDR3 memory, PCIe GEN-2, USB 2.0 and USB 3.0, serial and NAND flash and a PCIe attached integrated switching engine. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 3 compatible tokens including `ubnt,unifi-switch8`, `brcm,bcm53342`, `brcm,hr2`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Florian Fainelli <f.fainelli@gmail.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/brcm,hr2.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,hr2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,ns2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,ns2.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,ns2.yaml` defines the root platform compatible binding titled `Broadcom North Star 2 (NS2)`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 3 compatible tokens including `brcm,ns2-svk`, `brcm,ns2-xmc`, `brcm,ns2`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Ray Jui <rjui@broadcom.com>, Scott Branden <sbranden@broadcom.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/brcm,ns2.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,ns2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,nsp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,nsp.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,nsp.yaml` defines the root platform compatible binding titled `Broadcom Northstar Plus`. Broadcom Northstar Plus family of SoCs are used for switching control and management applications as well as residential router/gateway applications. The SoC features dual core Cortex A9 ARM CPUs, integrating several peripheral interfaces including multiple Gigabit Ethernet PHYs, DDR3 memory, PCIE Gen-2, USB 2.0 and USB 3.0, serial and NAND flash, SATA and several other IO controllers. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 7 accepted compatible sequences and lists 22 compatible tokens including `brcm,bcm958522er`, `brcm,bcm58522`, `brcm,nsp`, `brcm,bcm958525er`, `brcm,bcm958525xmc`, `brcm,bcm58525`, `brcm,bcm58535`, `brcm,bcm958622hr`, `brcm,bcm58622`, `brcm,bcm958623hr` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Ray Jui <rjui@broadcom.com>, Scott Branden <sbranden@broadcom.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/brcm,nsp.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,nsp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,stingray.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,stingray.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,stingray.yaml` defines the root platform compatible binding titled `Broadcom Stingray`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 4 compatible tokens including `brcm,bcm958742k`, `brcm,bcm958742t`, `brcm,bcm958802a802x`, `brcm,stingray`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Ray Jui <rjui@broadcom.com>, Scott Branden <sbranden@broadcom.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/brcm,stingray.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/brcm,stingray.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/raspberrypi,bcm2835-firmware.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/raspberrypi,bcm2835-firmware.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/raspberrypi,bcm2835-firmware.yaml` defines the devicetree schema binding titled `Raspberry Pi VideoCore firmware driver`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `mboxes`, `clocks`, `gpio`, `reset`, `power`, `pwm`, `touchscreen` with required set `compatible`, `mboxes`. The `compatible` property uses ordered `items` sequence and lists 2 compatible tokens including `raspberrypi,bcm2835-firmware`, `simple-mfd`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Eric Anholt <eric@anholt.net>, Stefan Wahren <wahrenst@gmx.net>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/input/touchscreen/touchscreen.yaml#`, `/schemas/power/raspberrypi,bcm2835-power.yaml#`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bcm/raspberrypi,bcm2835-firmware.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bcm/raspberrypi,bcm2835-firmware.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bitmain.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bitmain.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bitmain.yaml` defines the root platform compatible binding titled `Bitmain platform`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 2 compatible tokens including `bitmain,sophon-edge`, `bitmain,bm1880`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Manivannan Sadhasivam <manivannan.sadhasivam@linaro.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bitmain.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bitmain.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/blaize.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/blaize.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/blaize.yaml` defines the root platform compatible binding titled `Blaize Platforms`. Blaize Platforms using SoCs designed by Blaize Inc. The products based on the BLZP1600 SoC: - BLZP1600-SoM: SoM (System on Module) - BLZP1600-CB2: Development board CB2 based on BLZP1600-SoM BLZP1600 SoC integrates a dual core ARM Cortex A53 cluster and a Blaize Graph Streaming Processor for AI and ML workloads, plus a suite of connectivity and other peripherals. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 1 accepted compatible sequence and lists 2 compatible tokens including `blaize,blzp1600-cb2`, `blaize,blzp1600`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: James Cowgill <james.cowgill@blaize.com>, Matt Redfearn <matt.redfearn@blaize.com>, Neil Jones <neil.jones@blaize.com>, Nikolaos Pasaloukos <nikolaos.pasaloukos@blaize.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/blaize.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/blaize.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bst.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bst.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bst.yaml` defines the root platform compatible binding titled `BST platforms`. Black Sesame Technologies (BST) is a semiconductor company that produces automotive-grade system-on-chips (SoCs) for intelligent driving, focusing on computer vision and AI capabilities. The BST C1200 family includes SoCs for ADAS (Advanced Driver Assistance Systems) and autonomous driving applications. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 1 accepted compatible sequence and lists 2 compatible tokens including `bst,c1200-cdcu1.0-adas-4c2g`, `bst,c1200`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Ge Gordon <gordon.ge@bst.ai>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/bst.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/bst.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/calxeda.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/calxeda.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/calxeda.yaml` defines the root platform compatible binding titled `Calxeda Platforms`. Bindings for boards with Calxeda Cortex-A9 based ECX-1000 (Highbank) SOC or Cortex-A15 based ECX-2000 SOCs The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 2 compatible tokens including `calxeda,highbank`, `calxeda,ecx-2000`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Rob Herring <robh@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/calxeda.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/calxeda.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/calxeda/hb-sregs.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/calxeda/hb-sregs.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/calxeda/hb-sregs.yaml` defines the MMIO device binding titled `Calxeda Highbank system registers`. The Calxeda Highbank system has a block of MMIO registers controlling several generic system aspects. Those can be used to control some power management, they also contain some gate and PLL clocks. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `clocks` with required set `compatible`, `reg`. The `compatible` property uses single `const` and lists 1 compatible token including `calxeda,hb-sregs`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Andre Przywara <andre.przywara@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/calxeda/hb-sregs.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/calxeda/hb-sregs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/calxeda/l2ecc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/calxeda/l2ecc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/calxeda/l2ecc.yaml` defines the MMIO device binding titled `Calxeda Highbank L2 cache ECC`. Binding for the Calxeda Highbank L2 cache controller ECC device. This does not cover the actual L2 cache controller control registers, but just the error reporting functionality. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `interrupts` with required set `compatible`, `reg`, `interrupts`. The `compatible` property uses single `const` and lists 1 compatible token including `calxeda,hb-sregs-l2-ecc`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Andre Przywara <andre.przywara@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/calxeda/l2ecc.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/calxeda/l2ecc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cavium,thunder-88xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cavium,thunder-88xx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cavium,thunder-88xx.yaml` defines the root platform compatible binding titled `Cavium Thunder 88xx SoC`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 1 compatible token including `cavium,thunder-88xx`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Robert Richter <rric@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/cavium,thunder-88xx.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cavium,thunder-88xx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cci-control-port.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cci-control-port.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cci-control-port.yaml` defines the devicetree schema binding titled `CCI Interconnect Bus Masters`. Masters in the device tree connected to a CCI port (inclusive of CPUs and their cpu nodes). The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `cci-control-port` with required set none declared at the top level. The `compatible` property uses compatible schema and lists 0 compatible tokens including no explicit constants. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Lorenzo Pieralisi <lorenzo.pieralisi@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/types.yaml#/definitions/phandle`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/cci-control-port.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cci-control-port.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cirrus/cirrus,ep9301.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cirrus/cirrus,ep9301.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cirrus/cirrus,ep9301.yaml` defines the root platform compatible binding titled `Cirrus Logic EP93xx platforms`. The EP93xx SoC is a ARMv4T-based with 200 MHz ARM9 CPU. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 3 accepted compatible sequences and lists 4 compatible tokens including `technologic,ts7250`, `cirrus,ep9301`, `liebherr,bk3`, `cirrus,edb9302`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Alexander Sverdlin <alexander.sverdlin@gmail.com>, Nikita Shubin <nikita.shubin@maquefel.me>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/cirrus/cirrus,ep9301.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cirrus/cirrus,ep9301.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cix.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cix.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cix.yaml` defines the root platform compatible binding titled `CIX platforms`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 1 accepted compatible sequence and lists 3 compatible tokens including `radxa,orion-o6`, `xunlong,orangepi-6-plus`, `cix,sky1`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Peter Chen <peter.chen@cixtech.com>, Fugang Duan <fugang.duan@cixtech.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/cix.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cix.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cpus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cpus.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cpus.yaml` defines the cpu-node binding titled `ARM CPUs`. The device tree allows to describe the layout of CPUs in a system through the "cpus" node, which in turn contains a number of subnodes (ie "cpu") defining properties for every cpu. Bindings for CPU nodes follow the Devicetree Specification, available from: https://www.devicetree.org/specifications/ with updates for 32-bit and 64-bit ARM systems provided in this document. ================================ Convention used in this document ================================ This document follows the conventions described in the Devicetree Specification, with the addition: - square brackets define bitfields, eg reg[7:0] value of the bitfield in the reg property contained in bits 7 down to 0 ====... The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding describes ARM `cpu` subnodes under `/cpus`. It accepts a large `compatible` catalogue (151 tokens), requires `device_type`, `reg`, `compatible`, and exposes CPU topology, boot, power, OPP, supply, cache, idle-state, interconnect, and coherency properties such as `reg`, `compatible`, `enable-method`, `cpu-release-addr`, `cpu-idle-states`, `capacity-dmips-mhz`, `cci-control-port`, `dynamic-power-coefficient`, `interconnects`, `nvmem-cells`, `nvmem-cell-names`, `performance-domains`, `power-domains`, `power-domain-names`, `resets`, `arm-supply`, `cpu0-supply`, `mem-supply`, and 13 more.

## Control Flow, State, and Persistence
Validation follows CPU-node schema composition: core devicetree CPU requirements are checked first, then conditional blocks constrain `enable-method`, `cpu-release-addr`, idle states, PSCI/spin-table boot paths, performance domains, supplies, and implementation-specific compatible strings. The file does not store runtime CPU state; it locks the ABI used by architecture boot code, CPU hotplug, cpufreq/OPP, idle, power-domain, and topology code.

## Dependencies and Integration Points
Maintainers: Lorenzo Pieralisi <lorenzo.pieralisi@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/cpu.yaml#`, `/schemas/opp/opp-v1.yaml#`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-matrix`, and 1 more. Top-level conditionals: `allOf`, `dependencies`. Examples present: 4 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/cpus.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cpus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/digicolor.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/digicolor.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/digicolor.yaml` defines the root platform compatible binding titled `Conexant Digicolor Platforms`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses single `const` and lists 1 compatible token including `cnxt,cx92755`. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Baruch Siach <baruch@tkos.co.il>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/digicolor.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/digicolor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/firmware/linaro,optee-tz.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/firmware/linaro,optee-tz.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/firmware/linaro,optee-tz.yaml` defines the firmware interface binding titled `OP-TEE`. OP-TEE is a piece of software using hardware features to provide a Trusted Execution Environment. The security can be provided with ARM TrustZone, but also by virtualization or a separate chip. We're using "linaro" as the first part of the compatible property for the reference implementation maintained by Linaro. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `$nodename`, `compatible`, `interrupts`, `method` with required set `compatible`, `method`. The `compatible` property uses single `const` and lists 1 compatible token including `linaro,optee-tz`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Jens Wiklander <jens.wiklander@linaro.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 2 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/firmware/linaro,optee-tz.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/firmware/linaro,optee-tz.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/firmware/tlm,trusted-foundations.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/firmware/tlm,trusted-foundations.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/firmware/tlm,trusted-foundations.yaml` defines the firmware interface binding titled `Trusted Foundations`. Boards that use the Trusted Foundations secure monitor can signal its presence by declaring a node compatible under the /firmware/ node The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `$nodename`, `compatible`, `tlm,version-major`, `tlm,version-minor` with required set `compatible`, `tlm,version-major`, `tlm,version-minor`. The `compatible` property uses single `const` and lists 1 compatible token including `tlm,trusted-foundations`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Stephen Warren <swarren@nvidia.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/types.yaml#/definitions/uint32`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/firmware/tlm,trusted-foundations.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/firmware/tlm,trusted-foundations.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/freescale/fsl,imx51-m4if.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/freescale/fsl,imx51-m4if.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/freescale/fsl,imx51-m4if.yaml` defines the MMIO device binding titled `Freescale Multi Master Multi Memory Interface (M4IF) and Tigerp module`. collect the imx devices, which only have compatible and reg property The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg` with required set `compatible`, `reg`. The `compatible` property uses `oneOf` with 2 accepted compatible sequences and lists 7 compatible tokens including `fsl,imx25-aips`, `fsl,imx51-m4if`, `fsl,imx51-tigerp`, `fsl,imx51-aipstz`, `fsl,imx53-aipstz`, `fsl,imx7d-pcie-phy`, `fsl,imx53-tigerp`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Frank Li <Frank.Li@nxp.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/freescale/fsl,imx51-m4if.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/freescale/fsl,imx51-m4if.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/freescale/fsl,imx7ulp-pm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/freescale/fsl,imx7ulp-pm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/freescale/fsl,imx7ulp-pm.yaml` defines the MMIO device binding titled `Freescale i.MX7ULP Power Management Components`. The Multi-System Mode Controller (MSMC) is responsible for sequencing the MCU into and out of all stop and run power modes. Specifically, it monitors events to trigger transitions between power modes while controlling the power, clocks, and memories of the MCU to achieve the power consumption and functionality of that mode. The WFI or WFE instruction is used to invoke a Sleep, Deep Sleep or Standby modes for either Cortex family. Run, Wait, and Stop are the common terms used for the primary operating modes of Kinetis microcontrollers. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `#clock-cells`, `clocks`, `clock-names` with required set `compatible`, `reg`, `#clock-cells`. The `compatible` property uses single `const` and lists 1 compatible token including `fsl,imx7ulp-smc1`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: A.s. Dong <aisheng.dong@nxp.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/freescale/fsl,imx7ulp-pm.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/freescale/fsl,imx7ulp-pm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/freescale/fsl,imx7ulp-sim.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/freescale/fsl,imx7ulp-sim.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/freescale/fsl,imx7ulp-sim.yaml` defines the MMIO device binding titled `Freescale i.MX7ULP System Integration Module`. The system integration module (SIM) provides system control and chip configuration registers. In this module, chip revision information is located in JTAG ID register, and a set of registers have been made available in DGO domain for SW use, with the objective to maintain its value between system resets. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg` with required set `compatible`, `reg`. The `compatible` property uses ordered `items` sequence and lists 2 compatible tokens including `fsl,imx7ulp-sim`, `syscon`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Shawn Guo <shawnguo@kernel.org>, Sascha Hauer <s.hauer@pengutronix.de>, Fabio Estevam <festevam@gmail.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/freescale/fsl,imx7ulp-sim.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/freescale/fsl,imx7ulp-sim.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/fsl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/fsl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/fsl.yaml` defines the root platform compatible binding titled `Freescale i.MX Platforms`. It constrains devicetree nodes for this ARM platform or hardware block through compatible-string and property validation.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 207 accepted compatible sequences and lists 847 compatible tokens including `armadeus,imx1-apf9328`, `fsl,imx1ads`, `fsl,imx1`, `creative,x-fi3`, `fsl,imx23-evk`, `fsl,stmp378x-devb`, `olimex,imx23-olinuxino`, `sandisk,sansa_fuze_plus`, `fsl,imx23`, `fsl,imx25-pdk` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Shawn Guo <shawnguo@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/fsl.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/fsl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/gemini.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/gemini.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/gemini.yaml` defines the root platform compatible binding titled `Cortina systems Gemini platforms`. The Gemini SoC is the project name for an ARMv4 FA525-based SoC originally produced by Storlink Semiconductor around 2005. The company was renamed later renamed Storm Semiconductor. The chip product name is Storlink SL3516. It was derived from earlier products from Storm named SL3316 (Centroid) and SL3512 (Bulverde). Storm Semiconductor was acquired by Cortina Systems in 2008 and the SoC was produced and used for NAS and similar usecases. In 2014 Cortina Systems was in turn acquired by Inphi, who seem to have discontinued this product family. Many of the IP blocks used in the SoC comes from Faraday Technology. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 12 accepted compatible sequences and lists 14 compatible tokens including `storlink,gemini324`, `storm,sl93512r`, `cortina,gemini`, `dlink,dir-685`, `dlink,dns-313`, `edimax,ns-2502`, `itian,sq201`, `raidsonic,ib-4220-b`, `ssi,1328`, `teltonika,rut1xx` and more. Top-level schema properties are `$nodename`, `compatible`; required properties are none declared at the top level.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Linus Walleij <linusw@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/gemini.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/gemini.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/google.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/google.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/google.yaml` defines the root platform compatible binding titled `Google Tensor platforms`. ARM platforms using SoCs designed by Google branded "Tensor" used in Pixel devices. Currently upstream this is devices using "gs101" SoC which is found in Pixel 6, Pixel 6 Pro and Pixel 6a. Google have a few different names for the SoC: - Marketing name ("Tensor") - Codename ("Whitechapel") - SoC ID ("gs101") - Die ID ("S5P9845") Likewise there are a couple of names for the actual device - Marketing name ("Pixel 6") - Codename ("Oriole") Devicetrees should use the lowercased SoC ID and lowercased board codename, e.g. gs101 and gs101-oriole. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses `oneOf` with 1 accepted compatible sequence and lists 3 compatible tokens including `google,gs101-oriole`, `google,gs101-raven`, `google,gs101`. Top-level schema properties are `$nodename`, `compatible`, `ect`; required properties are `ect`.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Peter Griffin <peter.griffin@linaro.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/google.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/google.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/cpuctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/cpuctrl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/cpuctrl.yaml` defines the MMIO controller or bus binding titled `Hisilicon CPU controller`. The clock registers and power registers of secondary cores are defined in CPU controller, especially in HIX5HD2 SoC. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges` with required set `compatible`, `reg`. The `compatible` property uses ordered `items` sequence and lists 1 compatible token including `hisilicon,cpuctrl`. Pattern properties are `^clock@[0-9a-f]+$`.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Wei Xu <xuwei5@hisilicon.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional child objects constrained by a nested schema. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/hisilicon/controller/cpuctrl.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/cpuctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hi3798cv200-perictrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hi3798cv200-perictrl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hi3798cv200-perictrl.yaml` defines the MMIO controller or bus binding titled `Hisilicon Hi3798CV200 Peripheral Controller`. The Hi3798CV200 Peripheral Controller controls peripherals, queries their status, and configures some functions of peripherals. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges` with required set `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`. The `compatible` property uses ordered `items` sequence and lists 3 compatible tokens including `hisilicon,hi3798cv200-perictrl`, `syscon`, `simple-mfd`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Wei Xu <xuwei5@hisilicon.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional child objects constrained by a nested schema. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/hisilicon/controller/hi3798cv200-perictrl.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hi3798cv200-perictrl.yaml -->
