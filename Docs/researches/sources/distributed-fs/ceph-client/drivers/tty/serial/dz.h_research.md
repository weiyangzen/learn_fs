# sources/distributed-fs/ceph-client/drivers/tty/serial/dz.h

Purpose: register and bit definition header for the DECstation DZ serial chipset driver. It names CSR, receive, transmit, modem, line-parameter, baud, line-number, and buffer constants used by `dz.c`.

Important APIs/types/functions: no functions. Defines `DZ_TRDY`, `DZ_TIE`, `DZ_RDONE`, `DZ_RIE`, receive bits `DZ_DVAL`, `DZ_OERR`, `DZ_FERR`, `DZ_PERR`, software `DZ_BREAK`, modem bits, line IDs, baud encodings, character-size/parity/stop bits, register offsets, `DZ_NB_PORT`, `DZ_XMIT_SIZE`, `DZ_WAKEUP_CHARS`, and helper macros `LINE(x)` and `UCHAR(x)`.

Control flow: `dz.c` uses these constants to decode interrupt causes, select muxed lines, program line parameters, enable per-line TX/RX, infer errors, and size wakeup thresholds.

State/persistence: no state is stored in the header; it defines the hardware register contract.

Dependencies/integration: included by `dz.c`; constants are tied to DEC DZ hardware and serial-core line count/wakeup behavior.

Risks: shared offsets have different read/write meanings, so misuse corrupts behavior. `DZ_BREAK` is a software flag alongside hardware bits and must not collide. Baud support is limited to classic DZ rates up to 9600.

Test signals: `LINE()` extraction, register offset use by access direction, baud encoding coverage, modem/printer line bit mapping, and wakeup threshold behavior.
