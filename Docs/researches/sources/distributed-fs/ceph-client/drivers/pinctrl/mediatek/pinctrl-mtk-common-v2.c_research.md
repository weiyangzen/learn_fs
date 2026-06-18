# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common-v2.c

## Purpose
`pinctrl-mtk-common-v2.c` is a shared library for newer MediaTek pinctrl drivers. It provides register-field lookup, locked read/modify/write, GPIO-to-EINT translation hooks, EINT construction, bias helpers for multiple MediaTek pull-register designs, drive-strength helpers, advanced pull/drive helpers, and exported symbols consumed by Paris/v2 SoC drivers.

## Important APIs, Types, And Functions
- `mtk_rmw()` performs spinlock-protected read/modify/write on a selected MMIO base and register offset.
- `mtk_hw_pin_field_lookup()` and `mtk_hw_pin_field_get()` translate a pin descriptor plus logical register field enum into `struct mtk_pin_field` using SoC-provided range tables.
- `mtk_hw_set_value()` and `mtk_hw_get_value()` are exported generic field accessors and handle both single-register and cross-register bitfields.
- `mtk_is_virt_gpio()` and `mtk_xt_*` callbacks connect the generic `mtk-eint` core to GPIO/pin state, including virtual EINTs.
- `mtk_build_eint()` allocates and initializes the EINT controller object from device-tree register resources and IRQs.
- Bias helpers cover revision 0 PU/PD, revision 1 PULLEN/PULLSEL, PU/PD, pulldown-only, PUPD/R0/R1, RSEL, and PU/PD+RSEL combinations.
- Drive helpers cover old E4/E8 encoding, revision 1 `DRV`, raw `DRV`, advanced pull via R0/R1/PUPD, and advanced drive via bit fields or raw `DRV_ADV`.

## Control Flow
Runtime SoC drivers pass `struct mtk_pin_soc` tables to a higher-level v2/Paris probe. Pinmux or pinconf operations call exported helpers with a pin descriptor and logical field. The helper validates the enum, finds the relevant range, computes base index, offset, bit position, mask, and cross-register continuation, then applies a locked write or relaxed read. Bias combo setters choose the supported pull model from `soc->pull_type[pin]` or try all known types. EINT setup maps extra EINT register bases after the pinctrl base names and registers GPIO translation callbacks with `mtk_eint_do_init()`.

## State And Persistence
The file maintains no global mutable state. Runtime state is in `struct mtk_pinctrl`: MMIO base pointers, base count, device pointer, GPIO chip, EINT pointer, group arrays, lock, and `rsel_si_unit` interpretation flag. Hardware register writes persist in the SoC pin controller until reset or reconfiguration.

## Dependencies And Integration Points
The code integrates with Linux MMIO accessors, spinlocks, platform devices, OF address/IRQ parsing, gpiolib, and `mtk-eint`. It relies on SoC files to provide sorted register ranges, valid base-name counts, pin descriptors, pull-type tables, RSEL maps, drive group indexes, and EINT pin maps. It exports functions under GPL for other MediaTek pinctrl modules.

## Risks
Binary search assumes sorted non-overlapping ranges. `pfd->mask = (1 << c->x_bits) - 1` is unsafe for future 32-bit-wide fields. `mtk_pinconf_adv_pull_set()` returns `0` when R0 or R1 writes fail, masking partial programming. `mtk_rsel_get_si_unit()` returns success even if no matching RSEL index is found. EINT base counting assumes DT `reg-names` lists pinctrl bases first, then EINT bases.

## Test Signals
Cover field lookup for first, last, fixed, and cross-register fields in each SoC table. Exercise bias combo paths for all pull models, advanced pull and drive get/set round trips, EINT enabled/disabled probe paths, and concurrent GPIO/pinconf stress for `mtk_rmw()` serialization.
