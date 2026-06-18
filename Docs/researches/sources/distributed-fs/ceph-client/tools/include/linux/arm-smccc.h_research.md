# sources/distributed-fs/ceph-client/tools/include/linux/arm-smccc.h

## Purpose

This header provides ARM SMC Calling Convention constants and helpers for tools code that needs to encode or decode SMCCC function IDs.

## APIs, State, and Dependencies

It defines call type, 32/64-bit convention, owner, and function masks and shifts, plus helpers `ARM_SMCCC_IS_FAST_CALL`, `ARM_SMCCC_IS_64`, `ARM_SMCCC_FUNC_NUM`, `ARM_SMCCC_OWNER_NUM`, and `ARM_SMCCC_CALL_VAL`. It enumerates owner IDs, version IDs, architecture feature/workaround function IDs, KVM vendor hypervisor UID and function IDs, paravirtual time calls, TRNG calls, and return codes. It depends on `<linux/const.h>` and has no runtime state.

## Risks and Test Signals

These constants are ABI definitions. Wrong owner or function encodings can make hypercalls fail or call the wrong service. Tests should compare generated call values against ARM SMCCC specifications and kernel UAPI expectations, especially KVM PTP and workaround IDs.
