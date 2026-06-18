# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_comp.h

## Purpose
`icp_qat_fw_comp.h` defines the firmware ABI for QAT compression/decompression requests and responses, including deflate, LZ4/LZ4S, and zstd command IDs, session/request flags, content descriptor headers, state layouts, CRC data, and response counters.

## Important APIs, Types, And Functions
Key enums are `icp_qat_fw_comp_cmd_id`, `icp_qat_fw_comp_20_cmd_id`, and `icp_qat_fw_comp_bank_enabled`. Important structures include `icp_qat_fw_comp_req_params`, `icp_qat_fw_xlt_req_params`, `icp_qat_fw_comp_cd_hdr`, `icp_qat_fw_xlt_cd_hdr`, `icp_qat_fw_comp_req`, `icp_qat_fw_resp_comp_pars`, `icp_qat_fw_comp_state`, `icp_qat_fw_comp_resp`, `icp_qat_fw_comp_crc_data_struct`, and `xxhash_acc_state_buff`. Macros build and extract session flags, SOP/EOP/BFINAL/CNV/CRC/xxhash/append/drop/partial-decompress request flags, CNV error types, and RAM bank flags.

## Control Flow
The header itself has no control flow. `qat_comp_req.h` and compression context builders copy request templates, fill `comn_mid`, set `comp_len` and output buffer size, and read response counters/status/error codes through this ABI. Firmware consumes request flags to determine compression direction, stream framing, checksum behavior, and optional translator/intermediate buffer usage.

## State And Persistence Behavior
The structures describe per-request message state and optional stateful compression context state. In this driver subset, `qat_comp_algs.c` uses stateless requests but still relies on template context built elsewhere. Response counters persist only until the async completion callback updates `acomp_req->dlen`.

## Dependencies And Integration Points
The file includes `icp_qat_fw.h` and is used by `qat_comp_req.h`, `qat_comp_algs.c`, and device-specific compression context builders. It integrates with the Linux async compression API through the produced/consumed counters and firmware error/status fields.

## Risks
Flag bitfields are dense and version-sensitive. A wrong SOP/EOP/BFINAL/CNV setting can produce invalid streams or disable verified compression. Output overflow is reported through firmware status/errors and must map correctly to `-E2BIG`. End-to-end CRC and xxhash fields require consistent DMA-visible state if enabled.

## Test Signals
Deflate, LZ4S-zstd, and native zstd compression/decompression tests should validate status, produced counters, overflow behavior, CNV flags, and checksum modes. Hardware firmware traces or debug logs should show expected command IDs and request parameter flags.
