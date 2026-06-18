# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi_wlfw_v01.h

## Purpose

`qmi_wlfw_v01.h` declares the WLFW v01 QMI protocol used by ath10k WCN3990/SNOC firmware. It contains service identifiers, message IDs, maximum message sizes, protocol limits, enums, bit masks, message structures, and extern declarations for the encoder/decoder arrays implemented in `qmi_wlfw_v01.c`.

## Important APIs, Types, and Functions

- `WLFW_SERVICE_ID_V01` and `WLFW_SERVICE_VERS_V01` identify the QRTR/QMI service.
- `QMI_WLFW_*` constants define request, response, and indication message IDs.
- Protocol limits cap data payloads, athdiag payloads, CE/service/shadow arrays, memory regions/segments, strings, build IDs, timestamps, and MAC address size.
- `enum wlfw_driver_mode_enum_v01` defines mission, FTM, epping, WAL test, off, CCPM, QVIT, and calibration modes.
- `enum wlfw_cal_temp_id_enum_v01`, `enum wlfw_pipedir_enum_v01`, and `enum wlfw_mem_type_enum_v01` define calibration slots, CE directions, and memory types.
- Structures cover WLAN config/mode, capabilities, BDF/calibration transfer, MSA memory, firmware log INI, athdiag, host capability, memory request/response, rejuvenation, dynamic feature mask, M3 info, MAC address, voltage, and XO calibration.
- Each message has a `WLFW_*_MAX_MSG_LEN` and extern `wlfw_*_ei[]` schema declaration.

## Control Flow and Integration

This header does not execute code. `qmi.c` fills these structs and passes the matching `qmi_elem_info` arrays to QMI transaction APIs; the QMI framework uses field offsets to serialize/deserialize TLVs. A normal boot path registers indications, sends host/MSA information, requests capabilities, downloads board/calibration data, sends WLAN config, and switches WLAN mode.

## State and Persistence Behavior

The header defines no storage. Its structs are transient QMI messages, while decoded values persist in `struct ath10k_qmi` and firmware state. The declared ABI is persistent across host/firmware communication.

## Dependencies and Integration Points

It is included by `qmi.h`, `qmi.c`, and `qmi_wlfw_v01.c`. It relies on Linux QMI response and element-info types through users. Firmware and the Linux QMI framework are the main external integration points.

## Risks and Edge Cases

- Field reordering, type changes, max-length changes, or message ID changes can break firmware compatibility.
- Optional payloads require valid flags or the encoder omits them.
- 6144-byte BDF/calibration/athdiag caps require caller-side segmentation.
- Zero-length messages use placeholder structs but empty elem arrays and max length zero.
- The host-capability quirk has two encoders for one C struct, so caller selection must match firmware.

## Test Signals

- Compile QMI/SNOC builds to ensure every extern schema array is implemented.
- Boot/recovery logs should confirm expected WLFW message IDs succeed.
- Boundary tests should cover max payload sizes, max CE/service/shadow counts, max memory segments, and absent optional fields.
- Schema checks should compare this header and `qmi_wlfw_v01.c` against the WLFW firmware IDL.
