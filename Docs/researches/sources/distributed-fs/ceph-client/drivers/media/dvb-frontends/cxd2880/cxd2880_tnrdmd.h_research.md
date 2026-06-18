# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd.h

## Purpose
Defines the main CXD2880 tuner-demodulator control interface, state container, configuration IDs, interrupt masks, diversity modes, TS output modes, GPIO modes, and public control prototypes.

## Important APIs, Types, and Functions
Key enums include chip IDs, state, diversity mode, clock mode, TS output interface, crystal sharing, spectrum sense, config IDs, lock result, GPIO modes, and serial TS clock. Structures model saved config entries, PID filters, LNA thresholds, create parameters, diversity create parameters, and `struct cxd2880_tnrdmd`. It also defines `slvt_unfreeze_reg()` and interrupt bit masks. Prototypes mirror the core implementation.

## Control Flow
No executable flow except the `slvt_unfreeze_reg` macro performing a register write. Function declarations define the valid lifecycle: create, init, configure, tune, monitor lock, sleep, and auxiliary GPIO/interrupt/TS operations.

## State and Persistence
`struct cxd2880_tnrdmd` is the persistent per-instance state object for the driver lifetime. It records current active tuning state and saved configuration that is replayed during hardware transitions.

## Dependencies and Integration Points
Includes common, IO, DTV, DVB-T, and DVB-T2 definitions. It is the common contract consumed by all mode-specific and monitor files plus top-level frontend glue.

## Risks and Edge Cases
The unfreeze macro ignores write errors. Public mutable fields make invariants dependent on disciplined internal use. Config IDs have broad hardware effects, and some are only valid in sleep or specific TS output modes.

## Test Signals
Compile all consumers after any struct/enum change, ABI-like checks for top-level frontend assumptions, and runtime state transition tests verifying fields update consistently.
