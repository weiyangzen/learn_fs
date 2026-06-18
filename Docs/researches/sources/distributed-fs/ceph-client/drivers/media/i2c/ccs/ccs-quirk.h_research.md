# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-quirk.h

## Purpose
`ccs-quirk.h` defines the quirk callback interface for sensor modules that need behavior outside the generic CCS/SMIA path.

## Important APIs, Types, and Functions
`struct ccs_quirk` contains optional callbacks for `limits`, `post_poweron`, `pre_streamon`, `post_streamoff`, `pll_flags`, `init`, and `reg_access`, plus quirk flags. `CCS_QUIRK_FLAG_8BIT_READ_ONLY` alters read access. `struct ccs_reg_8` and `CCS_MK_QUIRK_REG_8()` support compact register-write tables. `ccs_call_quirk()` and `ccs_needs_quirk()` are the main dispatch helpers.

## Control Flow
Core code stores a selected quirk pointer in `sensor->minfo.quirk`. Call sites use `ccs_call_quirk()` to run a callback only when present. Register access quirks can rewrite the register/value, handle a read/write completely by returning `-ENOIOCTLCMD`, or return an error.

## State and Persistence Behavior
The header declares behavior only. Quirk callbacks can mutate cached limits, PLL flags, controls, and hardware registers, but no state is stored in this header.

## Dependencies and Integration Points
It forward-declares `struct ccs_sensor` and exports quirk objects implemented in `ccs-quirk.c`. It is included by `ccs.h`, making quirk support available to core and register-access layers.

## Risks and Edge Cases
The `reg_access` callback has broad authority and must preserve register width/value semantics. Returning `-ENOIOCTLCMD` means the core treats access as handled, with default read value zero for reads. Flag and callback semantics must remain synchronized with `ccs-reg-access.c`.

## Test Signals
Exercise devices with and without quirks, register-access quirks that redirect/suppress reads and writes, 8-bit-read-only behavior, and each lifecycle hook under probe, power cycle, stream on, and stream off.
