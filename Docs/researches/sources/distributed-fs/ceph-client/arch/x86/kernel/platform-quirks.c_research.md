# sources/distributed-fs/ceph-client/arch/x86/kernel/platform-quirks.c

## Purpose
Initializes broad x86 legacy platform feature expectations before later boot code probes devices. It distinguishes PC, Xen, Intel MID, and CE4100 subarchitectures.

## APIs, Types, And Functions
Exports no symbols. Main functions are `x86_early_init_platform_quirks()`, `x86_pnpbios_disabled()`, and, under `CONFIG_PNPBIOS`, `arch_pnpbios_disabled()`.

## Control Flow
`x86_early_init_platform_quirks()` sets conservative defaults: i8042 expected, RTC present, warm reset supported, BIOS region reservation disabled, and PNPBIOS enabled. It then switches on `boot_params.hdr.hardware_subarch`: PC enables BIOS region reservation; Xen disables PNPBIOS and RTC; Intel MID and CE4100 disable PNPBIOS, RTC, and i8042. A platform override hook may then adjust the features.

## State And Persistence
State persists in the global `x86_platform.legacy` feature structure, which later init paths consult for RTC registration, PNPBIOS availability, keyboard controller expectations, warm reset, and BIOS reservation behavior.

## Dependencies And Integration
Depends on boot parameters, `x86_platform`, BIOS EBDA setup, and PNPBIOS. It feeds `setup.c`, `rtc.c`, and platform-specific x86 init logic.

## Risks And Test Signals
Incorrect subarch classification can probe nonexistent legacy devices or skip real ones. Test signals are boot behavior on PC, Xen PV/HVM, Intel MID, and CE4100 platforms, plus absence of spurious RTC/i8042/PNPBIOS probes where disabled.
