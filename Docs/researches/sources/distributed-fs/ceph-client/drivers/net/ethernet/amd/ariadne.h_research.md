# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/ariadne.h

Purpose: defines Ariadne board register maps, PCnet-ISA CSR/ISACSR offsets and bit masks, descriptor structures, MC68230 register layout, and board memory offsets for `ariadne.c`.

Important APIs and types: provides `struct Am79C960`, swapped CSR constants, CSR0/CSR3/CSR4/CSR15/ISACSR bit definitions, `struct RDRE`, `struct TDRE`, RX/TX/error flags, `struct MC68230`, and Ariadne offsets for LANCE registers, PIT, boot ROM, and RAM.

Control flow: no executable control flow. The C file uses these definitions when probing, programming the PCnet chip, setting ring pointers, interpreting descriptor status, configuring media auto-select/LEDs, and reserving Zorro resources.

State and persistence: the header stores no state. Its structures describe hardware register and board RAM layout that persists only on the physical device.

Dependencies and integration points: assumes Linux/m68k fixed-width aliases like `u_short` and `u_char`. It is coupled to Ariadne Zorro-II hardware, the Am79C960 PCnet-ISA chip, and MC68230 board glue, and is local to the Ariadne driver.

Risks: many CSR constants are pre-byte-swapped, so using them outside the intended endian path would program incorrect registers. Descriptor and register structures use volatile fields and exact padding assumptions. The boot ROM offset is documented as guessed, so consumers should not rely on it without hardware confirmation.

Test signals: compile coverage with `ariadne.c`, hardware smoke tests for CSR access and descriptor interpretation, and verification that swapped constants program expected PCnet registers.
