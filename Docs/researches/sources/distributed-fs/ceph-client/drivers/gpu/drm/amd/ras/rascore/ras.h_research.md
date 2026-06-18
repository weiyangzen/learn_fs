# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras.h

## Purpose

`ras.h` is the central rascore public header. It defines RAS block/error/event/status enums, system callback interfaces, configuration structures, `ras_core_context`, and the exported rascore lifecycle and service APIs.

## Important APIs, Types, And Functions

Important enums include GPU health/status, firmware feature flags, RAS block IDs, ECC error types, sequence-number types/FIFOs, notify events, GPU status bits, and firmware EEPROM commands. Callback tables include `ras_mp1_sys_func`, `ras_eeprom_sys_func`, `ras_nbio_sys_func`, `ras_psp_sys_func`, and `ras_sys_func`. State/config types include `ras_ecc_count`, `ras_bank_ecc`, submodule configs, `ras_core_config`, and `ras_core_context`. Public APIs cover create/destroy, SW/HW init/fini, readiness, seqno generation/FIFO access, ECC update/query, GPU status helpers, IRQ/fatal handling, NPS, block names, timestamp conversion, status enablement, address translation, GPU memory, reset locks, event notifications, device info, and NPS page conversion.

## Control Flow, State, And Persistence

The header defines the rascore state machine. `ras_core_context` owns config, ACA, EEPROM and firmware EEPROM controls, PSP/UMC/NBIO/GFX/MP1/process/command/log-ring modules, system callbacks, poison support, RMA/initialized/enabled flags, sequence FIFOs with spinlock, and firmware feature bits. Persistent RAS data includes EEPROM bad pages, log-ring records, sequence state, bad-page retirement state, and submodule ECC counters.

## Dependencies And Integration Points

It includes rascore submodule headers and is used by manager code, command handlers, ACA parsers, EEPROM/UMC/PSP modules, and system adapter headers. It is the generic interface boundary between rascore and AMDGPU-specific plumbing.

## Risks And Test Signals

Risks include circular includes, ABI-like struct drift for command/log users, enum ID mismatches with TA firmware, race-prone seqno FIFOs, and callback tables not fully populated. Test signals include rascore lifecycle tests, all submodule init/fini ordering, command interface ABI validation, ECC query/update paths, reset lock correctness, and firmware EEPROM feature negotiation.
