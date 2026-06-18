# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/main.h

## Purpose
Declares shared helpers implemented by `main.c` and small inline utilities for b43legacy channel/rate conversion. It also defines the padding macro used by packed firmware-facing structures.

## Important APIs, Types, and Functions
Defines `PAD_BYTES` through token-pasting helper macros. Inline helpers are `b43legacy_freq_to_channel_bg`, `b43legacy_freq_to_channel`, `b43legacy_channel_to_freq_bg`, `b43legacy_channel_to_freq`, `b43legacy_is_cck_rate`, and `b43legacy_is_ofdm_rate`. Prototypes cover TSF access, SHM access, host-flag read/write, dummy transmission, wireless core reset, MAC suspend/enable, and controller restart.

## Control Flow
Inline channel conversion maps 2.4 GHz frequencies to channel IDs, with channel 14 handled specially at 2484 MHz. Rate helpers classify the four CCK hardware rates and treat all other b43legacy rates as OFDM. The declared functions are called by PHY/radio/xmit/debugfs/DMA paths to manipulate shared memory, timing, and MAC/core state.

## State and Persistence
The header itself owns no state. Its APIs mutate persistent hardware state: SHM contents, host flags, TSF registers, template RAM indirectly through dummy transmission/core reset, MAC enabled/suspended state, and restart work scheduling.

## Dependencies and Integration Points
Includes `b43legacy.h` for device types and rate constants. It is a cross-module interface between `main.c`, xmit, debugfs, DMA/PIO, PHY, and radio code.

## Risks
Rate classification depends on constants where rate values equal Mbps times two; changing constants breaks PLCP and rate-table logic. Channel helpers only support 2.4 GHz BG behavior, which matches b43legacy scope but would be wrong for 5 GHz. Padding macros affect packed firmware structures and should not be casually changed.

## Test Signals
Compile all users, verify channel 1/6/11/14 conversions, validate CCK/OFDM PLCP generation through TX tests, and confirm SHM/TSF/debugfs accessors link correctly. Core reset and MAC suspend/enable behavior are validated through start/stop and suspend/resume cycles.
