# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_input.h

- Purpose: Declares the Mantis rc-core input lifecycle and scancode forwarding functions.
- Important APIs/types/functions: `mantis_input_init`, `mantis_input_exit`, and `mantis_input_process`.
- Control flow: Probe/remove call init/exit; UART decode calls process.
- State and persistence: No state; functions use `struct mantis_pci` rc fields.
- Dependencies and integration points: Integrates `mantis_cards.c` and `mantis_uart.c` with rc-core.
- Risks: The closing comment names UART rather than input, a cosmetic guard-label mismatch.
- Test signals: Compile coverage plus IR event tests.
