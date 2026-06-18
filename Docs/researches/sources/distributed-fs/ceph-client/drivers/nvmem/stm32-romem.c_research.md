# sources/distributed-fs/ceph-client/drivers/nvmem/stm32-romem.c

Purpose: STMicroelectronics STM32 ROMEM/BSEC NVMEM provider for factory-programmed memory and OTPs, supporting plain MMIO, legacy SMC, and OP-TEE PTA access.

Important APIs/types/functions: `struct stm32_romem_cfg` defines size, lower OTP count, and whether TA is required. `stm32_romem_read()` handles simple byte MMIO OTP. `stm32_bsec_read()` reads lower OTPs from shadow MMIO and upper OTPs through SMC. `stm32_bsec_write()` programs OTPs through SMC. `stm32_bsec_pta_read()`/`write()` delegate to OP-TEE helper. Probe selects access mode based on compatible data and OP-TEE/SMC availability.

Control flow: probe maps the resource, fills common NVMEM config, then either exposes simple read-only ROMEM for non-BSEC compatibles or BSEC read/write access. For BSEC, it attempts OP-TEE when required or present; if TA is unavailable and not required, it checks legacy SMC support and falls back to SMC callbacks. Registered NVMEM is byte-granular and OTP typed.

State/persistence: OTP writes are permanent. Lower BSEC words are bitwise/incrementally programmable, while upper words are ECC-protected and word-program-only. Driver state includes MMIO base, lower boundary, NVMEM config, and optional TEE context cleaned by devm.

Dependencies/integration: compatibles `st,stm32f4-otp`, `st,stm32mp15-bsec`, `st,stm32mp13-bsec`, and `st,stm32mp25-bsec`; depends on ARM SMCCC when using SMC, OP-TEE helper when available/required, OF OP-TEE presence detection, and legacy fixed cells.

Risks: write access is exposed for BSEC variants and can permanently program OTPs; the driver warns on upper OTP updates but does not prevent them. TA-required variants fail probe without OP-TEE. SMC support is compile-time gated by `CONFIG_HAVE_ARM_SMCCC`.

Test signals: simple STM32F4 MMIO reads, MP15 OP-TEE fallback to SMC, MP13/MP25 TA-required failure without TA, unaligned reads through SMC/TA, write alignment rejection, upper OTP warning/lock behavior through TA, and devm TEE context cleanup.
