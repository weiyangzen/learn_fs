# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/hplance.h

Purpose: defines HP300 DIO LANCE register offsets, status bits, and memory/NVRAM offsets used by `hplance.c`.

Important APIs and types: constants include DIO registers `HPLANCE_ID` and `HPLANCE_STATUS`, status bits `LE_IE`, `LE_IR`, `LE_LOCK`, `LE_ACK`, `LE_JAB`, and offsets `HPLANCE_IDOFF`, `HPLANCE_REGOFF`, `HPLANCE_MEMOFF`, and `HPLANCE_NVRAMOFF`.

Control flow: no executable code. The C driver uses these definitions to reset the board, poll ACK after LANCE register accesses, enable board interrupts, locate the generic LANCE register block and init memory, and read the MAC address from NVRAM.

State and persistence: no software state. The header describes fixed board register and NVRAM locations; the NVRAM MAC contents persist on the device.

Dependencies and integration points: local to HP DIO LANCE support and paired with generic `7990.h` register offsets. It assumes DIO-specific IPL extraction is handled elsewhere.

Risks: all offsets are hard-coded for HP300 DIO hardware. `LE_JAB` is documented uncertainly as loss of TX clock, so diagnostics using it should be treated cautiously. Infinite ACK polling risk lives in the C code that consumes `LE_ACK`.

Test signals: compile coverage through `hplance.c`, hardware validation of MAC nibble offsets, and register-access ACK behavior.
