# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_pdr_msg.c

## Purpose

`qcom_pdr_msg.c` is a descriptor-only module for Qualcomm SERVREG/PDR QMI messages. It exports `struct qmi_elem_info` arrays consumed by the generic QMI encoder/decoder and by protection-domain clients such as `qcom_pd_mapper.c`.

## Important APIs, Types, and Functions

The file exports descriptors for domain-list request/response, listener registration request/response, restart-PD request/response, service-state update indications, ACK request/response, and local PFR request/response. `servreg_location_entry_ei` is the nested descriptor for domain list entries. Most descriptors pair optional-valid flags with matching optional values and use `qmi_response_type_v01_ei` for common response status.

## Control Flow

There is no executable protocol control flow beyond module load. At runtime, callers pass these arrays to `qmi_encode_message()` or `qmi_decode_message()`. The descriptor order matters: optional flags must precede the data with the same TLV type, data length descriptors must precede variable-length arrays, and nested structures point to their own descriptor arrays.

## State and Persistence Behavior

All state is static const descriptor data exported to other modules. The file has no private mutable state and no hardware or file persistence. Persistent protocol behavior comes from keeping these descriptors ABI-compatible with remote SERVREG firmware.

## Dependencies and Integration Points

It depends on `<linux/soc/qcom/qmi.h>` for descriptor schema constants and on `pdr_internal.h` for message structure definitions, sizes, message ids, and enum types. Integration points are all QMI clients/servers handling protection-domain restart, service registry lookup, and PDR listener state.

## Risks and Edge Cases

Descriptor mistakes are runtime ABI bugs, not compile-time type errors. `servreg_loc_pfr_req_ei` marks strings as `VAR_LEN_ARRAY` without a preceding `QMI_DATA_LEN`, unlike many variable arrays; correctness depends on the QMI string handling path rather than normal array-length handling. Some enum fields use `sizeof(u32)` rather than the enum type while other descriptors use enum size. Fixed string limits must leave room for the decoder's NUL terminator.

## Test Signals

Round-trip tests should encode/decode every exported message type, including optional fields present and absent, max-length names/reasons, zero-length variable lists, maximum `SERVREG_DOMAIN_LIST_LENGTH` responses, and unknown optional TLVs. Integration tests should exercise the descriptors through `qcom_pd_mapper.c` QMI request handling.
