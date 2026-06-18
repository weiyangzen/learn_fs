# sources/distributed-fs/ceph-client/drivers/thermal/loongson2_thermal.c

Purpose: Loongson-2 thermal driver for LS2K1000 and LS2K2000. It registers a thermal zone, reads temperature through SoC-specific formulas, programs low/high hardware trip registers from thermal framework set-trips callbacks, and services thermal interrupts.

Important APIs/types/functions: `struct loongson2_thermal_chip_data` supplies selected sensor index and flags, notably `LS2K2000_THSENS_OUT_FLAG` for a separate output register resource. `struct loongson2_thermal_data` stores control/temp MMIO and chip data. `loongson2_set_ctrl_regs()` writes threshold registers with Celsius offset by `HECTO` and optional enable bit. `loongson2_2k1000_get_temp()` reads `LOONGSON2_THSENS_OUT_REG`; `loongson2_2k2000_get_temp()` reads the separate temp resource and applies `(raw * 820 / 0x4000 - 311) * KILO`. `loongson2_thermal_irq_thread()` acknowledges interrupts and updates the thermal zone.

Control flow: probe maps control registers and, for LS2K2000, temp registers; gets IRQ; acknowledges current interrupt status; disables thresholds initially; scans thermal OF zone IDs 0..3 until registration succeeds; registers a threaded IRQ; and adds hwmon. Runtime `set_trips()` converts millidegree inputs to degrees and enables hardware thresholds.

State/persistence: threshold register state persists in hardware; software stores only MMIO pointers and match data. Dependencies: OF compatibles `loongson,ls2k1000-thermal` and `loongson,ls2k2000-thermal`, threaded IRQs, thermal OF, hwmon.

Risks: the probe loop treats `-ENODEV` as fatal but continues on other errors, which is unusual and should be checked against thermal OF semantics; threshold clamping uses `clamp(-40, low, high)` and `clamp(125, low, high)` ordering that deserves tests; no remove/suspend path reprograms thresholds. Test signals include both chip formulas, IRQ acknowledge/update, thermal-zone ID probing, set-trip register encoding, and hwmon creation.
