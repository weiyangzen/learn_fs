# sources/distributed-fs/ceph-client/drivers/mfd/wm8350-core.c

`wm8350-core.c` is the common MFD core for WM8350/WM8351/WM8352 PMICs. It exports register helpers, manages the hardware security lock, implements AUXADC reads, integrates IRQ setup, identifies chip revisions, runs platform initialization, and registers child platform devices.

Important APIs include `wm8350_clear_bits()`, `wm8350_set_bits()`, `wm8350_reg_read()`, `wm8350_reg_write()`, `wm8350_block_read()`, `wm8350_block_write()`, `wm8350_reg_lock()`, `wm8350_reg_unlock()`, `wm8350_read_auxadc()`, `wm8350_auxadc_irq()`, `wm8350_client_dev_register()`, and `wm8350_device_init()`. Init reads reset ID, ID, and revision, rejects unsupported customer IDs and unknown revisions, sets PMIC limits and revision coefficients, initializes AUXADC completion/lock, initializes IRQs, optionally requests the AUXADC IRQ, runs `pdata->init`, unmasks system interrupts, and registers codec, GPIO, hwmon, power, RTC, and watchdog devices.

State includes `unlocked`, `auxadc_mutex`, `auxadc_done`, `irq_base`, `chip_irq`, PMIC/power revision fields, child platform-device pointers, and hardware security/AUXADC/interrupt registers. Dependencies include regmap, platform devices, WM8350 subsystem headers, IRQ support, and platform data.

Risks: the copied source has a duplicated `platform_device_alloc()` assignment; `wm8350_reg_read()` can return undefined `data` after regmap failure; AUXADC waits only 5 ms and can return zero after timeout; child registration failures are non-fatal; IRQ init can return success after IRQ descriptor allocation failure. Test signals include chip ID/revision matrix probes, child device binding, lock/unlock behavior, AUXADC with and without IRQ, timeout behavior, and regmap failure injection.
