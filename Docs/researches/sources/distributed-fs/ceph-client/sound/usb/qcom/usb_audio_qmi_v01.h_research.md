# sources/distributed-fs/ceph-client/sound/usb/qcom/usb_audio_qmi_v01.h

Purpose: protocol declarations for the Qualcomm USB audio QMI stream service.

Important APIs, types, and data: defines service ID/version and request/response/indication message IDs. It declares memory descriptors (`mem_info_v01`, `apps_mem_info_v01`), USB descriptor mirror structs, stream status/device indication/speed enums, request/response/indication message structs, max encoded message lengths, and extern QMI element arrays.

Control flow: the offload driver receives `qmi_uaudio_stream_req_msg_v01`, validates requested format/channel/rate/buffer data, and fills `qmi_uaudio_stream_resp_msg_v01` with descriptors and xHCI memory data. Disconnect/suspend paths send `qmi_uaudio_stream_ind_msg_v01` events to the DSP.

State and persistence: message structs contain transient QMI payload state. The memory info fields carry both USB-host DMA addresses and backend/sysdev IOVA addresses, with valid flags determining which optional fields are encoded.

Dependencies and integration points: consumed by `qc_audio_offload.c` and `usb_audio_qmi_v01.c`, and must match the DSP-side QMI IDL. It depends on QMI core types such as `struct qmi_elem_info` and `struct qmi_response_type_v01`.

Risks: enum min/max sentinels force signed 32-bit enum encoding and must stay compatible with QMI. Max message length constants must be updated if fields change. The protocol exposes low-level USB descriptors and IOMMU mappings, so any layout mismatch can prevent DSP offload or corrupt resource handoff.

Test signals: compile-time struct offsets used by QMI arrays, interoperability with a DSP client, successful stream request/response round trips, and indication delivery for connect/disconnect/suspend/resume events.
