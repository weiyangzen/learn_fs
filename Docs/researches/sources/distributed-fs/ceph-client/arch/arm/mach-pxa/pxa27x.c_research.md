<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c

Purpose: PXA27x SoC-specific support for PM, IRQs, IO mapping, power-I2C, platform devices, DMA, and AC97/OTG quirks.

Important APIs/functions: `pxa27x_clear_otgph()` clears OTG peripheral hold; `pxa27x_configure_ac97reset()` switches AC97 reset pin between GPIO high and AC97 alternate function; `pxa27x_init_irq()` installs a 34-IRQ controller using `ichp_handle_irq`; `pxa27x_set_i2c_power_info()` enables `PCFR_PI2CEN` and registers power I2C. PM callbacks save MDREFR/PCFR/PSTR, clear FVC/PEDR/RCSR, support standby and mem sleep, and handle iWMMXt accumulator preservation.

Control flow: `postcore_initcall(pxa27x_init)` gates on `cpu_is_pxa27x()`, registers watchdog status, installs PM hooks and syscore ops, and registers legacy platform devices and DMA only when no DT is populated.

State and persistence: static PM `pwrmode`, DMA slave map, platform device arrays, syscore registrations, and power registers. Resume restores memory and power configuration.

Dependencies and integration: depends on PXA2xx MFP, keypad wake helper, DMAengine, GPIO, I2C, OHCI, UDC, ASoC, and `devices.c`.

Risks and test signals: AC97 warm reset workaround is GPIO-specific; power-I2C register updates are interrupt-protected but global. Test PXA27x boot, standby and mem suspend, keypad/USB/RTC wake, AC97 warm reset, power I2C probe, and DMA mappings for camera/I2S/SSP/MMC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c -->
