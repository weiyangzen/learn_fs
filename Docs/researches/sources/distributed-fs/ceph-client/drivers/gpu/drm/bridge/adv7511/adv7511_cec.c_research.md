<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_cec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_cec.c

## Purpose

`adv7511_cec.c` implements optional HDMI CEC support for ADV7511/ADV7533/ADV7535 bridge variants using the DRM HDMI CEC connector helper interface.

## Important APIs, Types, And Functions

- RX register arrays for the three hardware receive buffers and `ADV7511_INT1_CEC_MASK`.
- `adv_cec_tx_raw_status()`: converts TX-ready/arbitration-lost/retry-timeout interrupt bits and low-drive counters into CEC transmit completion status.
- `adv7511_cec_rx()`: reads one RX buffer, clamps length to 16, clears/re-enables that buffer, and delivers the message.
- `adv7511_cec_irq_process()`: handles TX status and RX buffers in hardware timestamp order.
- `adv7511_cec_enable()`: powers CEC up/down, clears RX buffers, enables/disables CEC IRQs, and resets logical-address state.
- `adv7511_cec_log_addr()`: programs up to three logical address masks.
- `adv7511_cec_transmit()`: sets retry count, clears TX IRQs, writes the CEC frame, length, and transmit-enable bit.
- `adv7511_cec_init()`: obtains/enables the CEC clock, resets CEC, configures non-legacy RX mode and clock divider, and stores the DRM connector.

## Control Flow

CEC init prepares the hardware block and leaves it powered down if the CEC clock is unavailable except for probe deferral. Enabling powers the block, clears RX buffers, disables TX, and enables main interrupt bits. IRQ processing first reports TX completion if relevant, then reads `CEC_RX_STATUS` to reconstruct oldest-to-newest RX buffer order before delivering messages. Transmit writes the full frame before setting TX enable.

## State And Persistence Behavior

Software state includes `cec_connector`, `cec_enabled_adap`, up to three logical addresses in `cec_addr[]`, `cec_valid_addrs`, and CEC clock frequency. Hardware state persists in CEC clock divider, RX buffer controls, TX frame registers, logical-address masks, and main interrupt enable/status registers.

## Dependencies And Integration Points

It depends on media CEC constants, DRM HDMI CEC helper callbacks, clocks, regmap, and ADV7511 chip-info `reg_cec_offset` for ADV7533-style register windows. The main driver calls its IRQ processor from shared interrupt handling.

## Risks And Edge Cases

Only three logical addresses are supported. `adv7511_cec_init()` returns success for non-deferral clock errors after powering CEC down, so CEC can be silently unavailable. RX length is clamped but malformed zero-length frames are ignored. The retry register uses at least one retry even when attempts is one because hardware semantics are unclear.

## Test Signals

CEC adapter registration, logical address allocation/clear, transmit OK/NACK/arbitration/timeout statuses, receiving multiple queued messages in order, CEC enable/disable cycles, ADV7511 and ADV7533 offset coverage, and missing-clock behavior are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_cec.c -->
