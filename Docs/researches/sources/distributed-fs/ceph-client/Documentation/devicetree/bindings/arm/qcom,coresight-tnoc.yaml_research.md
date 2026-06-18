<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tnoc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tnoc.yaml

## Purpose
This binding describes Qualcomm CoreSight Trace Network-on-Chip aggregator instances that combine trace streams and route them toward sinks.

## Important APIs, Types, And Functions
It uses a custom `select` for `qcom,coresight-tnoc` to avoid matching every `arm,primecell` node. Required properties include node name `tn@...`, compatible `qcom,coresight-tnoc`, `arm,primecell`, `reg`, APB `clocks`/`clock-names = "apb_pclk"`, `in-ports`, and `out-ports`.

## Control Flow
Validation requires full CoreSight graph connectivity and PrimeCell-compatible clock naming. Additional properties are rejected.

## State And Persistence
The DT stores MMIO, APB clock, and trace routing graph. Runtime state is the active CoreSight route and hardware aggregation configuration.

## Dependencies And Integration Points
It integrates with PrimeCell/AMBA probing, graph endpoints, TPDM/ITNOC inputs, funnels, and TMC sinks.

## Risks
The custom select is important; removing it can cause schema collisions with generic PrimeCell devices. Broken graph endpoints block trace path construction.

## Test Signals
`dtbs_check` validates graph and PrimeCell clock shape. CoreSight path enablement and trace capture validate runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tnoc.yaml -->
