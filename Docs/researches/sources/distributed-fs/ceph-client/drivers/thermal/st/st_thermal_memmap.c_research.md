# sources/distributed-fs/ceph-client/drivers/thermal/st/st_thermal_memmap.c

Purpose: memory-mapped STi thermal backend for the shared ST thermal core, currently matching `st,stih407-thermal`. It defines register fields, power control, IRQ threshold programming, regmap initialization, and platform driver glue.

Important functions and types: `st_mmap_thermal_regfields`, `st_mmap_thermal_trip_handler()`, `st_mmap_power_ctrl()`, `st_mmap_alloc_regfields()`, `st_mmap_enable_irq()`, `st_mmap_register_enable_irq()`, `st_mmap_regmap_init()`, `st_mmap_sensor_ops`, and `st_407_cdata`.

Control flow: probe delegates to `st_thermal_register()` with the memmap match table. The backend maps MMIO, creates a regmap, allocates high-threshold and interrupt-enable regfields in addition to common fields, registers a threaded rising IRQ, writes the critical threshold adjusted for raw sensor offset, and enables the interrupt.

Temperature and trip behavior: actual temperature reads are handled by `st_thermal.c`; this backend only programs the hardware interrupt high threshold to `crit_temp - temp_adjust_val`. The IRQ handler updates the thermal zone.

State and persistence: compatible data defines default calibration `16`, temperature adjustment `-95`, and critical threshold `120` raw C. Runtime hardware state includes power bits `THERMAL_PDN | THERMAL_SRSTN`, threshold register, and interrupt-enable bit.

Dependencies and integration points: shared ST core exports, platform MMIO, regmap MMIO, IRQ subsystem, thermal zone update, OF compatible `st,stih407-thermal`, and shared PM ops.

Risks: IRQ enable can occur before the shared core powers the sensor; the critical threshold is fixed from compatible data rather than thermal-zone trips; register-field index 0 depends on the header's mutually exclusive enum convention; power control writes both PDN and soft reset bits simultaneously as required by hardware.

Test signals: probe with valid MMIO and IRQ; trigger rising IRQ and verify thermal zone update; suspend/resume through shared PM and ensure threshold IRQ is reenabled; verify raw threshold accounts for `temp_adjust_val`.
