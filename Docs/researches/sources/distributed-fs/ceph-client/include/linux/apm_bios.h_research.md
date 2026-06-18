# sources/distributed-fs/ceph-client/include/linux/apm_bios.h

## Purpose
Defines kernel-side APM BIOS constants, persistent APM information, BIOS function codes, and device selection helpers.

## Important APIs, Types, And Functions
The header imports the UAPI APM definitions, defines segment selectors `APM_CS`, `APM_CS_16`, and `APM_DS`, installation flags such as `APM_16_BIT_SUPPORT`, and BIOS function constants from `APM_FUNC_INST_CHECK` through timer/ring operations. `struct apm_info` stores BIOS information and persistent driver policy flags. Global `apm_info` is declared, and `APM_DEVICE_BALL` selects all-device IDs based on connection version.

## Control Flow, State, And Persistence
`struct apm_info` is explicitly persistent across APM module unload/load, carrying BIOS metadata and quirk flags. Control flow using this header is low-level BIOS-call orchestration in architecture APM code.

## Dependencies And Integration Points
Depends on `uapi/linux/apm_bios.h` and architecture GDT definitions. Integrated with x86 APM setup, power-off, idle, suspend/resume, and legacy userspace APM interfaces.

## Risks And Test Signals
Incorrect function codes or segment assumptions can break BIOS calls on legacy systems. Risks also include stale persistent quirk flags after reload. Tests are legacy-platform focused: APM detection, power status calls, suspend/resume events, power-off behavior, and module reload persistence.
