# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpa11_cpdt.c

## Purpose
Implements FPA11 coprocessor data transfer instructions: load/store single, double, extended, and multiple-register formats between user memory and the emulator register file.

## Important APIs, Types, And Functions
Exports `PerformLDF`, `PerformSTF`, `PerformLFM`, `PerformSFM`, and `EmulateCPDT`. Internal helpers include `loadSingle`, `loadDouble`, `loadExtended`, `loadMultiple`, `storeSingle`, `storeDouble`, `storeExtended`, and `storeMultiple`.

## Control Flow
Transfer functions compute base, final, and effective addresses from `Rn`, pre/post-index, up/down, writeback, and offset fields. PC-relative base uses adjusted PC and disables writeback. Loads update register value and type tag. Stores convert from the current register type to requested transfer precision, write user memory, and raise pending rounding exceptions. Multiple-register transfers wrap Fd modulo 8 and move 3-word internal register formats.

## State, Dependencies, And Integration
State includes user memory, saved user general registers for writeback, FPA11 register values/type tags, and FPSR exception state. Dependencies are `get_user`, `put_user`, `fpmodule.inl`, endian handling, SoftFloat conversions, and opcode macros. Integrated via `EmulateAll` CPDT dispatch.

## Risks And Test Signals
Risks include unchecked `get_user`/`put_user` return handling, endian word-order mistakes, PC-relative address errors, writeback bugs, multiple-register wrap errors, and user fault behavior. Test with LDF/STF/LFM/SFM instruction suites, bad user pointers, endian builds, PC-relative transfers, and writeback cases.
