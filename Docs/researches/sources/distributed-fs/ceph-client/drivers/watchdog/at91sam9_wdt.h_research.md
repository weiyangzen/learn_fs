# sources/distributed-fs/ceph-client/drivers/watchdog/at91sam9_wdt.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/at91sam9_wdt.h` defines register offsets and bit fields for AT91 watchdog timer hardware used by the AT91SAM9 driver and related SAM9X60 support. The complete 61-line header was read for this report.

## Important APIs, Types, and Functions

The header defines control register `AT91_WDT_CR`, restart bit `AT91_WDT_WDRSTT`, and key `AT91_WDT_KEY`. It defines mode register `AT91_WDT_MR` and fields `AT91_WDT_WDV`, `AT91_WDT_SET_WDV()`, `AT91_WDT_WDFIEN`, `AT91_WDT_WDRSTEN`, `AT91_WDT_WDRPROC`, `AT91_WDT_WDDIS`, `AT91_WDT_WDD`, `AT91_WDT_SET_WDD()`, `AT91_WDT_WDDBGHLT`, and `AT91_WDT_WDIDLEHLT`. It also defines status register `AT91_WDT_SR` with underflow/error bits, plus SAM9X60-specific `AT91_SAM9X60_VR`, `AT91_SAM9X60_WLR`, period counter fields, and interrupt registers.

## Control Flow

No executable control flow exists. Consumers use these constants to read/write watchdog registers and construct mode values.

## State and Persistence Behavior

No storage is owned by the header. The constants describe hardware state fields that persist in MMIO registers, notably the mode register that may be write-once on AT91SAM9-class hardware.

## Dependencies and Integration Points

It includes `<linux/bits.h>` and integrates directly with `at91sam9_wdt.c`. The SAM9X60 definitions suggest shared hardware documentation for newer variants even though this source set only includes the SAM9x driver.

## Risks and Edge Cases

Incorrect bit definitions would cause irreversible watchdog mode programming mistakes. Several bits have variant-specific meanings, such as `AT91_WDT_WDFIEN` sharing bit position with `AT91_SAM9X60_WDDIS`, so users must apply the correct SoC variant semantics.

## Test Signals

Test signals are compile coverage with all AT91 watchdog users, hardware register programming review against datasheets, and runtime validation of restart, mode, status, and interrupt behavior on supported SoCs.
