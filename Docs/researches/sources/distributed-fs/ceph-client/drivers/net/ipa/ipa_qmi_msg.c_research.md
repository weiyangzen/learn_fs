# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi_msg.c

Purpose: provides QMI element-info descriptors that serialize and deserialize IPA QMI request, response, indication, and nested memory structures.

Important APIs/data: exported descriptor arrays include `ipa_indication_register_req_ei`, response descriptors for indication/register and driver-init-complete, `ipa_init_complete_ind_ei`, nested `ipa_mem_bounds_ei`, `ipa_mem_array_ei`, `ipa_mem_range_ei`, and full `ipa_init_modem_driver_req_ei`/`rsp_ei`.

Control flow: the QMI framework uses these arrays in `qmi_send_request()`, `qmi_send_response()`, `qmi_send_indication()`, and handler registration to map TLV type IDs to C structure offsets. Optional fields are represented by `QMI_OPT_FLAG` immediately followed by the value/struct with the same TLV type.

State/persistence: no mutable state; the arrays are constant protocol metadata. They must remain synchronized with `struct ipa_*` definitions and max message sizes in `ipa_qmi_msg.h`.

Dependencies/integration: depends on `linux/soc/qcom/qmi.h`, `offsetof`, `sizeof_field`, and the message structures in `ipa_qmi_msg.h`. Used exclusively by `ipa_qmi.c` and QMI core.

Risks: TLV IDs, field sizes, signed/unsigned enum types, or offsets that drift from the modem protocol will silently produce incompatible wire messages. Optional valid flags must match their value field TLV. Max receive/send sizes must cover encoded descriptors.

Test signals: QMI init-driver messages decode on the modem side, AP correctly decodes responses, QMI tracing shows expected TLV IDs, and protocol fuzz/compat tests do not report malformed element arrays.
