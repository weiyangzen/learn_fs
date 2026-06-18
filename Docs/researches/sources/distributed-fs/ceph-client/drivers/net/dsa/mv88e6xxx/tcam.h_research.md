# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcam.h

## Purpose
Declares TCAM match layout constants, destination port vector action modes, public TCAM entry APIs, and helper macros for filling byte-oriented match data.

## Important APIs, Types, and Functions
Defines `PAGE0_MATCH_SIZE`, `PAGE1_MATCH_SIZE`, `DPV_MODE_*`, `mv88e6xxx_tcam_entry_add`, `mv88e6xxx_tcam_entry_del`, `mv88e6xxx_tcam_entry_find`, and the `mv88e6xxx_tcam_match_set` macro. The inline `__mv88e6xxx_tcam_match_set` copies data and mask bytes into `struct mv88e6xxx_tcam_key`.

## Control Flow and State
Runtime logic is limited to copying match bytes. `BUILD_BUG_ON` in the macro enforces compile-time bounds when offsets and data sizes are constant. Persistent rule state lives in `struct mv88e6xxx_tcam_entry` and `chip->tcam.entries`, defined elsewhere.

## Dependencies and Integration Points
Requires chip/tcam structures from `chip.h` through includers. Used by `tcflower.c` to map flow dissector fields into TCAM frame offsets, and by `tcam.c` for entry management.

## Risks and Test Signals
Risks include incorrect offsets or endian treatment by callers, non-constant offsets weakening `BUILD_BUG_ON`, and match-size assumptions drifting from hardware. Test signals include compile checks for match bounds, tc flower add tests for each supported key, and packet-level validation of exact/masked matches.
