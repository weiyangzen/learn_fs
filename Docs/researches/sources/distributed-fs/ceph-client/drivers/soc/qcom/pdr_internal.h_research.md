<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pdr_internal.h -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/pdr_internal.h

Purpose: defines the internal SERVREG QMI message ABI used by `pdr_interface.c`. It is not a standalone implementation file; it supplies message ids, maximum encoded lengths, request/response structures, indication structures, and external QMI element-info declarations.

Important APIs/types/functions: constants cover SERVREG operations for register listener, get domain list, state update indication, set ACK, restart PD, and local PFR. Structures include `servreg_location_entry`, `servreg_get_domain_list_req`, `servreg_get_domain_list_resp`, `servreg_register_listener_req`, `servreg_register_listener_resp`, `servreg_restart_pd_req`, `servreg_restart_pd_resp`, `servreg_state_updated_ind`, `servreg_set_ack_req`, `servreg_set_ack_resp`, `servreg_loc_pfr_req`, and `servreg_loc_pfr_resp`. The header declares QMI element-info arrays such as `servreg_get_domain_list_req_ei[]` and `servreg_state_updated_ind_ei[]`.

Control flow: there is no runtime flow in the header. The structures define the payloads for the PDR flow: locator domain-list requests/responses, notifier listener registration, async state indications, indication ACK requests, and restart requests.

State and persistence: the structures carry transient QMI state only: service names/paths, domain offsets, domain records, current state, transaction ids, service-data fields, and QMI response codes. There is no local persistence.

Dependencies and integration: includes public PDR definitions from `<linux/soc/qcom/pdr.h>` for `SERVREG_NAME_LENGTH`, `SERVREG_PFR_LENGTH`, and service state types. It also assumes QMI core types such as `struct qmi_response_type_v01` and `struct qmi_elem_info` are available through that include chain. Element-info definitions are expected elsewhere in the same driver build.

Risks and test signals: the risk is ABI mismatch: wrong max lengths, field widths, enum encoding, or string sizes will make QMI transactions fail or silently decode wrong service paths/states. Test signals are successful domain-list pagination, listener registration response decoding, state indication decoding with transaction id, ACK request encoding, and restart response error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pdr_internal.h -->
