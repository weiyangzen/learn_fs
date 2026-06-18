# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-common.c

## Purpose

`wcd-common.c` provides shared Qualcomm WCD codec helper code for micbias voltage parsing/conversion, SoundWire component runtime-PM setup, SoundWire status/bus callbacks, and interrupt draining. The source was read as a complete 144-line file.

## Important APIs, Types, and Functions

Exported helpers are `wcd_get_micb_vout_ctl_val()`, `wcd_dt_parse_micbias_info()`, `wcd_sdw_component_ops`, `wcd_update_status()`, `wcd_bus_config()`, and `wcd_interrupt_callback()`. Internal `wcd_get_micbias_val()` reads `qcom,micbiasN-microvolt` properties, falls back to 1800 mV, and stores both millivolt and register-control forms through the caller's `struct wcd_common`.

## Control Flow

Micbias parsing loops from 1 to `common->max_bias`, reads each DT property, converts microvolts to millivolts, validates the 1000 mV to 2850 mV range, and computes the register value as `(mV - 1000) / 50`. Component bind enables runtime PM with a 3000 ms autosuspend delay; unbind disables it. SoundWire attach handling disables regcache cache-only mode and synchronizes cached writes. Bus configuration writes bank-specific clock divider control. Interrupt handling repeatedly dispatches nested IRQ 0 and rereads three interrupt status registers until all are clear.

## State and Persistence Behavior

The only caller-visible state is populated in `struct wcd_common`: `micb_mv[]` and `micb_vout[]`. Runtime PM state is stored in the device core. Register cache state is held by regmap. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on device tree, component framework, runtime PM, SoundWire APIs, irqdomain nested IRQ mapping, and regmap. It is intended for codec SoundWire slave drivers that share micbias and bus callback patterns.

## Risks and Edge Cases

`wcd_get_micbias_val()` logs the converted invalid value after `wcd_get_micb_vout_ctl_val()` returns a negative error, so the error message may show the error code rather than the original millivolt value. `sprintf()` into a 64-byte buffer is safe for the fixed property pattern and small index, but not bounds-checked. `wcd_interrupt_callback()` assumes the regmap exists; `wcd_update_status()` checks for regmap but the IRQ callback does not. The nested interrupt loop relies on status registers eventually clearing.

## Test Signals

Useful tests are DT parsing with missing, minimum, maximum, and out-of-range micbias properties; SoundWire attach tests that verify regcache sync; bus config tests for `next_bank`; IRQ tests with synthetic status register sequences; and runtime-PM bind/unbind smoke coverage.
