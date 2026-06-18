<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci_cmd.h

Purpose: private DPSECI command ABI header containing command version constants, encoded command IDs, field access macros, and packed command/response parameter structures used by `dpseci.c`.

Important APIs and control flow: defines DPSECI API version 5.3, command base versions, `DPSECI_CMD_V1/V2()`, command IDs for open/close, API version, enable/disable/reset, queue get/set, SEC attributes, and congestion notification. `dpseci_set_field()` and `dpseci_get_field()` update sub-byte fields using generated masks. Structures describe command payloads such as `dpseci_cmd_open`, `dpseci_cmd_queue`, `dpseci_rsp_get_tx_queue`, `dpseci_rsp_get_sec_attr`, `dpseci_rsp_get_api_version`, and `dpseci_cmd_congestion_notification`.

State and persistence behavior: none; it is compile-time wire-format definition.

Dependencies and integration points: consumed only by the DPSECI command wrapper and must match `linux/fsl/mc.h` command parameter storage and MC firmware layout.

Risks and test signals: risks include ABI breakage if structure padding differs from firmware expectations, field macros OR-ing into uncleared variables, and command version mismatch for `GET_SEC_ATTR`. Test signals are MC command success for every wrapper, sparse/endian-clean builds, and round-trip queue/congestion fields preserving sub-byte values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci_cmd.h -->
