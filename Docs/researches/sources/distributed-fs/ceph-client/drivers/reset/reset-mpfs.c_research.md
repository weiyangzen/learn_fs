# sources/distributed-fs/ceph-client/drivers/reset/reset-mpfs.c

Purpose: Microchip PolarFire SoC peripheral reset controller, usable both as an MFD platform child and as an auxiliary device from the MPFS clock driver.

Important APIs/types/functions: `struct mpfs_reset`, `mpfs_assert()`, `mpfs_deassert()`, `mpfs_status()`, `mpfs_reset()`, `mpfs_reset_xlate()`, `mpfs_reset_mfd_probe()`, `mpfs_reset_adev_probe()`, and exported `mpfs_reset_controller_register()`.

Control flow: reset IDs are based on clock IDs offset by `CLK_ENVM`. Xlate rejects `CLK_RESERVED` and IDs outside the peripheral range. Assert sets bits in `REG_SUBBLK_RESET_CR`; deassert clears; reset pulses with 100-200 us delay. MFD probe gets parent syscon regmap; auxiliary probe receives regmap as platform data.

State and persistence: hardware register stores reset state; no cache.

Dependencies and integration: MFD syscon path, auxiliary bus path, MPFS clock namespace `MCHP_CLK_MPFS`, dt-bindings clock IDs, reset framework.

Risks and test signals: reset IDs are clock IDs, which can confuse consumers. Test both registration paths, fabric reset rejection, module namespace import/export, and reset/status polarity.
