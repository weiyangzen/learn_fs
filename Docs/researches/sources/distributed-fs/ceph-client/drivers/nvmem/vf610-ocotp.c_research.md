# sources/distributed-fs/ceph-client/drivers/nvmem/vf610-ocotp.c

Purpose: Freescale/NXP Vybrid VF610 OCOTP read-only NVMEM provider.

Important APIs/types/functions: `base_to_fuse_addr_mappings` maps sparse MMIO offsets to fuse addresses. `vf610_ocotp_calculate_timing()` computes timing fields from the clock rate. `vf610_ocotp_wait_busy()` polls `BUSY` and clears `ERR` on timeout. `vf610_ocotp_read()` maps offsets, programs timing/address/read command, waits, and returns fuse data or zero for unmapped offsets.

Control flow: probe maps the OCOTP resource, gets the clock, computes timing once, fills static NVMEM config sized to the resource, and registers. Reads loop 4-byte chunks, skip unknown offset mappings as zero, and do not enable/disable the clock around reads.

State/persistence: OTP fuses persist in hardware and are read-only. Driver state includes timing derived from the clock rate.

Dependencies/integration: OF compatible `fsl,vf610-ocotp`; depends on clock framework, MMIO, and NVMEM provider.

Risks: `vf610_get_fuse_address()` returns zero for the first valid fuse address, but `vf610_ocotp_read()` only treats `fuse_addr > 0` as valid, so the mapping for fuse address 0 is skipped and returned as zero. Clock rate changes after probe are not reflected in timing. Hardware read errors are logged but the returned TRM error value is still passed to consumers.

Test signals: mapping table coverage including offset `0x400`, timing calculation at expected clock rates, busy timeout, error-bit handling, and reads from unmapped offsets.
