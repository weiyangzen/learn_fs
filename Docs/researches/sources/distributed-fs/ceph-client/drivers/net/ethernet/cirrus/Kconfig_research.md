# sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/Kconfig

## Purpose

This Kconfig file defines the Cirrus Ethernet vendor menu and driver options for CS89x0 ISA/platform Ethernet, EP93xx Ethernet, and Macintosh CS89x0 cards.

## Important APIs, Types, and Functions

- `NET_VENDOR_CIRRUS` is a vendor-level boolean, defaulting to `y` when platform dependencies match.
- `CS89x0` is a hidden tristate selected by the ISA and platform variants.
- `CS89x0_ISA` enables ISA CS89x0 support and selects `NETDEV_LEGACY_INIT` and `CS89x0`.
- `CS89x0_PLATFORM` enables platform-driver CS89x0 support for ARM or compile-test builds and selects `CS89x0`.
- `EP93XX_ETH` enables EP93xx SoC Ethernet and selects `MII`.
- `MAC89x0` enables Macintosh Nubus/LC-PDS CS89x0 support.

## Control Flow

When `NET_VENDOR_CIRRUS` is disabled, the nested Cirrus driver prompts are skipped. Enabling specific drivers controls which objects the directory Makefile includes. Hidden `CS89x0` is selected by concrete ISA/platform variants so shared CS89x0 code builds when either frontend is enabled.

## State and Persistence Behavior

Kconfig selections are build-time configuration state. There is no runtime state in this file.

## Dependencies and Integration Points

The file integrates with architecture symbols (`ISA`, `EISA`, `ARM`, `MAC`, `ARCH_EP93XX`, `COMPILE_TEST`), I/O port support (`HAS_IOPORT_MAP`), legacy netdev init, and MII support. Help text points users to the CS89x0 documentation.

## Risks and Edge Cases

- `CS89x0_ISA` depends on `CS89x0_PLATFORM=n`, making the ISA and platform variants mutually exclusive in that direction.
- Architecture dependencies intentionally exclude PPC32 for ISA and PPC for ARM compile-test platform support.
- Hidden `CS89x0` has no prompt; it must only be selected by valid frontends.

## Test Signals

Run Kconfig matrix checks for ISA, ARM, MAC, EP93XX, and COMPILE_TEST builds. Verify the expected object files appear for each selected option and that mutual exclusion between ISA and platform CS89x0 behaves as intended.
