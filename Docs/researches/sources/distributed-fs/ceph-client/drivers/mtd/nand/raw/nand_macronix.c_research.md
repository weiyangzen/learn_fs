# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_macronix.c

Purpose: this manufacturer extension configures Macronix raw NAND quirks and features: bad-block marker policy, read retry, randomizer OTP enablement, block protection, deep power-down suspend/resume, and OTP user-protection-region access for selected AC devices.

Important APIs, types, and functions: `macronix_nand_manuf_ops` exposes `.init`. `macronix_nand_onfi_init()` parses the Macronix ONFI vendor table. `macronix_nand_setup_read_retry()` writes `ONFI_FEATURE_ADDR_READ_RETRY`. `macronix_nand_randomizer_check_enable()` programs randomizer OTP bits. `mxic_nand_lock()` and `mxic_nand_unlock()` become `chip->ops.lock_area/unlock_area`. `macronix_30lfxg18ac_*_otp()` functions implement MTD user OTP callbacks.

Control flow: init marks SLC devices with first/second-page BBM, clears broken timing-mode feature bits for known AC model strings, enables ONFI-derived read retry and optional randomizer, probes block-protection support by reading the protection feature, adds deep-power-down hooks for selected AD parts, and registers OTP callbacks for supported 30LFxG18AC models.

State and persistence: state is mostly feature-register state on target 0. Randomizer OTP programming is persistent in flash. Block protection is volatile/configurable through feature address `0xA0`. Deep power-down suspend sends `0xB9`; resume toggles chip select by issuing the same low-level operation and waits for tRDP.

Dependencies and integration points: the file uses ONFI SET/GET FEATURES, device-tree property `mxic,enable-randomizer-otp`, raw page read/program helpers, target selection, MTD OTP callback slots, and manufacturer model strings.

Risks: randomizer enablement performs an OTP-affecting page program and is gated by DT but still permanent. Block-protection support assumes power-on all-lock state when probing. OTP support reports unlocked because lock state cannot be read, and locking is not supported. Deep power-down is model-list driven and only targets chip select 0.

Test signals: verify feature-list bits after init, read-retry mode changes, randomizer logs and persistence, lock/unlock behavior after probe, suspend/resume recovery after `0xB9`, OTP read/write bounds across 30 pages, and no timing-mode SET/GET attempts for broken AC models.
