<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-ctcu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-ctcu.yaml

## Purpose
This schema describes Qualcomm CoreSight TMC Control Unit devices that help TMC ETR sinks filter trace data by source Trace ID.

## Important APIs, Types, And Functions
It validates compatible `qcom,sa8775p-ctcu` or `qcom,qcs8300-ctcu`, `qcom,sa8775p-ctcu`, plus `reg`, optional APB clock, optional `label`, and graph `in-ports` from CoreSight trace buses.

## Control Flow
Validation requires compatible, reg, and in-ports. Graph port nodes are validated by the generic graph schema, allowing port indices 0 and 1.

## State And Persistence
The DT records the CTCU MMIO region, clock, and trace graph inputs. Runtime state is in CoreSight drivers configuring trace filters.

## Dependencies And Integration Points
It depends on graph bindings, clocks, and CoreSight TMC/ETR endpoint links.

## Risks
Broken graph endpoint phandles can make trace paths unusable even if the device probes. Missing clock data can affect APB register access on platforms that require it.

## Test Signals
`dtbs_check` validates graph shape. Runtime CoreSight path discovery and ETR trace filtering validate integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-ctcu.yaml -->
