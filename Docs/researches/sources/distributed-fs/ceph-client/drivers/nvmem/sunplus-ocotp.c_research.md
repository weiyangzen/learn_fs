# sources/distributed-fs/ceph-client/drivers/nvmem/sunplus-ocotp.c

Purpose: Sunplus SP7021 OCOTP read-only NVMEM provider.

Important APIs/types/functions: `struct sp_ocotp_priv` stores two MMIO bases (`hb_gpio`, `otprx`) and a clock. `sp_otp_read_real()` converts byte address to bank/word/byte selection, triggers OTP read, polls `OTP_READ_DONE`, and extracts one byte from HB GPIO data. `sp_ocotp_read()` enables the clock and reads bytes one at a time.

Control flow: probe maps named resources, gets and prepares the clock, fills static NVMEM config, registers, and leaves the clock prepared. Runtime reads enable the clock, loop byte offsets through the low-level read sequence, disable the clock, and return first error.

State/persistence: OTP data is persistent and read-only. State is MMIO base array and clock.

Dependencies/integration: OF compatible `sunplus,sp7021-ocotp`; depends on named resources, clock framework, MMIO polling, and legacy fixed cells.

Risks: per-byte read is slow but simple. The prepared clock is only unprepared on probe failure, not via a remove/devm action in the successful path. Static `sp_ocotp_nvmem_config.size` is fixed to QAC628 size and does not use match data dynamically.

Test signals: named-resource failures, clock prepare/enable failures, read timeout, byte extraction across word/bank boundaries, and fixed-cell reads over multiple bytes.
