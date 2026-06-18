<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-remote-etm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-remote-etm.yaml

## Purpose
This schema describes Qualcomm CoreSight remote ETM nodes for enabling trace collection from remote processors such as modems.

## Important APIs, Types, And Functions
It requires `compatible = "qcom,coresight-remote-etm"` and graph `out-ports` with a single `port` to the CoreSight trace bus. `label` is optional.

## Control Flow
Validation is strict and requires the output graph. There is no MMIO or clock requirement because the traced processor is remote.

## State And Persistence
The DT records a logical CoreSight source and its graph output. Runtime state is managed through CoreSight sysfs and remote processor trace infrastructure.

## Dependencies And Integration Points
It depends on graph bindings and integrates with funnels, TMC sinks, and remote processor trace enable paths.

## Risks
Without a valid output endpoint, the remote ETM cannot be connected to a sink. Because there is no register resource, all useful integration depends on graph correctness and driver support.

## Test Signals
`dtbs_check` validates graph shape. Runtime signal is enabling the remote ETM source and collecting trace through a CoreSight sink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-remote-etm.yaml -->
