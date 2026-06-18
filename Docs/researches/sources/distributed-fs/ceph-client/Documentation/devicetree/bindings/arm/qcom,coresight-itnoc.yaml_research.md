<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-itnoc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-itnoc.yaml

## Purpose
This binding describes Qualcomm CoreSight Interconnect Trace Network-on-Chip links that forward subsystem trace data to an aggregator TNOC.

## Important APIs, Types, And Functions
The node name matches `itnoc@...`; required properties include `compatible = "qcom,coresight-itnoc"`, `reg`, one APB clock with `clock-names = "apb"`, graph `in-ports`, and a single output `out-ports/port`.

## Control Flow
Validation requires both graph directions and rejects additional properties. Input ports can use small hexadecimal port indices; output is a fixed port object.

## State And Persistence
The DT records trace interconnect MMIO, clock, and graph connectivity. Runtime state is CoreSight routing state.

## Dependencies And Integration Points
It integrates with CoreSight graph endpoints, clock providers, TPDM sources, and aggregator TNOC nodes.

## Risks
Trace graph errors are high-impact: a missing remote endpoint can prevent source-to-sink path construction. Clock-name mismatch prevents driver clock lookup.

## Test Signals
`dtbs_check` validates graph and clock shape; CoreSight sysfs path discovery and trace capture validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-itnoc.yaml -->
