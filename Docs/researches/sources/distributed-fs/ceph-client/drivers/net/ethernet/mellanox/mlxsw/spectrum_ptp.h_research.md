# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ptp.h

## Purpose
This header declares Spectrum PTP clock, state, packet, hwtstamp, ts-info, shaper, and stats interfaces. It also provides no-op or software-fallback inline definitions when `CONFIG_PTP_1588_CLOCK` is not reachable.

## Important APIs, Types, And Functions
When PTP is enabled, it declares Spectrum-1 and Spectrum-2 clock init/fini, PTP state init/fini, RX/TX packet timestamp handlers, Spectrum-1 timestamp notification, hwtstamp get/set, shaper work, ts-info, and stats helpers. When PTP support is disabled, clock/state init return `NULL`, hwtstamp setters return `-EOPNOTSUPP`, receive falls back to normal RX listener handling, transmit frees SKBs, and stats counts are zero. Spectrum-2 shaper/stats helpers are inline no-ops even outside the disabled block.

## Control Flow
Main Spectrum initialization can call the generation-appropriate clock and state init functions regardless of config. Port hwtstamp operations call generation-specific setters/getters. Trap and TX completion paths call generation-specific receive/transmitted functions; disabled builds degrade to non-timestamp behavior.

## State And Persistence
The header declares opaque `mlxsw_sp_ptp_clock` and references `mlxsw_sp_ptp_state` without defining their internals. Runtime state is implemented in `spectrum_ptp.c`; no persistent storage exists.

## Dependencies And Integration Points
It depends on Linux device and rhashtable types, forward declarations for Spectrum device/port, and PTP/hwtstamp types when enabled through included kernel headers in users. It integrates with RX listeners and SKB freeing in disabled mode.

## Risks And Edge Cases
Callers must tolerate `NULL` clock/state when PTP support is disabled. Disabled-mode TX handlers consume SKBs, so callers must not reuse them. API shape differs by generation, especially Spectrum-1 timestamp notifications and shaper work.

## Test Signals
Build with and without `CONFIG_PTP_1588_CLOCK`, verify timestamp ioctls return `-EOPNOTSUPP` in disabled builds, confirm normal RX/TX behavior without PTP, and verify enabled builds link all generation-specific functions.
