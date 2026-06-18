<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb.h

## Purpose
This header defines the table format and helper macros for Broadcom STB pinctrl drivers, especially BCM2712 in this subset. It lets data files describe mux bit positions, pad pull bit positions, GPIO and AON pin descriptors, per-pin alternate functions, and probe match data.

## Important APIs, Types, And Functions
`BRCMSTB_FUNC()` maps enum function identifiers to names. `MUX_BIT()`, `PAD_BIT()`, `GPIO_REGS()`, `EMMC_REGS()`, `AON_GPIO_REGS()`, and `AON_SGPIO_REGS()` encode mux and pad register/shift values into compact `struct pin_regs` entries. `GPIO_PIN()`, `AON_GPIO_PIN()`, and `AON_SGPIO_PIN()` build pin descriptors. `struct brcmstb_pin_funcs` describes each pin's fsel mask, function array, and function count. `struct brcmstb_pdata` packages all SoC data consumed by `brcmstb_pinctrl_probe()`.

## Control Flow
SoC data files include this header to construct static tables. At probe, the OF match `.data` points to `struct brcmstb_pdata`, and the common core interprets the encoded mux/pad fields for reads and writes.

## State And Persistence
The header stores no runtime state. It defines immutable metadata structures that determine how hardware state is accessed by the common core.

## Dependencies And Integration Points
Depends on Linux type definitions, platform device declarations, and pinctrl pin descriptor macros. It is the local interface between brcmstb data files and the shared brcmstb implementation.

## Risks
The bit encoding macros are compact and easy to misuse: shifts are scaled to hardware field positions, `MUX_BIT_VALID` distinguishes no-mux pins from register bit zero, and `PAD_BIT_INVALID` marks pins without pull control. Any mismatch corrupts the common core's register math.

## Test Signals
Compile all brcmstb users and validate debugfs/function output. Runtime tests should cover pins with mux and pad bits, eMMC pads with no mux bit, and AON SGPIO pins with invalid pad bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-brcmstb.h -->
