## sources/distributed-fs/ceph-client/drivers/input/keyboard/pmic8xxx-keypad.c

Purpose: Qualcomm PM8058/PM8921 PMIC keypad matrix driver. It programs PMIC keypad timing, reads recent/old scan arrays, handles stuck-key interrupts, filters ghost keys, and reports matrix events.

Important APIs/types/functions: `struct pmic8xxx_kp` stores dimensions, input, regmap, sense/stuck IRQs, keycodes, device, current and stuck states, and cached control register. `pmic8xxx_kpd_init()` validates/programs rows, columns, scan delay, row hold, and debounce. `pmic8xxx_kp_read_matrix()` implements the synchronous read protocol. `pmic8xxx_kp_scan_matrix()` interprets event counters and reports transitions; `pmic8xxx_detect_ghost_keys()` filters ambiguous multi-key states.

Control flow: probe parses matrix properties and timing/wakeup flags, gets parent regmap and two IRQs, builds keymap, initializes state arrays to released, programs hardware, requests sense and stuck IRQs, reads the control register, registers input, and sets wakeup. Open sets `KEYP_CTRL_KEYP_EN`; close clears it. Sense IRQ reads event count from `KEYP_CTRL`, reads recent/old matrices as needed, reports releases/presses, and updates cached state. Stuck IRQ reads matrices and compares against `stuckstate`.

State/dependencies/integration: state is cached key matrices, control register, PMIC hardware registers, and wake configuration. Dependencies include parent regmap, OF matrix properties, input matrix helpers, IRQs, delays tied to 32 kHz clock, and PM callbacks.

Risks and test signals: synchronous read timing and event counter cases are hardware-sensitive. Ghost-key detection drops the scan without error. Suspend disables the keypad unless wakeup is enabled. Test one/two/lost event paths, stuck IRQ behavior, ghost detection, timing property validation, wake/non-wake suspend paths, and open/close enable bit preservation.
