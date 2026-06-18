# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ch7xxx.c

Purpose: i915 DVO driver for Chrontel CH7xxx DVI/TV-output chips, especially CH701x/CH7301 class devices.

Important APIs/functions: exported `ch7xxx_ops` implements init/detect/mode_valid/mode_set/dpms/get_hw_state/dump_regs/destroy. Helpers identify vendor/device IDs, read/write 8-bit I2C registers, detect DVI connection, program PLL/timing control registers, and set power management bits.

Control flow: init allocates private state, probes vendor and device IDs quietly, then enables logging after a match. Detect temporarily powers DVI logic, reads connection-detect, and restores original power state. Mode set chooses timing values based on <=65 MHz or higher clocks, programs clock and PLL controls, updates input sync polarity, and configures sync outputs. DPMS toggles DVI power bits.

State and persistence: `struct ch7xxx_priv` stores only quiet flag. Hardware state persists in chip registers.

Dependencies and integration points: i915 DVO core, Linux I2C, DRM debug logging, and DVO connector/encoder machinery.

Risks: ID tables are limited. Detection manipulates power management and assumes safe restoration. I2C failures are mostly logged but not returned through DVO ops. Mode programming is coarse and only supports fixed clock ranges with a 165 MHz cap.

Test signals: probe across supported Chrontel IDs, DVI connection detection, 65 MHz threshold modes, sync polarity, DPMS state readback, and register dumps.
