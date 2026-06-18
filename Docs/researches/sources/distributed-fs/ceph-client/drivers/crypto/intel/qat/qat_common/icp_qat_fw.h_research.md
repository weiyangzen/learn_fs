# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw.h

## Purpose
`icp_qat_fw.h` defines common QAT firmware request/response ABI structures and bitfield helpers shared by symmetric crypto, compression, PKE, DMA, and admin services.

## Important APIs, Types, And Functions
Important types include `struct icp_qat_fw_comn_req_hdr`, `icp_qat_fw_comn_req_hdr_cd_pars`, `icp_qat_fw_comn_req_mid`, `icp_qat_fw_comn_req_cd_ctrl`, `icp_qat_fw_comn_req`, `icp_qat_fw_comn_resp_hdr`, and `icp_qat_fw_comn_resp`. Enums define common service/request IDs and slice IDs. Macros include `QAT_FIELD_SET()`, `QAT_FIELD_GET()`, common header valid/CNV/CNVNR flags, pointer/content descriptor flag builders, current/next slice ID accessors, and response status builders/getters.

## Control Flow
The header is declarative. Runtime code fills a request header, content descriptor parameters, mid fields with source/destination/opaque data, service-specific request parameters, and content descriptor controls. Firmware returns a common response header plus opaque data, which service callbacks use to recover request context and decode status/error bits.

## State And Persistence Behavior
No state is owned here. The structures are transient firmware messages in ring DMA memory or per-request software buffers. The layout is effectively persistent ABI between driver and firmware versions.

## Dependencies And Integration Points
It includes `icp_qat_hw.h` for hardware enums and is included by service-specific firmware headers (`icp_qat_fw_la.h`, `icp_qat_fw_comp.h`, `icp_qat_fw_pke.h`, admin headers) and request-building code. The common opaque pointer field is central to async completion routing.

## Risks
Structure packing, field sizes, and bit positions must match firmware exactly. `QAT_FIELD_SET()` is a statement macro that mutates its first argument and can surprise callers if used with expressions. Status bits use inverted meanings in some contexts (`OK` is zero), so callbacks must use the correct service-specific getter. ABI drift can silently corrupt hardware requests.

## Test Signals
Compile-time ABI checks are limited, so runtime firmware selftests, request completions across all services, and decoded firmware errors are primary signals. Tests should cover SGL versus flat pointer flags and all common response status paths.
