# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_flash.h

Purpose: defines IOSM flashing wire constants, EBL/FLS command IDs, capability bits, response offsets, packet sizes, erase timing, and C structs used by `iosm_ipc_flash.c`.

Important APIs/types: `enum iosm_flash_package_type`, `iosm_out_of_session_action`, `iosm_out_of_session_type`, `iosm_ebl_caps`, `iosm_ebl_rsp`, `iosm_mdm_send_recv_data`, `iosm_ebl_error`, `iosm_swid_table`, `iosm_flash_msg_control`, and `iosm_flash_data`. It exports boot and flash entry points for PSI, EBL, capabilities, link establishment, SWID read, and FLS send.

Control flow role: this header is the protocol schema for flash.c. Packet sizes choose write-vs-data-write EBL frame lengths; response offsets select capability fields; erase timeout/interval drive polling. State is not persistent in the header, but constants define persistent modem flash effects such as full NAND erase.

Dependencies: requires `struct iosm_devlink`, `struct iosm_imem`, and `struct firmware` from the including translation units. Risks center on ABI drift with modem firmware: incorrect offsets like `EBL_OOS_CONFIG`, maximum payload sizes, or checksum field order can brick an update path. Test signals include compile-time inclusion in flash/devlink code, command encoding fixtures, bounds checks against `IOSM_EBL_HEAD_SIZE`, and mocked response buffers at every enum offset.
