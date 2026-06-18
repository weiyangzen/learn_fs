# sources/distributed-fs/ceph-client/drivers/uio/uio_fsl_elbc_gpcm.c

## Purpose
`uio_fsl_elbc_gpcm.c` exposes a peripheral connected to a Freescale/NXP enhanced Local Bus Controller bank in GPCM mode through UIO. It validates and programs eLBC BR/OR registers, maps the peripheral memory window, optionally provides netX 51/52 interrupt support, and exposes sysfs attributes for controlled BR/OR tuning.

## Important APIs, Types, And Functions
Private state is `struct fsl_elbc_gpcm`, which stores the device, eLBC register base, bank number, display name, and optional type-specific init/shutdown/IRQ callbacks. Sysfs attributes `reg_br` and `reg_or` use `reg_show()` and `reg_store()`. DT parsing and validation are handled by `get_of_data()` and `check_of_data()`. Probe and remove are `uio_fsl_elbc_gpcm_probe()` and `uio_fsl_elbc_gpcm_remove()`. Optional netX support adds `netx5152_irq_handler()`, `netx5152_init()`, and `netx5152_shutdown()`.

## Control Flow And State
Probe requires the global FSL LBC controller registers, parses the child node resource, bank number, `elbc-gpcm-br`, `elbc-gpcm-or`, optional `device_type`, IRQ, and `uio_name`, then validates bank, mode, address mask, and base address. It checks whether the bank is already valid and compatible, warns if behavior bits change, writes OR then BR with forced base/GPCM/valid bits, maps the resource with `ioremap()`, fills UIO memory metadata, optionally installs a type-specific IRQ handler, runs type init, registers UIO, and stores drvdata.

`reg_store()` permits runtime BR/OR changes only when the effective base address, GPCM mode, and address mask remain stable. NetX IRQ handling checks enabled and active interrupt bits in the mapped DPM window, disables global interrupts, and leaves acknowledgement/re-enable to userspace. Remove unregisters UIO, calls type shutdown, and unmaps the resource.

## Dependencies And Integration Points
The driver depends on `FSL_LBC`, OF address/IRQ parsing, UIO core, eLBC register definitions, and optional `CONFIG_UIO_FSL_ELBC_GPCM_NETX5152`. It matches `fsl,elbc-gpcm-uio` DT nodes.

## Risks And Edge Cases
Programming BR/OR affects shared local-bus state, so DT validation and sysfs write restrictions are critical. The global `fsl_lbc_ctrl_dev` must be initialized before probe. Optional IRQs without a known type handler are ignored. NetX offsets and masks are type-specific and must not be used for generic peripherals.

## Test Signals
Test DT validation failures for bank, mode, size mask, and base address; already-configured bank compatibility; sysfs BR/OR allowed and rejected writes; generic no-IRQ devices; netX IRQ disable/init/shutdown; UIO mmap correctness; and remove cleanup after userspace has opened the device.
