# sources/distributed-fs/ceph-client/arch/x86/kernel/io_delay.c

## Purpose
Selects and implements the delay operation used by legacy `inb_p/outb_p` style I/O, with command-line and DMI quirks for systems that cannot tolerate port `0x80`.

## Important APIs And State
Exports `native_io_delay()` and global `io_delay_type`. Defines delay modes `0x80`, `0xed`, `udelay`, and `none`; `io_delay_override`; DMI quirk callback `dmi_io_delay_0xed_port()`; `io_delay_init()`; and early parameter parser `io_delay_param()`.

## Control Flow And Persistence
At boot the default mode is selected by Kconfig. `io_delay=` can force a mode and suppress DMI override. Without override, `io_delay_init()` scans known affected HP/Compaq/Quanta systems and switches from `0x80` to `0xed`. `native_io_delay()` performs the selected outb, a calibrated-ish `udelay(2)`, or nothing.

## Dependencies And Integration Points
Used by native/paravirt I/O delay paths and legacy port I/O helpers. Depends on DMI, early params, Kconfig defaults, and low-level port I/O.

## Risks And Test Signals
Risks include lockups from port `0x80`, inadequate delay timing before calibration, and removing bus side effects by using `udelay` or `none`. Tests include booting quirked laptop DMI profiles, `io_delay=` modes, legacy ISA/PIC/PIT access stability, and no regressions in paravirt native delay assumptions.
