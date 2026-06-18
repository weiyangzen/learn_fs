<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts5500.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts5500.c

Purpose: supports Technologic Systems TS-5500/TS-5600 DIO blocks and LCD-as-DIO blocks using legacy x86 I/O ports, with per-block pinout tables and limited hardware IRQ routing.

Important APIs, types, and functions: `struct ts5500_dio` describes each line's value port, control port, direction capability, and optional IRQ. `struct ts5500_priv` stores the pinout, gpiochip, spinlock, strap mode, and hardware IRQ. GPIO callbacks are input, output, get, set, and `to_irq()`. `ts5500_enable_irq()` and `ts5500_disable_irq()` toggle board-specific IRQ enable bits.

Control flow: probe selects a pinout from platform ID, requests the relevant I/O port regions, arbitrates shared port `0x7d` with global `hex7d_reserved`, forces LCD mode when needed, registers the gpiochip, and enables the block's hardware IRQ. Direction and value operations use locked `inb()`/`outb()` read-modify-write cycles. Remove disables the IRQ enable bit.

State and persistence behavior: no per-line software value cache. Hardware port registers hold direction and values. Global `hex7d_reserved` persists across device instances and prevents duplicate region requests.

Dependencies and integration points: depends on platform IDs, legacy I/O port resources, board wiring tables, gpiolib, and fixed ISA IRQ numbers.

Risks and test signals: `hex7d_reserved` is never cleared on remove, so unload/rebind behavior can differ. IRQs are not represented as a modern irqdomain; `to_irq()` returns fixed hardware IRQs or strapped IRQs. Test all block IDs, shared 0x7d ordering, input-only/output-only rejection, LCD DIO mode, IRQ enable/disable bits, and multi-instance probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts5500.c -->
