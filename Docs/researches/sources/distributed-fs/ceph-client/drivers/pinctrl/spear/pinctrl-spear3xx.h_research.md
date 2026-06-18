<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear3xx.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear3xx.h

## Purpose
This header is the shared declaration layer for SPEAr3xx pinmux variants. It defines common mux bit masks, declares the common groups/functions exported by `pinctrl-spear3xx.c`, provides aggregate macros for variant group/function arrays, and exposes the shared `spear3xx_machdata`.

## Important APIs, Types, And Data
- `PMX_*_MASK` constants define bit positions in the SPEAr3xx mux control register for PWM, FIRDA, I2C, SSP, MII, GPIO0 pins, UART0, and timers.
- `SPEAR3XX_COMMON_PINGROUPS` expands to pointers to all common `struct spear_pingroup` objects.
- `SPEAR3XX_COMMON_FUNCTIONS` expands to pointers to all common `struct spear_function` objects.
- Extern declarations allow variant files to compose common and SoC-specific tables without duplicating common definitions.
- `spear3xx_machdata` is declared as the shared machine descriptor completed by each variant probe.

## Control Flow And Integration
The header has no runtime flow. Its macros are included by SPEAr300, SPEAr310, and SPEAr320 drivers when constructing their group and function arrays. It also imports `pinctrl-spear.h`, which supplies the SPEAr core data structures and helper macros.

## State And Persistence
It owns no storage. It declares shared objects whose storage lives in `pinctrl-spear3xx.c`. Hardware state is affected only when variant drivers and the common SPEAr core consume the declared masks and tables.

## Dependencies
It depends on `pinctrl-spear.h` and the exact names of common group/function symbols in `pinctrl-spear3xx.c`.

## Risks And Review Notes
- Mask definitions are a cross-file ABI. Changing a bit position affects every SPEAr3xx variant.
- Aggregate macros hide ordering and membership. New common groups must update both extern declarations and aggregate macros.
- The shared `spear3xx_machdata` declaration encourages probe-time mutation by variants; that pattern should stay synchronized with the common core expectations.

## Test Signals
Build all SPEAr3xx variant drivers after any mask or macro change. Confirm common group/function counts and names in debugfs for SPEAr300/310/320 and verify common mux bit behavior with register readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear3xx.h -->
