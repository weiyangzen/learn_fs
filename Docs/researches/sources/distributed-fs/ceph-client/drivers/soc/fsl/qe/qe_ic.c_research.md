# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_ic.c

## Purpose
Implements the main QUICC Engine interrupt controller as a Linux irq_domain with cascaded high and low parent IRQ handlers.

## Important APIs, types, and functions
`struct qe_ic` stores mapped registers, irq_domain, irq_chip, and parent high/low virqs. `struct qe_ic_info` maps hardware source numbers to mask bits, mask registers, priority code, and priority register. `qe_ic_unmask_irq`, `qe_ic_mask_irq`, and `qe_ic_irq_chip` implement the child irq_chip. Domain operations are `qe_ic_host_match`, `qe_ic_host_map`, and `irq_domain_xlate_onetwocell`. Cascade handlers are `qe_ic_cascade_low`, `qe_ic_cascade_high`, and `qe_ic_cascade_muxed_mpic`.

## Control flow and state behavior
Probe maps the controller registers, copies the base irq_chip, obtains low and optional high parent IRQs, creates a 64-entry linear domain, clears CICR, and installs chained handlers. Child IRQ mask/unmask operations update either `QEIC_CIMR` or `QEIC_CRIMR` under `qe_ic_lock`; masking uses `mb()` before re-enabling interrupts to reduce spurious interrupts. Cascaded handlers read `CIVEC` or `CHIVEC`, translate the six-bit source through the domain, call `generic_handle_irq`, and EOI the parent chip.

## Dependencies and integration points
Registers as a platform driver for `"fsl,qe-ic"` or type `"qeic"` at `subsys_initcall`. It integrates device-tree interrupt specifiers with Linux irq_domain and parent interrupt controllers such as MPIC.

## Risks and test signals
Only sources with nonzero `qe_ic_info[hw].mask` can map; reserved IRQs fail. The muxed cascade path calls parent `irq_eoi` unconditionally, while the separate low/high handlers check for it. Test signals include successful mapping of valid sources, rejection of reserved sources, correct interrupt delivery through high and low vectors, and lack of interrupt storms after masking.
