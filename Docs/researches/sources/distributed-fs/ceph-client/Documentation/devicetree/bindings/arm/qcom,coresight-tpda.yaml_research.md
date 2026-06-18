<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tpda.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tpda.yaml

## Purpose
This schema describes Qualcomm Trace, Profiling and Diagnostics Aggregator devices that packetize and timestamp TPDM data using MIPI STPv2 and forward it over ATB.

## Important APIs, Types, And Functions
It uses custom selection on `qcom,coresight-tpda`. Required properties include node name `tpda@...`, compatible `qcom,coresight-tpda`, `arm,primecell`, `reg`, APB clock with `apb_pclk`, `in-ports`, and `out-ports`; `label` is optional.

## Control Flow
Validation requires both input and output CoreSight graph sides. The description also documents sysfs integration-test commands that generate TPDM test data and observe sink write pointers.

## State And Persistence
The DT records TPDA MMIO, clock, and graph links. Runtime state is aggregation, packetization, and active CoreSight route state.

## Dependencies And Integration Points
It integrates with TPDM sources, funnels, TMC sinks, graph bindings, and PrimeCell/AMBA clocking.

## Risks
A trace path must contain only one TPDA between a TPDM source and sink; graph mistakes can create invalid topology. Missing APB clock prevents register access.

## Test Signals
`dtbs_check` validates the node; CoreSight integration tests, sink `rwp` movement, and trace capture are direct runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tpda.yaml -->
