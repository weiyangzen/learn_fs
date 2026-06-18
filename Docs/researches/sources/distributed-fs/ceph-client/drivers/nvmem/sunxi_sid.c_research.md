# sources/distributed-fs/ceph-client/drivers/nvmem/sunxi_sid.c

Purpose: Allwinner sunXi Security ID NVMEM provider and entropy contributor.

Important APIs/types/functions: `struct sunxi_sid_cfg` supplies value offset, size, and whether register readout is required. `sunxi_sid_read()` copies directly from SID memory with trailing-byte handling. `sun8i_sid_register_readout()` performs command-based reads through `PRCTL/RDKEY`; `sun8i_sid_read_by_reg()` uses it for H3 unreliable memory window. Probe registers NVMEM and feeds the SID bytes to `add_device_randomness()`.

Control flow: probe selects compatible config, maps MMIO, allocates NVMEM config, chooses direct or register read callback, registers read-only OTP NVMEM, allocates a temporary buffer, reads the full SID, adds it as device randomness, frees the buffer, and stores drvdata.

State/persistence: SID/OTP data persists in SoC hardware. Driver state includes base and value offset; no cache.

Dependencies/integration: many Allwinner compatibles from sun4i A10 through sun50i H6; depends on MMIO polling, NVMEM provider, and kernel random subsystem.

Risks: `.stride = 4` with `.word_size = 1` means core alignment rules must match expected consumers. Adding SID to randomness is useful but should not be treated as secret entropy if IDs are readable. H3 register-read path has a 250 ms poll timeout.

Test signals: direct and register-read variants, trailing byte reads, PRCTL timeout, randomness path allocation failure, and compatible-specific sizes/value offsets.
