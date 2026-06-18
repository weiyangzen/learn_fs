# sources/distributed-fs/ceph-client/drivers/net/phy/bcm-cygnus.c

## Purpose
Implements Broadcom Cygnus and Omega internal PHY support, using the shared Broadcom PHY library for register access, interrupts, EEE, APD, downshift, stats, and AFE workarounds.

## Important APIs, Types, and Functions
Private state `bcm_omega_phy_priv` stores a statistics shadow array. Important functions are `bcm_cygnus_afe_config`, `bcm_cygnus_config_init`, `bcm_cygnus_resume`, `bcm_omega_config_init`, `bcm_omega_resume`, `bcm_omega_get_tunable`, `bcm_omega_set_tunable`, `bcm_omega_get_phy_stats`, and `bcm_omega_probe`.

## Control Flow and State
Cygnus config masks interrupts globally, configures the interrupt mask register to unmask link/speed/duplex events, applies several AFE calibration writes, advertises EEE, and enables APD. Resume repeats config-init and restarts autoneg. Omega config logs revision once, performs a dummy BMSR read to work around a first-MDIO-read issue, applies 28 nm A0/B0 AFE config for revision 0, reads downshift state, enables EEE only when downshift is disabled, and enables APD. Omega tunable writes update downshift, adjust EEE accordingly, and restart autoneg.

## Dependencies and Integration Points
Depends on `bcm-phy-lib.h`, Broadcom PHY register definitions in `linux/brcmphy.h`, generic phylib, ethtool tunables/stats, and Broadcom internal PHY IDs. Driver entries wire shared library callbacks for interrupts and stats.

## Risks and Test Signals
Risks include AFE magic values being revision-specific, interrupt mask polarity confusion, EEE and downshift interaction causing link failures, resume not preserving user tunables, and stats shadow allocation mismatches. Test signals include Cygnus/Omega hardware bring-up, interrupt-driven link/speed changes, resume link recovery, downshift tunable get/set, EEE advertisement with downshift enabled/disabled, and ethtool stats accumulation.
