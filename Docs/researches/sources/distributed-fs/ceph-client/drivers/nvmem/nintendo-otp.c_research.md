# sources/distributed-fs/ceph-client/drivers/nvmem/nintendo-otp.c

Purpose: Read-only, root-only NVMEM provider for Nintendo Wii and Wii U OTP banks.

Important APIs/types/functions: `struct nintendo_otp_devtype_data` supplies NVMEM name and bank count for Hollywood and Latte devices. `nintendo_otp_reg_read()` issues big-endian OTP read commands and reads big-endian data words.

Control flow: probe matches compatible data, maps the register window, fills a 4-byte stride read-only/root-only NVMEM config sized by bank count, and registers it. Reads compute bank/address from the byte offset, write `OTP_READ | bank | addr` to `HW_OTPCMD`, then read `HW_OTPDATA`.

State/persistence: OTP contents are per-console keys/signatures and persist in hardware. Driver state is only the MMIO mapping.

Dependencies/integration: OF compatibles `nintendo,hollywood-otp` and `nintendo,latte-otp`; relies on big-endian MMIO accessors and NVMEM permissions to restrict root access.

Risks: sensitive key material is exposed through NVMEM to root. No explicit command-completion polling is present, so hardware is assumed to provide data synchronously after command write.

Test signals: bank-size mapping for Wii versus Wii U, big-endian read command formation, root-only sysfs visibility, and multiword reads crossing bank boundaries.
