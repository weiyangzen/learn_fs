# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2055.h

## Purpose
`radio_2055.h` defines the BCM2055 radio register map, the N-PHY revision-2 channel-table row layout, and the public helper prototypes implemented by `radio_2055.c`. It is the shared hardware contract for BCM2055 radio initialization, calibration, and channel switching in the B43 N-PHY path.

## Important APIs, Types, And Definitions
- Register constants: `B2055_*` names map radio register addresses from `0x00` through `0xE2`, covering spare/power-down controls, RSSI, RX/TX gain controls, PLL/VCO, local generator, per-core RX/TX baseband and RF blocks, calibration, power detector, GPIO-like/spare areas, and programmed gain-control entries.
- `struct b43_nphy_channeltab_entry_rev2`: channel switch row with channel number, frequency, an unknown field, 22 radio-register values, and `struct b43_phy_n_sfo_cfg phy_regs`.
- `b2055_upload_inittab(struct b43_wldev *dev, bool ghz5, bool ignore_uploadflag)`: uploads default BCM2055 register values for the selected band, optionally ignoring the upload flags.
- `b43_nphy_get_chantabent_rev2(struct b43_wldev *dev, u8 channel)`: returns an immutable channel-table entry for an N-PHY channel or `NULL`.

## Control Flow And State
The header has no executable control flow. It shapes the runtime behavior in `radio_2055.c` and `phy_n.c`: channel switching obtains a `struct b43_nphy_channeltab_entry_rev2`, then writes the radio fields to the register constants declared here and uses `phy_regs` for N-PHY bandwidth/SFO programming. Initialization calls the upload helper to program band-specific defaults. There is no software persistence in the header itself.

## Dependencies And Integration Points
- Includes `<linux/types.h>` and `tables_nphy.h` for `struct b43_phy_n_sfo_cfg`.
- `radio_2055.c` uses these constants as table indices and write targets.
- `phy_n.c` uses many `B2055_*` names directly for channel setup, radio calibration, RSSI calibration, TX/RX IQ calibration, power-detector configuration, and workaround logic.
- The register constants must remain consistent with any vendor radio documentation or reverse-engineered tables used by the driver.

## Risks
- Register address mistakes are high-impact and can cause band-specific radio failure, calibration failure, or out-of-spec transmission.
- The channel-entry struct layout must stay aligned with `RADIOREGS()` and `PHYREGS()` initializers in `radio_2055.c`. Reordering fields without updating initializers would silently program wrong registers.
- The `unk2` field is undocumented; its consumers and meaning should be verified before changing it.
- This header is specific to BCM2055. Mixing constants with BCM2056 or later radio code would misprogram hardware.

## Test Signals
- Compile N-PHY/BCM2055 paths after any struct or macro change to catch initializer mismatches.
- Runtime tests should cover radio init, channel switching, calibration, and traffic on hardware known to use BCM2055.
- Register trace comparisons against known-good channel-switch sequences are the strongest signal for table or register-map changes.
