# sources/distributed-fs/ceph-client/drivers/nvmem/stm32-bsec-optee-ta.c

Purpose: OP-TEE client helper for STM32MP BSEC OTP access, used by the STM32 ROMEM NVMEM driver.

Important APIs/types/functions: `stm32_bsec_optee_ta_open()` opens a TEE context and verifies the BSEC TA UUID. `stm32_bsec_optee_ta_read()` invokes `PTA_BSEC_READ_MEM` with aligned shared memory output. `stm32_bsec_optee_ta_write()` invokes `PTA_BSEC_WRITE_MEM` for fuse programming and then lock programming for upper ECC-protected OTPs. Session helpers open/close TA sessions per operation.

Control flow: open checks for OP-TEE GP capability, opens a session to prove TA presence, closes it, and returns the context. Reads open a session, align requested offset/length to 32-bit boundaries, allocate kernel shared memory, invoke the TA, copy requested bytes from the aligned buffer, free shared memory, and close the session. Writes open a session, require 32-bit aligned full words, allocate/copy shared memory, invoke fuse write, optionally rewrite the shared buffer with `LOCK_PERM` words and invoke lock access for upper OTPs, then free and close.

State/persistence: no data cache. The TEE context is retained by the caller; OTP writes and locks are permanent in BSEC hardware.

Dependencies/integration: depends on TEE client API, OP-TEE GP implementation, UUID `94cf71ad-80e6-40b5-a7c6-3dc501eb2803`, and constants shared with `stm32-romem.c`.

Risks: `stm32_bsec_optee_ta_write()` opens a TEE session before validating alignment; the early `return -EINVAL` can leak the session. TA return codes are collapsed to `-EIO` when the kernel invocation itself succeeded but TA returned an error. Writes are permanent and upper OTPs are locked after successful programming.

Test signals: OP-TEE absent causing `-EPROBE_DEFER`, TA session open failure, unaligned read alignment/copy behavior, write alignment rejection with session cleanup, TA access-denied mapping, and upper-lock invocation boundary at `lower * 4`.
