# sources/distributed-fs/ceph-client/drivers/nvmem/rockchip-otp.c

Purpose: Read-only NVMEM provider for newer Rockchip OTP controllers with reset, bulk clocks, optional ECC, and variant-specific word sizes.

Important APIs/types/functions: `struct rockchip_data` defines size, read offset, word size, clock names, and low-level read callback. `rockchip_otp_read()` is the NVMEM callback and adapts byte requests to variant word reads. `px30_otp_read()`, `rk3568_otp_read()`, and `rk3588_otp_read()` implement controller generations. Helpers reset the OTP PHY, poll status, and enable/disable ECC through SBPI.

Control flow: probe selects match data, maps MMIO, allocates clock bulk array, gets clocks and reset controls, fills static NVMEM config, and registers. Reads enable all clocks, add any variant read offset, allocate temporary word buffers for multi-byte word sizes, call the low-level reader, copy requested bytes, and disable clocks.

State/persistence: OTP contents persist in hardware and are read-only. State consists of clocks, resets, MMIO base, and variant data.

Dependencies/integration: supports PX30/RK3308/RK3528/RK3562/RK3568/RK3576/RK3588 compatibles; depends on reset controller, clock bulk APIs, MMIO polling, and legacy fixed OF cells.

Risks: static `otp_config` is mutated on probe. ECC status errors on RK3568 abort reads with `-EIO`; board cell definitions must account for word-size/read-offset transformations. Reset is performed for some variants on each read, which can be expensive but ensures controller state.

Test signals: variant clock list acquisition, reset failure, ECC enable failure, ECC read error, RK3588 auto-read timeout, partial byte reads from 16/32-bit words, and compatible size/read-offset coverage.
