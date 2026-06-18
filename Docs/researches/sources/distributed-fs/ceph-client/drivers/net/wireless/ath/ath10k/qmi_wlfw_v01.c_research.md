# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi_wlfw_v01.c

## Purpose

`qmi_wlfw_v01.c` is the static QMI TLV schema table set for the ath10k WLFW v01 service. Each exported `const struct qmi_elem_info ..._ei[]` array describes how the Linux QMI framework encodes or decodes one WLFW request, response, indication, or nested structure declared in `qmi_wlfw_v01.h`.

## Important APIs, Types, and Functions

- Nested arrays describe CE pipe config, service-to-pipe config, shadow registers, memory regions/segments, chip/board/SoC info, and firmware version info.
- Exported message arrays cover indication registration, FW/MSA ready indications, WLAN mode/config, capability, BDF download, calibration report/download/update, MSA info/ready, INI firmware logging, athdiag read/write, host capability, memory request/response, rejuvenation, dynamic feature masks, M3 info, and XO calibration.
- The 8-bit host capability encoder `wlfw_host_cap_8bit_req_msg_v01_ei` intentionally encodes only daemon support for older firmware quirks.

## Control Flow

There is no driver control flow here. The QMI framework walks each descriptor array until the terminating `{}` entry. Descriptors specify data type, element count/size, array kind, TLV type, struct offset, and nested element arrays. `qmi.c` passes these arrays to `qmi_txn_init()` and `qmi_send_request()` or registers them for indication decoding.

## State and Persistence Behavior

The file defines read-only global constant arrays. It performs no allocation, I/O, or mutation. Persistence concerns are ABI stability: TLV IDs, offsets, element sizes, signedness, and max lengths must match firmware.

## Dependencies and Integration Points

It includes Linux QMI types and `qmi_wlfw_v01.h`, and depends on QMI descriptor constants such as `QMI_UNSIGNED_*`, `QMI_SIGNED_4_BYTE_ENUM`, `QMI_STRING`, `QMI_STRUCT`, `QMI_OPT_FLAG`, `QMI_DATA_LEN`, `NO_ARRAY`, `STATIC_ARRAY`, and `VAR_LEN_ARRAY`. `qmi.c` is the primary in-driver consumer; firmware is the peer.

## Risks and Edge Cases

- Any mismatch between header struct layout and `offsetof()` descriptors corrupts QMI traffic.
- Some struct length fields are `u32` while the protocol length descriptor uses `u8` or `u16`; callers must clamp values before encoding.
- Empty arrays represent valid zero-length messages and must still be paired with correct message IDs and max lengths.
- Variable-length arrays require matching `QMI_DATA_LEN` descriptors for the same TLV.
- Using the 8-bit host-capability encoder with normal firmware would omit most capability fields.

## Test Signals

- Compile-time coverage should catch missing exported arrays referenced by `qmi.c`.
- Firmware boot tests should exercise indication registration, MSA info/ready, capability, BDF download, config, mode, and INI messages.
- Protocol tests should cover maximum BDF/calibration/athdiag payloads, maximum CE/service/shadow arrays, zero-length messages, and both host-capability encoders.
