# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/serial.h

Purpose: Provides ISS platform serial constants needed by generic serial code.

Important APIs, types, and functions: Header guard `__ASM_XTENSA_ISS_SERIAL_H` and `BASE_BAUD`.

Control flow: No executable control flow; defines `BASE_BAUD 0` because real 8250 baud rates have no meaning on ISS but generic early serial code expects the macro.

State and persistence: No runtime state.

Dependencies and integration: Included by serial/8250 early code or platform serial consumers for ISS builds.

Risks: `BASE_BAUD` being zero is intentional for ISS but would be invalid for real UART programming if reused outside simulator context.

Test signals: ISS builds with 8250 early serial code and no divide-by-zero or missing macro warnings.
