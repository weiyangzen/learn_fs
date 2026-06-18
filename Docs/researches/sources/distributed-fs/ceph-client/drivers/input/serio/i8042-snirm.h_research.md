<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-snirm.h -->
# sources/distributed-fs/ceph-client/drivers/input/serio/i8042-snirm.h

## Purpose
`i8042-snirm.h` is the SNI RM low-level backend for `i8042.c`. It maps the controller through an MMIO base chosen by SNI board type and supplies board-specific IRQ numbers.

## Important APIs, types, and functions
- Static globals `i8042_kbd_irq`, `i8042_aux_irq`, and `kbd_iobase` back the generic IRQ and register macros.
- Register macros use offsets `0x60` and `0x64` from `kbd_iobase`.
- Inline accessors use `readb()`/`writeb()` for MMIO access.
- `i8042_platform_init()` checks `sni_brd_type`: RM200 maps `0x16000000` and uses IRQs 33/44; other boards map `0x14000000` and use IRQs 1/12.
- `i8042_platform_exit()` is empty.

## Control flow
With `CONFIG_SNI_RM`, platform init maps the controller base and sets IRQs before generic i8042 probing. Generic `i8042.c` then uses the MMIO accessors for command/data operations and the selected IRQs for serio ports.

## State and persistence
The mapped `kbd_iobase` and IRQ globals persist for the driver lifetime. No persistent hardware configuration is saved. The exit path does not unmap `kbd_iobase`.

## Dependencies and integration points
It depends on `<asm/sni.h>`, SNI board-type detection, MMIO mapping, and generic i8042 globals. It integrates non-ISA SNI hardware into the generic i8042 driver.

## Risks
- `i8042_platform_exit()` does not call `iounmap()`, so mapping cleanup relies on process lifetime or historical platform expectations.
- Only two hardcoded physical bases are supported.
- Incorrect board-type detection yields wrong IRQs and I/O base.

## Test signals
- Build with `CONFIG_SNI_RM`.
- Hardware tests should cover RM200 and non-RM200 boards, mapping failure, keyboard/AUX IRQ delivery, and unload/reload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-snirm.h -->
