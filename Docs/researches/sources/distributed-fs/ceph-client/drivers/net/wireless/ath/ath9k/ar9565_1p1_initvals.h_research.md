# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9565_1p1_initvals.h

Purpose: Provides the AR9565 1.1 initval layer. It mostly reuses AR9565 1.0 tables and overrides only the radio postamble values needed for 1.1-or-later silicon.

Important APIs and data: Macro aliases map `ar9565_1p1_mac_core`, MAC postamble, baseband core/postamble, radio core, SOC pre/postamble, RX gain, TX gain, PCIe SERDES, fast-clock, no-XLNA RX gain, and Japan CCK FIR names to their 1.0 equivalents. The only local array is `ar9565_1p1_radio_postamble`, a five-column modal table with 1.1-specific radio postamble entries.

Control flow: `ar9003_hw.c` selects these symbols for `AR_SREV_9565_11_OR_LATER()`. Because most symbols are aliases, initialization flows exactly like the 1.0 branch except that `ah->iniRadio[ATH_INI_POST]` points at the 1.1 radio postamble. TX/RX gain override helpers use the 1.1 names, which resolve to 1.0 data except where separately overridden.

State and persistence: No runtime state is owned by the header. It controls which read-only tables are referenced by `struct ath_hw` and later written to device registers during reset/channel setup.

Dependencies and integration points: Depends directly on `ar9565_1p0_initvals.h` being included before use in `ar9003_hw.c`. It integrates with AR9565 revision detection, PCIe power-save setup, TX/RX gain selection, and shared AR9003 init sequencing.

Risks: The alias-heavy design makes the single override easy to miss. Any future 1.1-specific change must define a real table before the alias is used or it will silently keep 1.0 behavior. Include ordering is material because the alias targets must already exist. Misclassifying 1.0 versus 1.1 hardware affects radio postamble programming.

Test signals: Confirm AR9565 1.1-or-later devices choose this branch, compare radio register writes against the 1.1 postamble, run association/throughput tests across 2.4 GHz channels, exercise PCIe suspend/resume, and ensure AR9565 1.0 behavior is unchanged.
