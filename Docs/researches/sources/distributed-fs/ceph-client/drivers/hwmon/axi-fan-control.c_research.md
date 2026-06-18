# sources/distributed-fs/ceph-client/drivers/hwmon/axi-fan-control.c

Purpose: platform hwmon driver for Analog Devices AXI Fan Control HDL core. It exposes PWM duty, fan RPM/fault, die temperature, and programmable automatic PWM temperature thresholds.

Important APIs, types, and functions: `axi_fan_control_data` stores MMIO base, hwmon device, clock rate, IRQ, pulses-per-revolution, and IRQ-derived state flags. `axi_ioread()`/`axi_iowrite()` wrap register access. `axi_fan_control_get_pwm_duty()` and `axi_fan_control_set_pwm_duty()` convert between sysfs PWM 0-255 and core PWM width/period registers. `axi_fan_control_get_fan_rpm()` converts tach period to RPM using clock rate and PPR. `axi_fan_control_irq_handler()` handles PWM changes, tach errors, temperature-triggered changes, and new measurements. Extra threshold attributes are built with `SENSOR_DEVICE_ATTR_RW`.

Control flow: probe matches a device-tree compatible, maps registers, enables the clock, verifies AXI core major version, reads `pulses-per-revolution`, unmasks selected interrupts, releases reset, registers hwmon with extra groups, then requests a threaded IRQ. Reads and writes are direct MMIO operations. IRQs update software flags, notify hwmon on hardware PWM changes, update tach reference/tolerance after software PWM changes, and latch fan fault until read.

State and persistence: hardware registers hold PWM width, threshold points, tach period/tolerance, and reset/IRQ state. Software state includes `fan_fault` latch cleared on `fan1_fault` read, `hw_pwm_req` to distinguish automatic core changes, and `update_tacho_params` to defer tach parameter updates until a fresh measurement. No cache is used for normal values.

Dependencies and integration points: depends on platform/OF matching, `adi-axi-common.h` version macros, MMIO I/O, clocks, interrupts, hwmon core, and device properties. It integrates with hwmon notifications and exposes nonstandard auto-point attributes as sysfs groups.

Risks: code trusts `PWM_PERIOD` is nonzero. RPM math depends on valid clock rate and PPR property. IRQ comments mention hardware stabilization delays and distinguish software versus automatic PWM changes; missed or reordered IRQs could leave tach parameters stale. Threshold conversion uses two formulas in different paths (`show/store` versus input temperature read), so unit consistency deserves attention. `fan_fault` is not protected by a lock.

Test signals: test device-tree probe with valid/invalid PPR and version mismatch, read/write PWM endpoints and auto thresholds, verify RPM against known tach signal, induce tach error and confirm `fan1_fault` latch clears, and confirm hwmon notification on hardware-driven PWM changes. IRQ path testing should cover software PWM update followed by new measurement.
