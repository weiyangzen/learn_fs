# sources/distributed-fs/ceph-client/security/yama/Kconfig

## Purpose

This Kconfig entry declares `SECURITY_YAMA`, the build option for the Yama Linux Security Module. Yama adds system-wide DAC-hardening controls, currently focused on ptrace restrictions, and is stackable with other LSMs.

## Important APIs, types, and functions

The file defines a single boolean config symbol, `SECURITY_YAMA`, depending on `SECURITY` and defaulting to `n`. Its help text points administrators to `Documentation/admin-guide/LSM/Yama.rst`.

## Control Flow

There is no runtime control flow. The Kconfig symbol controls whether `security/yama/Makefile` builds `yama.o` and whether Yama registration code is available to the LSM framework.

## State and Persistence

The selected value persists in the kernel `.config`. Runtime state such as `ptrace_scope` is implemented in `yama_lsm.c`, not here.

## Dependencies and Integration Points

It integrates with the kernel security menu and requires the general `SECURITY` infrastructure. It is consumed by the Yama Makefile.

## Risks and Test Signals

Risks are configuration-level: missing `SECURITY` disables Yama, and default `n` means it is absent unless selected. Test signals are Kconfig dependency checks and build matrix coverage with Yama enabled and disabled.
