# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/powerflags.c

## Purpose

This file is a data-only lookup table for x86 CPU power-management feature names. It intentionally contains no executable code and feeds human-readable power-management strings into `/proc/cpuinfo`.

## Important APIs, Types, And Functions

The single exported datum is `const char *const x86_power_flags[32]`. Entries map bit positions in `struct cpuinfo_x86::x86_power` to strings such as `ts`, `fid`, `vid`, `tm`, `hwpstate`, `cpb`, `eff_freq_ro`, `proc_feedback`, and `acc_power`. Empty entries suppress output for bits intentionally mapped elsewhere, such as invariant TSC.

## Control Flow

There is no control flow in this file. Consumers index the array while rendering CPU information and skip null or empty names according to their own rules.

## State, Dependencies, And Integration

The table is immutable static kernel data. It depends on `asm/cpufeature.h` for the associated feature definitions and integrates mainly with `proc.c` when printing `power management:` in `/proc/cpuinfo`.

## Risks And Test Signals

Risk is mostly ABI/user-visible naming drift. Adding, moving, or removing entries changes `/proc/cpuinfo` output and can affect scripts that parse power flags. Test by building x86 CPU code and comparing `/proc/cpuinfo` power-management output on CPUs with the relevant bits set.
