# sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam_secure.c

Purpose: wraps AT91 secure monitor calls used by secure power-management firmware.

Important APIs/types/functions: global `optee_available`; macro `SAM_SIP_SMC_STD_CALL_VAL()`; functions `sam_smccc_call()`, `sam_linux_is_optee_available()`, and `sam_secure_init()`.

Control flow: `sam_secure_init()` locates an `optee` node with method `smc` and records availability. `sam_smccc_call()` encodes the SIP function number, invokes `arm_smccc_smc()`, and returns the result structure to PM code.

State and persistence: only the boot-time `optee_available` boolean persists.

Dependencies and integration: depends on ARM SMCCC, OF lookup, and `sam_secure.h` function IDs. `pm.c` uses it when `CONFIG_ATMEL_SECURE_PM` is enabled.

Risks: firmware ABI mismatches or absent OP-TEE nodes can disable secure PM or return unsupported modes. The wrapper does not validate function arguments beyond encoding the call number.

Test signals: boot with and without OP-TEE, secure suspend-mode negotiation, and checking firmware return values during SAMA5 secure PM.
