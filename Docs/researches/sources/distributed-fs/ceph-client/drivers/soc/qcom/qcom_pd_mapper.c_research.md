# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_pd_mapper.c

## Purpose

`qcom_pd_mapper.c` implements an in-kernel Qualcomm Protection Domain Mapper service. It exposes a QRTR/QMI SERVREG LOC server that answers domain-list requests for known SoC protection domains and acknowledges local process-failure-reason reports. Its goal is to replace or supplement a userspace pd-mapper daemon on platforms with static domain topology.

## Important APIs, Types, and Functions

`struct qcom_pdm_domain_data` describes one domain, instance id, and associated service names. Runtime objects are `qcom_pdm_data`, `qcom_pdm_service`, and `qcom_pdm_domain`. `qcom_pdm_add_domain()` builds a service-to-domains list, always registering the domain under `tms/servreg` and additionally under listed services. `qcom_pdm_get_domain_list()` handles `SERVREG_GET_DOMAIN_LIST_REQ`; `qcom_pdm_pfr()` handles `SERVREG_LOC_PFR_REQ`. `qcom_pdm_start()` selects the current machine from `qcom_pdm_domains`, initializes `qmi_handle`, adds static domains, and registers the QMI server.

## Control Flow

The auxiliary driver binds to `qcom_common.pd-mapper`. Probe serializes global startup under `qcom_pdm_mutex`; the first probe calls `qcom_pdm_start()` and later probes increment a refcount. QMI message dispatch is provided by `qmi_interface.c` using `qcom_pdm_msg_handlers`. For domain-list requests, the handler computes the requested offset, looks up the service, fills response metadata, copies up to `SERVREG_DOMAIN_LIST_LENGTH` domains, sends a QMI response, then frees the response. Remove decrements the refcount and shuts down the QMI handle only when the last auxiliary device goes away.

## State and Persistence Behavior

State is global and process-lifetime: `__qcom_pdm_data` points to the singleton QMI server and service list. Domain data itself is static read-only tables selected by SoC compatible. There is no persistent storage; responses reflect the baked-in table, not runtime remoteproc discovery. Refcounting allows multiple auxiliary devices to share one server.

## Dependencies and Integration Points

It depends on auxiliary bus, `of_machine_get_match()`, QRTR/QMI helpers, message descriptors from `qcom_pdr_msg.c` and `pdr_internal.h`, and Qualcomm common auxiliary device creation elsewhere. Remote clients discover the server via QMI service id `QMI_SERVICE_ID_SERVREG_LOC`, version `0x101`, instance 0.

## Risks and Edge Cases

The pagination condition uses `i < SERVREG_DOMAIN_LIST_LENGTH` rather than comparing `i - offset` against the response capacity, so nonzero offsets can prematurely return no entries or too few entries. `strscpy()` uses `sizeof(rsp->domain_list[i].name)` while writing index `j`; sizes are the same, but the index mismatch is fragile. `qcom_pdm_add_domain()` does not roll back earlier service registrations if a later service add fails. Unsupported machines return `-ENODEV`, forcing userspace to provide the service. Static tables can become stale as firmware service naming changes.

## Test Signals

Tests should cover machine match selection, duplicate service/domain rejection, multiple auxiliary probes/removes, domain-list requests for `tms/servreg`, audio/GPS/WLAN services, nonzero offsets, unknown service names, PFR requests, QRTR net reset behavior through `qmi_handle`, and memory-failure unwinding.
