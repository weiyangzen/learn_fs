# sources/distributed-fs/ceph-client/drivers/mmc/core/sd_uhs2.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sd_uhs2.c

### Purpose
`sd_uhs2.c` implements SD UHS-II attach, enumeration, configuration, legacy SD-TRAN initialization, PM, reset, and command-packet preparation. It bridges native UHS-II packets with the existing MMC request model and the SD memory-card setup flow.

### Important APIs, Types, And Functions
Public entry points are `mmc_attach_sd_uhs2()` and `mmc_uhs2_prepare_cmd()`. `sd_uhs2_ops` provides bus remove, detect, alive, suspend/resume, runtime PM, shutdown, and hardware reset callbacks. Core helpers include `sd_uhs2_power_up()`, `sd_uhs2_power_off()`, `sd_uhs2_phy_init()`, `sd_uhs2_dev_init()`, `sd_uhs2_enum()`, `sd_uhs2_config_read()`, `sd_uhs2_config_write()`, `sd_uhs2_go_dormant_state()`, `sd_uhs2_init_card()`, `sd_uhs2_legacy_init()`, and `sd_uhs2_reinit()`.

### Control Flow
`mmc_attach_sd_uhs2()` first checks host capability, powers off legacy SD, then tries UHS-II initialization at 52 MHz and 26 MHz. Attach powers up the host, initializes the PHY, sends DEVICE_INIT, enumerates a node ID, allocates a card, reads card configuration registers, writes negotiated generic/PHY/link settings, optionally enters dormant state for speed-range changes, sets `host->uhs2_sd_tran`, and runs legacy SD initialization through SD-TRAN. Legacy init resets the SD side, sends CMD8/ACMD41/CID/RCA/CSD/SCR, decodes SD identity, selects high power via CMD6 group 3 when possible, and checks write-protect. `mmc_uhs2_prepare_cmd()` converts an MMC request into UHS-II CCMD/DCMD metadata, handles APP tagging, multi-block half-duplex transfer mode, and payload length.

### State, Persistence, And Dependencies
State is stored in `host->ios`, `host->uhs2_caps`, `host->uhs2_sd_tran`, `host->uhs2_app_cmd`, `host->card`, and `card->uhs2_config`. Configuration writes change card link/PHY behavior and host UHS-II register settings through `host->ops->uhs2_control()`. Dependencies include UHS-II public constants, generic MMC/SD helpers, SD memory-card decoding, bus attach, PM runtime, and host UHS-II control operations such as `UHS2_SET_IOS`, `UHS2_PHY_INIT`, `UHS2_SET_CONFIG`, interrupt enable/disable, clock control, and dormant checks.

### Integration Points
This path is attempted before/alongside legacy SD probing on hosts with `MMC_CAP2_SD_UHS2`. It reuses `sd_type`, `mmc_decode_cid()`, `mmc_sd_get_csd()`, `mmc_decode_scr()`, `mmc_sd_get_ro()`, and `mmc_sd_switch()` for the SD-TRAN phase. Host drivers must provide UHS-II controls and request handling that understands `cmd->uhs2_cmd`.

### Risks
The sequence is spec-driven and fragile: DEVICE_INIT retry semantics, node ID assignment, configuration register endianness, dormant-state transitions, and config-complete polling must align with host hardware. `sd_uhs2_config_write()` assumes 2-lane full/half-duplex choices and hardcodes max retry to 3. PM suspend powers off rather than using hibernate, so resume must fully reinitialize and verify identity. Incorrect APP state handling can corrupt subsequent SD-TRAN commands. Removal lacks the graceful power-off-notify/cache handling found in `sd.c`.

### Test Signals
Use a UHS-II-capable host/card at both 52 MHz and 26 MHz retry frequencies, speed range A/B, half-duplex and full-duplex modes, dormant-state transitions, SD-TRAN legacy initialization, high-power CMD6 selection, card removal detection, runtime/system suspend/resume, hardware reset, and multi-block UHS-II command packet generation.
