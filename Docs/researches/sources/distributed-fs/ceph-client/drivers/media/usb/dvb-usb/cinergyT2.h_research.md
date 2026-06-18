# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cinergyT2.h

Purpose: shared header for the TerraTec/qanu Cinergy T2 driver. It defines driver identity, debug macros, endpoint-1 firmware command IDs, packed control/status message formats, and the frontend attach prototype.

Important APIs, types, and definitions: `DRIVER_NAME` is the frontend/device display name. Debug macros define info, transfer, PLL, TS, error, RC, firmware, memory, and USB-transfer categories. `enum cinergyt2_ep1_cmd` defines command bytes for PID table reset/setup, stream transfer control, tuner parameters, tuner status, scan, remote events, sleep mode, and firmware version. `struct dvbt_get_status_msg` mirrors the packed firmware status response. `struct dvbt_set_parameters_msg` mirrors the packed firmware tune request. `cinergyt2_fe_attach()` is declared for the core file.

Control flow role: no executable code. The command IDs drive `cinergyT2-core.c` and `cinergyT2-fe.c` control messages. The packed structures define how those files overlay local byte buffers before calling `dvb_usb_generic_rw()` and how responses are interpreted.

State and persistence: no runtime state is stored here. The packed message structures describe transient USB control payloads and cached frontend status in `cinergyT2-fe.c`.

Dependencies and integration points: includes `<linux/usb/input.h>` and `dvb-usb.h`, binding the driver to Linux input definitions and the DVB USB framework. Both CinergyT2 C files include this header, so changes affect power/streaming, remote, and frontend tune/status paths.

Risks: packed structs must match the published device protocol exactly; field size or endian changes would break hardware communication. Some command IDs for PID and scan are defined but unused in the current C files. Debug categories are broader than current usage, which may suggest inherited or stale logging surface.

Test signals: compile both CinergyT2 translation units, verify structure sizes against expected firmware protocol lengths, inspect USB control payloads for tune/status/sleep/stream/remote commands, and run hardware tests for frontend attach, tuning, status reads, power, and streaming.
