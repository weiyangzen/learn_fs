# sources/distributed-fs/ceph-client/drivers/iio/adc/rcar-gyroadc.c

Renesas R-Car GyroADC IIO driver for an on-SoC ADC interface connected to external ADC devices. It supports multiple child ADC models/modes, per-channel VREF regulators, runtime PM, debug register access, and direct raw/scale/sample-frequency reads.

`struct rcar_gyroadc` stores MMIO base, clock, VREF regulators, mode, model, channel count, and sample width. Hardware helpers are `rcar_gyroadc_hw_init`, `rcar_gyroadc_hw_start`, `rcar_gyroadc_hw_stop`, and `rcar_gyroadc_set_power`. IIO callbacks are `rcar_gyroadc_read_raw` and `rcar_gyroadc_reg_access`. DT parsing and lifecycle are handled by `rcar_gyroadc_parse_subdevs`, `rcar_gyroadc_init_supplies`, probe/remove, and runtime PM suspend/resume.

Probe maps MMIO, gets `fck`, parses child ADC nodes to choose a single mode and channel table, enables VREF regulators, enables the clock, starts runtime PM, initializes hardware timing from clock rate and mode, starts sampling, registers IIO, then autosuspends. Raw reads claim direct mode, resume runtime PM, read the realtime data register masked to sample width, then autosuspend. Scale reads use the channel regulator voltage; sample frequency returns fixed 800 Hz.

Selected mode/sample width/channel table and regulator pointers are derived from DT and retained. Hardware sampling is stopped in runtime/system suspend or remove. Dependencies include platform MMIO resources, `fck`, child DT compatibles, child `vref` supplies, IIO direct mode, runtime PM, and optional R8A7792 interrupt registers.

Risks include mixed child modes failing probe, special MB88101 all-channel behavior, temporary `dev->of_node` switching while fetching child regulators, direct-mode `-EBUSY`, and delicate cleanup ordering. Test each mode, invalid child `reg`, missing VREF, R8A7792 debug ranges, runtime PM reads, scale values, remove cleanup, and clock timing rounding.
