# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbt_precomp.h

## Purpose
`halbt_precomp.h` is the common include aggregator for the rtlwifi Bluetooth coexistence implementation. It pulls in core rtlwifi headers, the coexistence output-source interface, chip-specific coexistence algorithm headers, bus-type constants, and local `BIT0` through `BIT31` definitions expected by imported Realtek coexistence code.

## Important APIs, Types, And Functions
The file defines include guards, includes `wifi.h`, `efuse.h`, `base.h`, `regd.h`, `cam.h`, `ps.h`, `pci.h`, `halbtcoutsrc.h`, and chip-specific headers for 8192E 2-antenna, 8723B 1/2-antenna, and 8821A 1/2-antenna coexistence. It defines `RT_PCI_INTERFACE`, `RT_USB_INTERFACE`, `RT_SDIO_INTERFACE`, and hard-codes `DEV_BUS_TYPE` to `RT_PCI_INTERFACE`. It also defines numeric bit masks `BIT0` through `BIT31`.

## Control Flow
There is no runtime control flow. Compile-time flow uses this header to make the imported coexistence source files see one consolidated environment of rtlwifi types, register/helper declarations, interface constants, and bit macros.

## State And Persistence
The header stores no runtime state. The selected bus constant and bit macros influence compiled coexistence logic. Runtime coexistence state lives in rtlwifi private structures and BTC-specific data structures declared in the included headers.

## Dependencies And Integration Points
It integrates the coexistence source tree with the broader rtlwifi core, including EFUSE data, base-layer helpers, regulatory/CAM/power-save state, PCI transport declarations, and chip-specific BTC algorithms. The local `BITn` macros reflect vendor-code expectations rather than the kernel `BIT()` macro style.

## Risks
The hard-coded `DEV_BUS_TYPE` as PCI is risky if shared coexistence code is reused by USB/SDIO rtlwifi variants or if logic branches on bus type. Local `BIT0`-`BIT31` definitions can collide with other headers or diverge from kernel idioms, though they are ordinary constants. As an include aggregator, adding heavy or order-sensitive headers can create circular include or compile-time coupling problems.

## Test Signals
Signals include clean builds of all `btcoexist-objs`, coexistence behavior on the chip families whose headers are included, no macro redefinition warnings, and runtime validation that bus-type-dependent coexistence decisions are correct for the actual transport.
