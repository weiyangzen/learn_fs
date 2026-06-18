# sources/distributed-fs/ceph-client/drivers/soc/qcom/qmi_encdec.c

## Purpose

`qmi_encdec.c` is the generic Qualcomm QMI TLV encoder/decoder. It translates C structures described by `struct qmi_elem_info` arrays to and from QMI wire messages with `struct qmi_header`, endian conversion, nested structures, strings, optional TLVs, static arrays, and variable-length arrays.

## Important APIs, Types, and Functions

Exported APIs are `qmi_encode_message()`, `qmi_decode_message()`, and `qmi_response_type_v01_ei`. Internal helpers include `qmi_calc_min_msg_len()`, `qmi_encode_basic_elem()`, `qmi_encode_struct_elem()`, `qmi_encode_string_elem()`, `qmi_encode()`, `qmi_decode_basic_elem()`, `qmi_decode_struct_elem()`, `qmi_decode_string_elem()`, `find_ei()`, and `qmi_decode()`. Macro helpers encode/decode TLV headers and little-endian integer widths.

## Control Flow

Encoding starts at `qmi_encode_message()`, optionally validates NULL payloads against minimum message length, allocates header plus caller-provided max length, recursively encodes top-level TLVs, fills header type/txn/message id/message length, and updates `*len`. Top-level fields reserve TLV header space before payload; nested fields omit TLV headers. Optional flags determine whether all fields with the same TLV type are skipped. Decoding verifies inputs, then walks TLVs until the payload is consumed; required unknown TLVs fail, unknown optional TLVs are skipped, known TLVs are decoded into C offsets.

## State and Persistence Behavior

The module has no mutable state. Allocation state is limited to encoded message buffers returned to callers, who must free them. Decoding writes into caller-provided output structures. Protocol persistence depends entirely on descriptor stability and QMI peers.

## Dependencies and Integration Points

It depends on Linux allocation, endian helpers, string handling, kernel logging, and `<linux/soc/qcom/qmi.h>`. It is the codec backend for `qmi_interface.c`, `qcom_pdr_msg.c`, `qcom_pd_mapper.c`, and other Qualcomm QMI clients.

## Risks and Edge Cases

Several pointer operations are on `void *`, relying on compiler extensions used by the kernel. `qmi_decode_message()` does not check `len >= sizeof(struct qmi_header)` before subtracting, so too-short messages can underflow size. `qmi_encode_string_elem()` uses `strlen()` on source buffers, requiring C-string termination even for fixed QMI string fields. `qmi_decode_string_elem()` rejects `string_len >= elem_len`, so max-capacity strings require descriptors to include terminator space. Descriptor errors around optional flags or `QMI_DATA_LEN` can desynchronize subsequent fields.

## Test Signals

Round-trip tests should cover all integer widths, signed enums, nested structs, static arrays, variable arrays with 8-bit and 16-bit lengths, optional fields omitted and present, strings at boundary lengths, unknown optional TLVs, unknown required TLVs, zero-length messages, too-short headers, undersized output buffers, and malformed data lengths larger than descriptor limits.
