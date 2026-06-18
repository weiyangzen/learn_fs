# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smtdef.c

## Purpose
`smtdef.c` centralizes default SMT/CMT configuration and MIB initialization for the SysKonnect FDDI stack. It seeds station, MAC, path, and port attributes, operational timer values, policy defaults, link error thresholds, and MAC operational values used by later SMT initialization and state machines.

## Important APIs and Functions
The public functions are `smt_reset_defaults()`, `smt_set_mac_opvalues()`, and `smt_fixup_mib()`. Internal helpers are `smt_init_mib()` and `set_min_max()`. Compile-time constants define microsecond/millisecond/second defaults for PCM, ECM, RMT, MAC, LCT, LEM, polling, and path-test behavior.

## Control Flow
`smt_reset_defaults()` calls `smt_init_mib()`, records `SMC_VERSION`, initializes token emulation timestamps from `smt_get_time()`, and sets the `smc->s` configuration block for DAS defaults, number of PHYs, PCM timers, ECM timers, RMT timers, MAC limits, and LCT thresholds. Optional ESS/SBA/TAG_MODE sections reset feature-specific state at cold-start or reset level.

`smt_init_mib()` zeroes the non-OS/non-hardware portion of `struct s_smc` on level 0, or clears selected transient SMT flags on later resets. It then fills station version/manufacturer/user data, station policies, available paths, notification/report settings, MAC indexes and timers, path bounds, and port attributes. It deliberately leaves PHY MIB pointers for `init_smt()` phase two and ends by applying MAC operational values.

`smt_set_mac_opvalues()` reconciles requested MIB values with path lower bounds using two's-complement FDDI timer representations, emits an AIX remote T-Req event when T-Req changes, and returns whether any operational value changed. `smt_fixup_mib()` finalizes master/non-master counts after the SAS/DAS/NAC mode is known.

## State, Dependencies, and Integration
The file persists defaults into `smc->mib`, `smc->s`, `smc->sm.last_tok_time[]`, optional `smc->ess`, and optional hardware tag fields. It is called by `skfddi.c` during driver initialization and reset, and by `smtinit.c` before hardware/state-machine startup. It depends on FDDI MIB layouts and event macros such as `AIX_EVENT()`.

## Risks and Test Signals
The main risk is reset-level semantics: level 0 wipes most of `struct s_smc`, while later levels preserve selected state. Timer values are negative two's-complement BCLK values, so boundary comparisons are easy to regress. Tests should verify cold reset versus warm reset MIB preservation, default MAC/path/port values, SAS/DAS master-count fixups, operational timer clamping, and expected T-Req change events.
