# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_tcc_cooling.c

## Purpose

`intel_tcc_cooling.c` registers a thermal cooling device that throttles processors by programming the TCC offset register through the Intel TCC library.

## Important APIs, Types, and Functions

The cooling callbacks are `tcc_get_max_state()`, `tcc_get_cur_state()`, and `tcc_set_cur_state()`, which map state directly to TCC offset degrees. `tcc_cooling_init()` checks supported CPU IDs, platform programmability bit, temperature target MSR, lock bit, and registers cooling device `TCC Offset`.

## Control Flow

Module init is gated by CPU model, `MSR_PLATFORM_INFO` bit 30, and `MSR_IA32_TEMPERATURE_TARGET` lock bit. On success, thermal governors can set cooling state; set calls `intel_tcc_set_offset(-1, state)`. Exit unregisters the cooling device.

## State and Persistence Behavior

Only the global cooling-device pointer is stored. Hardware TCC offset persists in the MSR until another component changes it or reset occurs.

## Dependencies and Integration Points

It depends on the Intel TCC namespace, thermal cooling device framework, x86 CPU matching, and MSR helpers. Thermal zones may bind it as an active cooling device.

## Risks and Test Signals

Risks include direct global TCC offset changes affecting all CPUs, CPU model whitelist maintenance, lock/prog bit mismatch, and no saved/restore of previous offset. Test signals include init gating, cooling max/current/set callbacks, governor binding, lock-bit rejection, and module unload.
