# sources/distributed-fs/ceph-client/include/linux/firmware/qcom/qcom_qseecom.h

## Purpose
This header exposes the Qualcomm QSEECOM client-facing wrapper for Secure Execution Environment applications. It models a QSEE application as an auxiliary bus client and gives consumers a narrow send/receive entry point.

## APIs, types, and control flow
`struct qseecom_client` embeds `struct auxiliary_device` and stores the loaded secure app `app_id`. `qcom_qseecom_app_send()` is an inline wrapper around `qcom_scm_qseecom_app_send(client->app_id, req, req_size, rsp, rsp_size)`. The effective flow is client driver owns a `qseecom_client`, allocates TrustZone/DMA-safe request and response buffers, fills the request, then routes the call through the Qualcomm SCM layer.

## State and dependencies
Persistent state is the auxiliary device identity plus firmware app id. It depends on `linux/auxiliary_bus.h`, DMA mapping types, and `qcom_scm.h`; QSEECOM behavior is provided by the SCM implementation and `CONFIG_QCOM_QSEECOM`.

## Integration, risks, and tests
Callers must pass TZ memory buffers with valid sizes and app-specific layout. Risks are stale app ids, non-secure buffers, bad request ABI, and treating SCM errors as app responses. Test signals include disabled-config `-EINVAL` paths in SCM, successful auxiliary client bind/probe, DMA/TZ allocation lifetime tests, and app-specific request/response round trips.
