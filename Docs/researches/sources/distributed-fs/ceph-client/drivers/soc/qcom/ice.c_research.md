# sources/distributed-fs/ceph-client/drivers/soc/qcom/ice.c

## Purpose
Qualcomm Inline Crypto Engine support for storage inline encryption. It discovers ICE hardware, chooses raw-key versus hardware-wrapped-key mode, initializes low-power/optimization/HWKM registers, and exports key programming and wrapped-key lifecycle helpers to storage drivers.

## Important APIs, Types, And Functions
Exports `qcom_ice_enable()`, `qcom_ice_resume()`, `qcom_ice_suspend()`, `qcom_ice_program_key()`, `qcom_ice_evict_key()`, `qcom_ice_get_supported_key_type()`, `qcom_ice_derive_sw_secret()`, `qcom_ice_generate_key()`, `qcom_ice_prepare_key()`, `qcom_ice_import_key()`, and `devm_of_qcom_ice_get()`. Main private type is `struct qcom_ice` with device, base, core clock, HWKM flags, and HWKM version. Important internals are `qcom_ice_check_supported()`, `qcom_ice_hwkm_init()`, `qcom_ice_wait_bist_status()`, `qcom_ice_program_wrapped_key()`, `qcom_ice_create()`, and `of_qcom_ice_get()`.

## Control Flow
`qcom_ice_create()` waits for SCM availability, checks SCM ICE support, obtains one of the legacy or node-local clocks, reads hardware version and fuse state, determines HWKM version, and chooses HWKM only if the module parameter `qcom_ice.use_wrapped_keys=1` and SCM wrapped-key support are present.

Consumers call `devm_of_qcom_ice_get()`. For legacy bindings, it maps an `ice` resource from the consumer device and creates an instance. For modern bindings, it follows the `qcom,ice` phandle, gets the provider platform device, reads its drvdata, and creates a device link. Provider probe maps resource 0 and stores a created ICE instance.

`qcom_ice_enable()` enables low-power and optimization sequences, initializes HWKM if selected, then waits for BIST completion. Resume reenables the clock and repeats HWKM/BIST setup; suspend disables the clock and marks HWKM init incomplete. Key programming accepts only AES-256-XTS. Wrapped keys are programmed through SCM into translated HWKM slots and then enable `CRYPTOCFG`; raw keys are endian-converted and sent through `qcom_scm_ice_set_key()`, then zeroed.

## State And Persistence
State includes the mapped ICE registers, enabled clock, module parameter policy, HWKM mode/version, and `hwkm_init_complete`. Key material is passed to SCM and keyslots; raw key stack copies are wiped with `memzero_explicit()`. No filesystem persistence.

## Dependencies And Integration Points
Depends on Qualcomm SCM firmware APIs, blk-crypto key types and sizes, platform/OF resource lookup, clocks, device links, MMIO, and storage consumers such as UFS/eMMC drivers. The Makefile builds it as `qcom_ice`.

## Risks
Mode selection is global/module-parameter driven and must happen before storage drivers advertise crypto capabilities. HWKM and legacy raw-key mode are mutually exclusive. If HWKM self-test fails after capabilities were exposed, the driver can only log the error. TrustZone/SCM errors directly affect key programming. Slot translation differs between HWKM v1 and v2. Legacy consumer-created instances and provider-node instances have different put semantics.

## Test Signals
Expected logs identify ICE version and HWKM version/mode. Probe should defer until SCM is available. Storage drivers should advertise raw or wrapped key support consistently with `qcom_ice_get_supported_key_type()`. Key generation/prepare/import/program/evict paths should succeed with valid SCM firmware and reject wrong modes, wrong sizes, and invalid wrapped keys with appropriate errors.
