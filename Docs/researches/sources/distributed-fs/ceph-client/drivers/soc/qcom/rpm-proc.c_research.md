# sources/distributed-fs/ceph-client/drivers/soc/qcom/rpm-proc.c

## Purpose

`rpm-proc.c` is a small platform driver that represents the Qualcomm RPM processor/subsystem node. It optionally registers an SMD edge described by a `smd-edge` child and populates child devices below the RPM processor node.

## Important APIs, Types, and Functions

`rpm_proc_probe()` and `rpm_proc_remove()` are the only runtime functions. Probe uses `of_get_child_by_name()`, `qcom_smd_register_edge()`, `devm_of_platform_populate()`, and stores the optional `struct qcom_smd_edge *` as drvdata. The driver binds `qcom,rpm-proc`.

## Control Flow

Probe looks for a `smd-edge` child. If present, it registers the edge and handles errors with `dev_err_probe()`. It then populates child platform devices. If child population fails after edge registration, the edge is unregistered. Remove unregisters the edge if one exists. Registration uses `arch_initcall` so RPM infrastructure is available early for dependent child devices.

## State and Persistence Behavior

The driver owns only the optional SMD edge handle and child device population. There is no persistent storage or hardware state mutation in this file beyond registering the communication edge with the SMD/rpmsg infrastructure.

## Dependencies and Integration Points

It depends on OF platform population and Qualcomm SMD rpmsg helpers. It is an integration parent for RPM child drivers such as SMD RPM, regulators, clocks, and other resources under the RPM processor DT node.

## Risks and Edge Cases

If no `smd-edge` child exists, the driver still populates children; those children must not assume an edge exists unless their DT requires it. Devm child population is automatic, but explicit SMD edge unregister must stay paired with registration. Probe deferral comes from edge registration or child population.

## Test Signals

Test with and without `smd-edge`, failed edge registration, failed child population after edge registration, remove ordering, and initcall ordering with child drivers that depend on RPM communication.
