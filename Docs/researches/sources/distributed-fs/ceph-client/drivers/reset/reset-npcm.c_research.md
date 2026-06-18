# sources/distributed-fs/ceph-client/drivers/reset/reset-npcm.c

Purpose: Nuvoton NPCM BMC reset controller with USB PHY/device reset sequencing, optional restart handling, and NPCM8xx clock auxiliary registration.

Important APIs/types/functions: `struct npcm_reset_info`, `struct npcm_rc_data`, `npcm_rc_restart()`, `npcm_rc_setclear_reset()`, `npcm_reset_xlate()`, `npcm_usb_reset_npcm7xx()`, `npcm_usb_reset_npcm8xx()`, `npcm_usb_reset()`, `npcm_clock_adev_alloc()`, `npcm8xx_clock_controller_register()`, and `npcm_rc_probe()`.

Control flow: probe maps reset registers, sets two-cell xlate `(register offset, bit)`, registers the reset controller, performs BMC-family-specific USB reset sequencing based on MDLR strap bits, optionally registers restart using `nuvoton,sw-reset-number`, and for NPCM8xx creates an auxiliary clock controller. Assert/deassert/status update encoded register/bit pairs.

State and persistence: reset register bits and GCR PHY control bits persist in hardware. Driver stores BMC info, base, GCR regmap, and restart number.

Dependencies and integration: built-in platform driver, syscon GCR, auxiliary bus for NPCM8xx clocks, restart API, reset framework.

Risks and test signals: USB initialization has many hardware-order dependencies and fallback GCR lookup for old DTs. Test NPCM7xx/NPCM8xx paths, xlate offset validation, USB host/device enumeration after boot, restart number bounds, and auxiliary clock cleanup.
