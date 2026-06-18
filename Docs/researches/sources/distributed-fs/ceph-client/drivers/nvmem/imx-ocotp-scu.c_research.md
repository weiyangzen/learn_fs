<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp-scu.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp-scu.c

## Purpose
Implements i.MX8 SCU-mediated OCOTP access, reading fuses through SCU RPC and writing single words through an ARM SMC call while respecting ECC and hole regions.

## Important APIs, Types, And Functions
`struct ocotp_devtype_data` describes fuse count and special regions. `in_hole()` and `in_ecc()` classify indexes. `imx_sc_misc_otp_fuse_read()` issues SCU MISC OTP read RPCs. `imx_scu_ocotp_read()` reads words into a temporary buffer, zeroes holes, and serializes with `scu_ocotp_mutex`. `imx_scu_ocotp_write()` validates single-word writes, rejects holes, checks ECC words are still zero, and invokes `arm_smccc_smc(IMX_SIP_OTP_WRITE, ...)`.

## Control Flow
Probe gets the SCU IPC handle, selects i.MX8QXP or i.MX8QM data, sizes the provider, and registers writable `imx-scu-ocotp`. Reads round to 32-bit words and call SCU RPC per non-hole word. Writes allow exactly four bytes, optionally pre-read ECC regions to avoid reprogramming, then issue the secure monitor write.

## State And Persistence
Driver state is SCU IPC pointer, SoC region map, and device pointer. The global mutex serializes all SCU OCOTP accesses. Fuse programming is permanent.

## Dependencies And Integration Points
Depends on IMX_SCU firmware RPC, ARM SMCCC, platform OF matching, and NVMEM provider APIs. It uses legacy fixed OF cells and can serve consumers that need SoC IDs or calibration values.

## Risks
Write support can permanently alter OTP. Offset handling treats NVMEM offsets as word indexes despite a byte-sized config, so callers must follow the configured word size and core alignment. ECC-region policy only checks nonzero before programming and cannot fully prevent hardware-specific one-time constraints. Firmware/SMC errors propagate but may not be descriptive.

## Test Signals
Test reads in normal, ECC, and hole regions; writes of wrong sizes; write attempts to holes; ECC write to nonzero words; successful write/readback on disposable fuses; and SCU IPC unavailable deferral/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp-scu.c -->
