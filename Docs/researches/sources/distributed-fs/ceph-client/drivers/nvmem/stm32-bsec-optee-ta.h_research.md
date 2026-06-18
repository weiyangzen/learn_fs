# sources/distributed-fs/ceph-client/drivers/nvmem/stm32-bsec-optee-ta.h

Purpose: Conditional interface header for STM32 BSEC OP-TEE helper functions.

Important APIs/types/functions: declares `stm32_bsec_optee_ta_open()`, `stm32_bsec_optee_ta_close()`, `stm32_bsec_optee_ta_read()`, and `stm32_bsec_optee_ta_write()` when `CONFIG_NVMEM_STM32_BSEC_OPTEE_TA` is enabled; otherwise provides inline stubs returning `-EOPNOTSUPP`.

Control flow: no runtime flow in the header, but it determines whether `stm32-romem.c` can attempt TA-backed access or must fall back/fail.

State/persistence: no state. The API passes a `struct tee_context *` opaque context opened by the helper and owned by the caller for devm cleanup.

Dependencies/integration: included by both the TA implementation and STM32 ROMEM driver; relies on `struct tee_context` being visible via included headers in users.

Risks: stub behavior makes missing TA support look like a runtime unsupported operation, so probe logic must distinguish optional versus required TA variants. Documentation comments contain minor `nvem` typos only.

Test signals: build coverage with the config enabled and disabled, ROMEM fallback behavior when stubs return `-EOPNOTSUPP`, and correct devm close callback typing.
