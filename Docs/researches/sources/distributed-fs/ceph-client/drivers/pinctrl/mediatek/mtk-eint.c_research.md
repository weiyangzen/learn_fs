# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/mtk-eint.c

Purpose: Implements the reusable MediaTek external interrupt controller library used by multiple pinctrl drivers. It creates an irqdomain for EINT lines, translates EINTs to GPIOs through pinctrl callbacks, handles masking/type/wake/debounce, and dispatches chained parent IRQs.

Important APIs/types/functions: Public exports are `mtk_eint_do_init()`, `mtk_eint_do_suspend()`, `mtk_eint_do_resume()`, `mtk_eint_set_debounce()`, `mtk_eint_find_irq()`, and debounce tables for several SoCs. Core internals include `mtk_eint_irq_chip`, `mtk_eint_irq_handler()`, `mtk_eint_set_type()`, `mtk_eint_flip_edge()`, `mtk_eint_chip_write_mask()`, and `mtk_eint_hw_init()`.

Control flow: Initialization fills default register offsets, allocates per-instance pin lists plus wake/current masks, creates a linear irqdomain, initializes hardware by enabling AP domain and masking all EINTs, maps each EINT to a Linux IRQ, installs `handle_level_irq`, and attaches a chained parent handler. IRQ handling walks each instance and port status register, maps the status bit back to an EINT number, optionally masks wake-only lines, dispatches `generic_handle_domain_irq()`, emulates dual-edge by flipping polarity and raising a software interrupt if a transition was missed, and resets debounce counters.

State and persistence: Runtime state lives in `struct mtk_eint`: MMIO bases, pin metadata, irqdomain, parent IRQ, per-instance `pin_list`, `wake_mask`, `cur_mask`, debounce table count, register layout, and GPIO translation hooks. Suspend writes wake masks into hardware; resume restores current masks. Debounce configuration persists in EINT debounce registers.

Dependencies and integration points: Uses Linux irqdomain/chained IRQ/GPIO APIs and `struct mtk_eint_xt` callbacks supplied by pinctrl implementations. SoC drivers provide `mtk_eint_hw` sizing and optional explicit `mtk_eint_pin` maps.

Risks: Dual-edge emulation depends on stable GPIO reads while polarity is flipped. `mtk_eint_set_debounce()` assumes an existing IRQ mapping and valid irq_data; invalid EINT numbers or unmapped lines can be hazardous. Wake/current mask semantics are inverted through `mask_set`/`mask_clr`, so regressions easily break suspend wake. The optional explicit pin map must not exceed `nbase` and must have indexes that fit allocated `pin_list` arrays.

Test signals: GPIO-to-IRQ conversion, rising/falling/both-edge interrupts, level-high/low interrupts, wake from suspend, debounce programming with each SoC table, invalid type rejection, wake-only interrupt masking, and stress tests around fast edge changes that exercise software re-triggering.
