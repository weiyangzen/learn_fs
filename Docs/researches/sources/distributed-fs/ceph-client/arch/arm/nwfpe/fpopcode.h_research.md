# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpopcode.h

## Purpose
Documents and encodes the FPA11 instruction formats and provides opcode masks, tests, field extractors, condition-code constants, rounding decoders, and constant accessors for the emulator.

## Important APIs, Types, And Functions
Defines CPDT, CPDO, CPRT masks and opcode constants; transfer flags such as `BIT_PREINDEX`, `BIT_UP`, `BIT_WRITE_BACK`, `BIT_LOAD`; arithmetic codes like `ADF_CODE`, `MUF_CODE`, `MVF_CODE`, `SQT_CODE`; CPRT codes like `FLT_CODE`, `FIX_CODE`, `WFS_CODE`, `CMF_CODE`; field getters `getRn`, `getFd`, `getFn`, `getFm`, `getRd`; and inline decoders `getTransferLength`, `getRegisterCount`, `getRoundingPrecision`, `getDestinationSize`.

## Control Flow
No runtime stateful flow. Inline helper functions switch on masked opcode fields and return compact enum-like values consumed by emulator dispatch.

## State, Dependencies, And Integration
No writable state. Depends on `CONFIG_FPE_NWFPE_XP` for extended constants and on type tags from `fpa11.h`. Integrated across all NWFPE instruction decode paths.

## Risks And Test Signals
Risks are mask mistakes causing wrong instruction class, undefined opcodes incorrectly accepted, transfer length/count mismatch, and condition-code incompatibility. Test signals are decode unit tests or instruction suites covering every CPDT/CPDO/CPRT format and invalid encodings.
