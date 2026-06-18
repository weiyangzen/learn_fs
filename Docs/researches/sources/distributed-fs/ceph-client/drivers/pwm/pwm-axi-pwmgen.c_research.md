# sources/distributed-fs/ceph-client/drivers/pwm/pwm-axi-pwmgen.c

Purpose: implements a waveform-capable PWM driver for the Analog Devices AXI PWM generator soft IP.

Important APIs/types/functions: `struct axi_pwmgen_ddata` stores regmap and PWM clock rate. `struct axi_pwmgen_waveform` is the hardware waveform representation. The driver implements `.round_waveform_tohw`, `.round_waveform_fromhw`, `.read_waveform`, and `.write_waveform`. `axi_pwmgen_setup()` verifies the core magic and ADI pcore major version, enables the core, enables force-align, and returns the channel count.

Control flow: probe maps MMIO into a regmap, validates hardware, allocates a PWM chip with the reported `NPWM`, enables AXI and optional external clocks, locks clock rate, validates the rate, marks the chip atomic, and registers it. Writes program period, duty, and offset registers for one channel, then write `LOAD_CONFIG`, which resynchronizes enabled channels.

State and persistence: software stores only regmap and clock rate. Hardware channel registers store period/duty/offset counts. The framework caches requested state; readback is available via hardware waveform registers.

Dependencies and integration: depends on ADI AXI common version macros, regmap-mmio, clocks, OF compatible `adi,axi-pwmgen-2.00.a`, and the PWM waveform API including character-device users.

Risks and test signals: `LOAD_CONFIG` can resynchronize all channels, so one consumer can glitch another unless periods are coordinated. Readback contains a FIXME about duty offset behavior when offset exceeds period. Test signals include core magic/version failure, channel count, clock-rate bounds, exact and rounded waveform ioctls, duty-offset programming, and multi-channel resynchronization behavior.
