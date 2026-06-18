# sources/distributed-fs/ceph-client/include/linux/rpmsg/qcom_glink.h

## Purpose
`qcom_glink.h` declares Qualcomm GLINK SMEM registration and subsystem-restart notification helpers.

## Important APIs, types, and functions
The header forward-declares `struct qcom_glink_smem`. Public helpers are `qcom_glink_ssr_notify()`, `qcom_glink_smem_register()`, and `qcom_glink_smem_unregister()`, with no-op or `NULL` stubs when the relevant GLINK/SMEM configs are disabled.

## Control flow, state, and persistence
Qualcomm platform code registers a GLINK SMEM transport using a parent device and device-tree node, after which GLINK channels can appear as rpmsg devices. Subsystem restart paths call `qcom_glink_ssr_notify()` with an SSR name so GLINK users can react to remote resets. Persistent state is held by the GLINK SMEM transport and device model.

## Dependencies and integration points
It depends on `struct device`, `struct device_node`, `CONFIG_RPMSG_QCOM_GLINK`, and `CONFIG_RPMSG_QCOM_GLINK_SMEM`. Integration points include qcom remoteproc, SMEM-backed GLINK transport, subsystem restart, and rpmsg client drivers.

## Risks and test signals
Risks include edge registration before link readiness, stale channel devices after subsystem restart, disabled-config stubs returning no edge, and teardown races with active endpoints. Test signals include qcom remoteproc boot/shutdown, channel enumeration, endpoint traffic, SSR/restart cleanup, and module unload.
