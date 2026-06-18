# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5.h

Purpose: declares the shared Q6V5 helper state and exported lifecycle functions used by Qualcomm remoteproc implementations.

Important APIs/types/functions: `struct qcom_q6v5` stores the parent device, associated `struct rproc`, SMEM stop state, AOSS QMP handle, interconnect path, named IRQs, handover state, start/stop completions, crash-reason SMEM id, running flag, optional load-state string, and optional handover callback. The header declares init/deinit, prepare/unprepare, stop request, start wait, and panic helpers.

Control flow: this header has no executable flow. Its contract is that platform-specific drivers allocate or embed `struct qcom_q6v5`, call `qcom_q6v5_init()` during probe after allocating `rproc`, call `qcom_q6v5_prepare()` before boot, wait with `qcom_q6v5_wait_for_start()`, stop with `qcom_q6v5_request_stop()`, and release common votes/IRQs with `qcom_q6v5_unprepare()` and `qcom_q6v5_deinit()`.

State and persistence: the structure is runtime driver state only. It tracks completion and resource ownership around each boot cycle and references external persistent-looking objects such as SMEM state and QMP, but it owns no on-disk or firmware-persistent data.

Dependencies and integration: depends on Linux completions and forward declarations for `icc_path`, `rproc`, `qcom_smem_state`, and `qcom_sysmon`; it includes AOSS QMP definitions. It is private to kernel Qualcomm remoteproc drivers rather than a UAPI.

Risks and test signals: the header encodes ownership expectations that are easy to violate in callers. Tests and reviews should confirm every embedding driver initializes the struct once, does not call helpers after deinit, protects handover resource release when `qcom_q6v5_unprepare()` returns true, and supplies a valid `rproc`/platform device with the required named IRQ and `"stop"` SMEM state resources.
