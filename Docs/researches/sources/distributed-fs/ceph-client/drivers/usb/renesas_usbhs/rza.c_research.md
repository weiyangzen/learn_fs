<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza.c

## Purpose
RZ/A1 USBHS hardware initialization and platform information.

## Important APIs, Types, And Functions
`usbhs_rza1_hardware_init()` looks up `usb_x1` and `extal` clock nodes, reads `clock-frequency`, selects 12 MHz EXTAL via SYSCFG.UCKSEL when no 48 MHz USB clock is present, enables USB PLL with SYSCFG.UPLLE, waits, and sets SUSPMODE.SUSPM. `usbhs_rza1_plat_info` exports this init callback, gadget ID, and new pipe configs.

## Control Flow
Common probe calls hardware init after resets and before hotplug. Invalid clock sources return `-EIO`.

## State And Persistence
Hardware clock-source, PLL, and SUSPMODE register state; static const platform-info.

## Dependencies And Integration Points
Depends on OF node lookup by `"usb_x1"` and `"extal"`, common register helpers, and RZ/A-compatible match entries.

## Risks
Global node-name lookup is fragile. Missing clock nodes can default to zero and force fallback validation. Role is fixed to gadget. RZ/A2 and RZ/G2L symbols are declared in `rza.h` but defined in `rza2.c`.

## Test Signals
48 MHz USB clock, 12 MHz EXTAL fallback, invalid/missing clocks, PLL/SUSPMODE effects, and probe failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza.c -->
