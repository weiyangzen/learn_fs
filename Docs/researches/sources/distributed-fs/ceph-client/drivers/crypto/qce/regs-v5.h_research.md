<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/regs-v5.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/regs-v5.h

Purpose: provides the QCE v5 register offsets, bit shifts, masks, and enum values consumed by shared register setup.

Important definitions: offsets cover version/status, segment sizes, GO, encryption segment config, counters/IVs, XTS, authentication segment config, auth IV/nonce/bytecount/expected MAC, global config, encryption keys, XTS keys, and authentication keys. Bit definitions describe version fields, status errors/MAC failure/operation done, config burst/pipe/endian/interrupt masks, auth modes/sizes/key sizes/positions/nonce words, encryption algorithms/modes/key sizes/encode, GO/result dump, and engine availability.

Control flow and integration: `common.c` uses these constants to compose `REG_CONFIG`, `REG_AUTH_SEG_CFG`, `REG_ENCR_SEG_CFG`, and `REG_GOPROC` writes for SHA, skcipher, and AEAD flows.

State and persistence: no runtime state; this is a hardware ABI map. Wrong values persist only as bad MMIO programming during requests.

Dependencies: Linux bitops and QCE v5-compatible hardware.

Risks and test signals: these values are the root of register programming correctness. Test across `qcom,crypto-v5.1` and `v5.4`, especially CCM, XTS, status error decoding, MAC failure, burst/pipe selection, and little-endian result-dump mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/regs-v5.h -->
