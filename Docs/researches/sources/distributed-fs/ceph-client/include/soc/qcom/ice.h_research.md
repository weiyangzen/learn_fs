# sources/distributed-fs/ceph-client/include/soc/qcom/ice.h

Purpose: declares the Qualcomm Inline Crypto Engine API used by storage drivers to enable ICE, manage suspend/resume, program and evict crypto keys, and handle wrapped-key operations.

Important APIs/types/functions: forward-declares `struct qcom_ice` and exports `qcom_ice_enable`, `qcom_ice_resume`, `qcom_ice_suspend`, `qcom_ice_program_key`, `qcom_ice_evict_key`, `qcom_ice_get_supported_key_type`, `qcom_ice_derive_sw_secret`, `qcom_ice_generate_key`, `qcom_ice_prepare_key`, `qcom_ice_import_key`, and `devm_of_qcom_ice_get`.

Control flow: storage drivers acquire an ICE instance from device tree, enable or resume it, ask what key type is supported, program key slots for blk-crypto, evict slots when no longer needed, and use wrapped-key helpers for generate/import/prepare/derive flows.

State and persistence: state is held by the ICE driver and hardware key slots. Key material and wrapped-key buffers are security-sensitive and must be invalidated or evicted by callers.

Dependencies and integration: depends on `linux/blk-crypto.h` and `linux/types.h`. Consumers include `sdhci-msm` and `ufs-qcom`; implementation is in `drivers/soc/qcom/ice.c`.

Risks: slot mismatch, suspend/resume ordering, unsupported key type handling, or incorrect buffer sizes can break storage encryption or expose key material. Test signals include blk-crypto self-tests, UFS/eMMC encrypted IO, suspend/resume cycles, wrapped-key flows, and key eviction error handling.
