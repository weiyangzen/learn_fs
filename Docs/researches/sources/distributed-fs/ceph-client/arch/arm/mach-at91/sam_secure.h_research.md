# sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam_secure.h

Purpose: declares the secure PM interface shared by AT91 platform code.

Important APIs/types/functions: defines SIP function IDs `SAMA5_SMC_SIP_SET_SUSPEND_MODE` and `SAMA5_SMC_SIP_GET_SUSPEND_MODE`; declares `sam_secure_init()`, `sam_smccc_call()`, and `sam_linux_is_optee_available()`.

Control flow: callers initialize secure availability at machine init and call into secure firmware during PM setup.

State and persistence: header only; state is in `sam_secure.c`.

Dependencies and integration: includes Linux types and SMCCC result types through users. It is consumed by SAMA5 machine and PM code.

Risks: function ID changes must stay synchronized with firmware. Missing declarations would force duplicate SMCCC encodings.

Test signals: compile coverage under `CONFIG_ATMEL_SECURE_PM` and secure suspend negotiation on OP-TEE systems.
