<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tpdm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tpdm.yaml

## Purpose
This binding describes Qualcomm Trace, Profiling and Diagnostics Monitor devices that collect implementation-defined, basic count, tenure count, CMB, and DSB datasets and forward them to TPDA/funnels.

## Important APIs, Types, And Functions
Compatible is either `qcom,coresight-static-tpdm` or `qcom,coresight-tpdm`, `arm,primecell`. Required properties are `compatible`, `reg`, `clocks`, and `clock-names`; dataset properties include `qcom,dsb-element-bits`, `qcom,cmb-element-bits`, `qcom,dsb-msrs-num`, and `qcom,cmb-msrs-num`. `out-ports` is optional graph output.

## Control Flow
Custom selection prevents PrimeCell overmatching. Validation enforces enum bounds for dataset widths and MSR counts, while graph output connects TPDM to TPDA or funnel.

## State And Persistence
The DT records monitor MMIO, clock, dataset capabilities, and trace graph output. Runtime state is dataset collection and CoreSight route state.

## Dependencies And Integration Points
It integrates with PrimeCell/AMBA, CoreSight graph routing, TPDA aggregators, funnels, and TMC sinks.

## Risks
Incorrect dataset element width or MSR count can make TPDA/driver programming wrong. Static TPDM nodes lack MMIO, so driver handling must match the compatible branch.

## Test Signals
`dtbs_check` validates properties and graph shape. Runtime signals include TPDM source enablement, integration-test data generation, and sink trace movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tpdm.yaml -->
