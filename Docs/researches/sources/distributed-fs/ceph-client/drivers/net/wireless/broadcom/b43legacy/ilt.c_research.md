# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/ilt.c

## Purpose
Provides initial internal lookup-table data for b43legacy PHY/radio calibration and helper functions to read/write device ILT entries. Tables include rotor, retard, fine-frequency, noise, noise-scale, and sigma-square values used by PHY calibration code.

## Important APIs, Types, and Functions
Exports constant arrays declared in `ilt.h`: `b43legacy_ilt_rotor`, `b43legacy_ilt_retard`, `b43legacy_ilt_finefreqa`, `b43legacy_ilt_finefreqg`, `b43legacy_ilt_noisea2`, `b43legacy_ilt_noisea3`, `b43legacy_ilt_noiseg1`, `b43legacy_ilt_noiseg2`, `b43legacy_ilt_noisescaleg1/2/3`, and `b43legacy_ilt_sigmasqr1/2`. Public helpers are `b43legacy_ilt_write`, `b43legacy_ilt_write32`, and `b43legacy_ilt_read`.

## Control Flow
Most of the file is static calibration data. Access helpers write the target offset to `B43legacy_PHY_ILT_G_CTRL`, then write low and optionally high data words to `B43legacy_PHY_ILT_G_DATA1` and `B43legacy_PHY_ILT_G_DATA2`; reads set the control offset and read data word 1. Higher-level PHY code is responsible for iterating tables and choosing offsets.

## State and Persistence
The arrays are immutable kernel data. The helpers mutate hardware PHY ILT registers, which persist in device state until reset or overwritten. No kernel-side dynamic state is owned here.

## Dependencies and Integration Points
Depends on `b43legacy.h`, `ilt.h`, and `phy.h` for register constants and PHY read/write helpers. It integrates with G/B PHY initialization, noise calculations, LO calibration, and interference mitigation in the broader b43legacy PHY subsystem.

## Risks
Table values are hardware magic constants; accidental edits may degrade RF behavior without compile-time errors. `b43legacy_ilt_write32` writes high word before low word, matching expected register semantics. Callers must serialize PHY access according to the driver locking policy.

## Test Signals
Hardware initialization that reaches `b43legacy_phy_init`, stable RSSI/noise readings, successful calibration, and no PHY TX error storm after init are practical signals. Table-size macros should match array initializers at compile time.
