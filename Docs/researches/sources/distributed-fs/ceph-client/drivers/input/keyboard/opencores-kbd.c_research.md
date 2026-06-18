## sources/distributed-fs/ceph-client/drivers/input/keyboard/opencores-kbd.c

Purpose: simple platform driver for the OpenCores keyboard controller. It reads one byte per interrupt and reports key state directly.

Important APIs/types/functions: `struct opencores_kbd` stores input, mapped register address, IRQ, and 128 identity keycodes. `opencores_kbd_isr()` reads the data byte and reports low 7 bits as keycode, with bit 7 meaning release. `opencores_kbd_probe()` maps MMIO, initializes identity keymap, requests IRQ, and registers input.

Control flow: probe gets IRQ/MMIO, sets `BUS_HOST` IDs, fills keycodes 0..127, marks key bits, requests rising-edge IRQ, and registers input. Runtime IRQ reads the controller byte, reports press when bit 7 is clear and release when set, then syncs.

State/dependencies/integration: no mutable runtime state beyond input and MMIO mapping. Dependencies are platform resources, MMIO, interrupt core, and input.

Risks and test signals: the controller scancode is assumed to equal Linux `KEY_*` value, which limits layout flexibility. No `MSC_SCAN` is emitted. Test identity mapping expectations, release-bit polarity, rising-edge IRQ behavior, MMIO read side effects, and probe errors for missing IRQ/resource.
