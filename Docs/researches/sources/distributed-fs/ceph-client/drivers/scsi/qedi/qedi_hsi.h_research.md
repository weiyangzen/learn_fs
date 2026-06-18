# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_hsi.h

Purpose: this header is qedi's local hardware software interface shim for common QED iSCSI structures. It includes shared QED HSI headers and defines the iSCSI command queue element shape used by the driver/firmware interface.

Important definitions: it includes `common_hsi.h`, `storage_common.h`, `tcp_common.h`, and `iscsi_common.h`. `struct iscsi_cmdqe` contains a connection ID, invalid-command marker, command header type, reserved words, and 13 dwords of command payload. `enum iscsi_cmd_hdr_type` distinguishes BHS-only, BHS-with-AHS, and AHS command header forms.

Control flow and state: there is no runtime control flow. The struct and enum describe firmware command queue layout consumed by lower-level QED iSCSI code and qedi task/SQE setup.

Dependencies and integration points: this header deliberately defines `__QEDI_HSI__` and relies on shared QED HSI contracts. `qedi.h`, `qedi_fw_scsi.h`, and `qedi_fw_api.c` include it so firmware context and PDU definitions are available.

Risks: HSI layout is firmware ABI. Padding, endian handling, field widths, and enum values must match the firmware and common QED headers. Any local change here can break command submission compatibility.

Test signals: build compatibility with QED HSI headers, firmware command submission smoke tests, structure size/layout checks when available, and hardware validation for BHS-only, BHS-with-AHS, and AHS cases.
