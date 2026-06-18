# sources/distributed-fs/ceph-client/arch/alpha/kernel/err_titan.c

**Purpose:** Implements TITAN and Privateer machine-check decoding. It parses CChip non-existent-memory indications, PChip SERROR/PERROR/AGPERROR fields, converts some machine-check-reported interrupts back into normal interrupts, registers Regatta-family console-data-log annotations, and delegates EV6 processor frames where appropriate.

**Important APIs/types/functions:** Exposes `titan_process_logout_frame()`, `titan_machine_check()`, `titan_register_error_handlers()`, `privateer_process_logout_frame()`, and `privateer_machine_check()`. Important helpers are `titan_parse_c_misc()`, `titan_parse_p_serror()`, `titan_parse_p_perror()`, `titan_parse_p_agperror()`, `titan_parse_p_chip()`, `el_process_regatta_subpacket()`, and `privateer_process_680_frame()`.

**Control flow:** `titan_machine_check()` synchronizes, delegates non-system vectors to `ev6_machine_check()`, parses TITAN system logout data silently, reports unless the frame is dismissible, optionally prints verbose decoded details and registers, then derives a TITAN interrupt mask from `c_dirx` and dispatches pending interrupt-like machine checks through `titan_dispatch_irqs()`. PERROR parsing specifically marks legacy VGA/BIOS or low I/O master-abort patterns as dismissible to tolerate video BIOS probing. `titan_register_error_handlers()` registers Regatta/TITAN annotations and handler then calls `ev6_register_error_handlers()`. Privateer processing selects EV6, TITAN, environmental, or unknown handling based on machine-check code; Privateer system events always report then dispatch pending 680/hotplug-like interrupts.

**State and persistence behavior:** Reads PAL logout frames and TITAN system-data areas, temporarily changes `err_print_prefix`, may dispatch IRQs, and clears machine-check state with `wrmces`. Registration mutates the common subpacket registry. No persistent storage is used.

**Dependencies and integration points:** Depends on `<asm/core_titan.h>`, `<asm/err_ev6.h>`, common error utilities, IRQ register access, `titan_dispatch_irqs()` from TITAN system code, and EV6 processing. Used by TITAN/Privateer machine vectors and console data-log replay.

**Risks:** Dismissal heuristics around PCI master aborts must be precise. Verbose decode blocks mean some detail only exists with `CONFIG_VERBOSE_MCHECK`. Converting machine-check bits back into interrupts couples error handling with IRQ routing. The Regatta handler calls `privateer_process_logout_frame()` on embedded frame data, so frame layout assumptions are critical.

**Test signals:** Use TITAN logout-frame samples for CChip NXM, PChip ECC, PCI parity/abort, SG PTE, and AGP errors. Verify expected dismissals for VGA/BIOS probing, interrupt dispatch from `c_dirx`, Privateer environmental vector behavior, Regatta subpacket annotation output, and fallback to EV6 on processor machine checks.
