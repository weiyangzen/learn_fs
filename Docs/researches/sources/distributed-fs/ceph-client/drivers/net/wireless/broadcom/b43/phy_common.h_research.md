# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_common.h

## Purpose
`phy_common.h` defines the shared PHY abstraction for b43. It provides register routing macros, version masks, antenna and interference enums, TX power result/flag enums, the `struct b43_phy_operations` vtable, the central `struct b43_phy` state container, and prototypes for common PHY/radio lifecycle and register helpers.

## Important APIs, Types, and Data
- Register routing macros (`B43_PHY_CCK`, `B43_PHY_N`, `B43_PHY_N_BMODE`, `B43_PHY_OFDM`, `B43_PHY_EXTG`) encode PHY register spaces.
- Version masks decode analog type, PHY type, and PHY revision from the version register.
- `enum b43_interference_mitigation` and antenna identifiers define cross-PHY control values.
- `enum b43_txpwr_result` and `enum b43_phy_txpower_check_flags` describe TX power recalculation and scheduling.
- `struct b43_phy_operations` is the PHY vtable for allocation, preparation, init/exit, PHY/radio access, hardware power control, rfkill, analog switching, channel switching, antenna selection, interference mitigation, TX power, and periodic work.
- `struct b43_phy` stores the chosen vtable, per-PHY private pointer union, band support, gmode, full-init state, versioning, radio state, desired TX power, current channel definition, TX error counter, and optional debug locks.
- Function prototypes expose allocation/free/init/exit, PHY/radio register helpers, firmware-lock helpers, reset sequencing, channel switching, software rfkill, TX power work, TSSI reads, generic analog switching, 40 MHz check, and forced PHY clock.

## Control Flow
The header declares the vtable-driven PHY flow implemented in `phy_common.c` and PHY-specific files: select ops, allocate private state, optionally prepare structures/hardware, initialize, switch channels, perform periodic maintenance, adjust TX power, then exit and free. Register helpers centralize callers through common wrappers even when a PHY supplies custom low-level access.

## State and Persistence
`struct b43_phy` is persistent per wireless device and is reset/reinitialized across core lifecycle transitions. Its fields bridge software scheduling state, RF/hardware identity, current channel configuration, and debug access tracking. The header also defines constants for persistent hardware registers and shared behaviors but stores no data itself.

## Dependencies and Integration Points
- Includes Linux basic types and cfg80211/nl80211 channel definitions.
- Forward-declares `struct b43_wldev` and per-PHY private structs to avoid heavy include coupling.
- Used by every PHY implementation and by `main.c` for lifecycle, band support, rfkill, channel switching, and TX power management.

## Risks and Edge Cases
- Documentation says several vtable callbacks must not be NULL, but the type system does not enforce this; common code assumes many callbacks exist.
- The per-PHY private pointer is a union outside debug builds, so using the wrong member can alias silently.
- `struct cfg80211_chan_def *chandef` points into mac80211 configuration; callers must keep it valid across channel changes and initialization.
- Antenna constants are sparse (`B43_ANTENNA3 = 8`), so code must not treat them as dense array indices.
- Deprecated aliases `b43_radio_read16/write16` preserve old call sites but can obscure modernization work.

## Test Signals
- Compile all configured PHY variants to catch vtable and struct changes.
- Runtime coverage should include PHY allocation/free, init/exit, rfkill, channel switch, TX power check/adjust scheduling, TSSI reads, 40 MHz detection, and debug lock assertions.
