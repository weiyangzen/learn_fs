<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/serial.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/serial.h

**Purpose:** Defines default 8250 serial port baud base, flags, and standard COM port table for Alpha PC-style UARTs.

**Important APIs/types/functions:** `BASE_BAUD`, `STD_COM_FLAGS`, `STD_COM4_FLAGS`, and `SERIAL_PORT_DFNS` for ttyS0-ttyS3.

**Control flow:** The 8250 serial driver consumes the macro table at initialization to register legacy ports and optionally detect IRQs.

**State and persistence behavior:** No local state; registered UART state is owned by serial core.

**Dependencies and integration points:** Depends on `CONFIG_SERIAL_8250_DETECT_IRQ` and 8250 port flag definitions.

**Risks:** Legacy I/O addresses and IRQs may collide with platform quirks; COM4 deliberately skips `UPF_SKIP_TEST` due to the 8514 problem.

**Test signals:** Boot with serial console, verify ttyS0-ttyS3 registration, IRQ autodetection, and no false COM4 conflict.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/serial.h -->
