# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-common.h

## Purpose

`wcd-common.h` declares shared data structures and helper APIs for Qualcomm WCD codec support, especially SoundWire channel metadata, micbias storage, SoundWire component operations, and common callback functions. The source was read as a complete 46-line file.

## Important APIs, Types, and Functions

`WCD_MAX_MICBIAS` sets the common micbias array size to four entries. `struct wcd_sdw_ch_info` stores SoundWire port number, channel mask, and master channel mask; `WCD_SDW_CH()` initializes all three fields with matching channel masks. `struct wcd_common` carries a device pointer, max-bias count, and per-bias millivolt/register-control arrays.

The header declares `wcd_sdw_component_ops`, `wcd_get_micb_vout_ctl_val()`, `wcd_dt_parse_micbias_info()`, `wcd_update_status()`, `wcd_bus_config()`, and `wcd_interrupt_callback()`.

## Control Flow

There is no executable control flow in this header. It provides compile-time contracts for helper users and for the implementation in `wcd-common.c`.

## State and Persistence Behavior

The only state layout defined here is `struct wcd_common`, caller-owned and normally embedded in a codec driver. Values are runtime configuration derived from firmware/DT and do not persist outside driver lifetime.

## Dependencies and Integration Points

The header forward-declares `struct device`, `struct sdw_slave`, `struct sdw_bus_params`, `struct irq_domain`, and `enum sdw_slave_status` to keep includes light. It integrates with SoundWire codec drivers and common component binding.

## Risks and Edge Cases

Callers must keep `max_bias <= WCD_MAX_MICBIAS`; the parsing implementation does not independently clamp it. `WCD_SDW_CH()` assumes the master channel mask initially matches the slave channel mask, which may need adjustment for unusual routing.

## Test Signals

Build coverage from several WCD codec drivers is the main signal. Runtime tests should exercise `struct wcd_common` with one to four micbiases and verify channel metadata is interpreted correctly by SoundWire DAI setup code.
