# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/skfbi.h

## Purpose
`skfbi.h` defines the PCI FDDI adapter register map, interrupt bits, BMU control/status bits, address translation macros, FORMAC/PLC register access helpers, timer bits, descriptor control bits, and low-level I/O macros used by board and FORMAC code.

## Important APIs, Types, And Functions
Major groups include banked register offsets (`B0_*` through `B6_*`), control bits (`CTRL_*`, `DAS_*`, `LED_*`, `TIM_*`), interrupt source/mask bits (`IS_*`, `IRQ_*`, `ALL_IRSR*`), BMU reset/start bits (`CSR_*`), descriptor flags (`BMU_OWN`, `BMU_STF`, `BMU_EOF`, `BMU_BBC`), address helpers (`ADDR`, `ADDRS`, `PCI_C`, `FM_A`, `PLC`, `GET_ISR`), interrupt mask helpers, `MARW`, `MARR`, `MDRW`, and `GET_ST*`.

## Control Flow
This header is macro-only but controls every hardware access path. Board reset uses `B0_CTRL`, `B0_DAS`, LEDs, PCI config, and masks. FORMAC code uses `FM_A`, `MARW`, `MDRW`, and status registers. ISR code uses `GET_ISR()` and masks.

## State And Persistence
No C state is declared, but macros read and write persistent device registers, EEPROM/PROM windows, timers, BMU descriptors, and adapter memory while powered.

## Dependencies And Integration Points
It depends on `PCI`, optional memory-mapped I/O, low-level `inp/outp/inpw/outpw/inpd/outpd`, and FORMAC/PLC constants from `supern_2.h`. Included by `drvfbi.c`, `fplustm.c`, and hardware modules.

## Risks And Edge Cases
`ADDR()` changes the RAP bank register as a side effect, so concurrent or reordered register access can hit the wrong bank. Memory-mapped and I/O-port modes differ. Interrupt mask constants differ for adapter variants. BMU reset/start sequencing is hardware-sensitive.

## Test Signals
Register access smoke tests, bank switching across high offsets, interrupt mask setup, reset control sequencing, DAS/bypass and LED writes, BMU reset/clear/start, descriptor ownership flags, FORMAC MDR writes, and ISR source decoding on Da Vinci versus Monalisa-style hardware.
