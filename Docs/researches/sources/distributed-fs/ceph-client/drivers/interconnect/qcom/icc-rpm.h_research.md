# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpm.h

Purpose: shared data contract for legacy Qualcomm SMD RPM interconnect drivers.

Important APIs/types/functions: defines RPM request IDs, `enum qcom_icc_type`, `struct rpm_clk_resource`, provider/QoS/node/descriptor structs, clock resource externs, `qnoc_probe()`, `qnoc_remove()`, and low-level RPM helper prototypes.

Control flow: SoC topology files instantiate nodes/descriptors; `icc-rpm.c` consumes them for provider registration, QoS programming, aggregation, and RPM/clock voting.

State and persistence: struct fields define persistent provider and node runtime state, including cached bus rates and aggregate arrays.

Dependencies/integration: SMD RPM, RPM ICC dt-bindings, clocks, interconnect provider APIs, platform devices.

Risks and test signals: compile-test all legacy Qualcomm topologies, validate coefficients, nonzero buswidth/channel assumptions, RPM IDs, and tag/state bit compatibility.
