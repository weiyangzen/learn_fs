
# sources/distributed-fs/ceph-client/drivers/soc/litex/litex_soc_ctrl.c

## Purpose
LiteX SoC controller platform driver. It verifies LiteX CSR access through a scratch register and registers a restart handler that writes the LiteX reset register.

## Important APIs, Types, and Functions
- `litex_check_csr_access()` reads/writes/restores scratch register and panics on mismatch.
- `struct litex_soc_ctrl_device` stores CSR base.
- `litex_reset_handler()` writes reset value.
- `litex_soc_ctrl_probe()` maps registers, checks CSR access, and registers restart handler.

## Control Flow
Probe allocates device state, maps resource 0, validates scratch read value, writes test value, validates it, restores original scratch value, logs initialization, and registers a devm restart handler. System restart calls the handler, which writes `1` to reset offset.

## State and Persistence
Private state is devm-managed base pointer. Scratch register is temporarily modified and restored. Reset register write causes system reset.

## Dependencies and Integration Points
Depends on OF compatible `litex,soc-controller`, `linux/litex.h` accessors, platform I/O resources, and sys-off restart handler framework.

## Risks
The driver intentionally panics if CSR access appears broken, which is appropriate for incorrect soft-SoC endianness/layout but fatal at boot. Restart registration failure is warning-only.

## Test Signals
Valid scratch read/write, intentional mismatch panic, restart handler write, missing resource failure, and compatible matching.
