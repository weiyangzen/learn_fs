# sources/distributed-fs/ceph-client/sound/usb/qcom/usb_audio_qmi_v01.c

Purpose: QMI encoder/decoder metadata for the Qualcomm USB audio stream service version 1.

Important APIs, types, and data: exports `qmi_uaudio_stream_req_msg_v01_ei`, `qmi_uaudio_stream_resp_msg_v01_ei`, and `qmi_uaudio_stream_ind_msg_v01_ei`. It also defines static element arrays for nested `mem_info_v01`, `apps_mem_info_v01`, `usb_endpoint_descriptor_v01`, and `usb_interface_descriptor_v01` structures.

Control flow: the QMI core uses these `struct qmi_elem_info` arrays to decode incoming stream requests, encode stream responses, and encode asynchronous device indications. Required fields use fixed TLV IDs; optional fields are represented by `QMI_OPT_FLAG` followed by a value using the same TLV type. Nested structures point at their own element arrays through `ei_array`.

State and persistence: no runtime state. The arrays are constant protocol metadata compiled into the module and shared by the QMI service in `qc_audio_offload.c`.

Dependencies and integration points: depends on `linux/soc/qcom/qmi.h` data types and the message/descriptor structures declared in `usb_audio_qmi_v01.h`. The max message length constants in the header must cover the encoded fields described here.

Risks: TLV type, offset, enum width, or optional-flag mismatches break ABI with the DSP QMI client. Because this file mirrors protocol layout manually, adding a field requires synchronized updates in the header structs, max length defines, and element arrays. Endianness is delegated to QMI data type encoders.

Test signals: QMI request decoding succeeds for valid DSP messages; response and indication encoding includes optional fields only when the matching `_valid` flag is set; ABI tests compare encoded TLV IDs and lengths against the DSP service specification.
