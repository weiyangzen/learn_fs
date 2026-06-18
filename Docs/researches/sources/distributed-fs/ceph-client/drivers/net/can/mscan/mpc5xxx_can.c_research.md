# sources/distributed-fs/ceph-client/drivers/net/can/mscan/mpc5xxx_can.c

## Purpose
`mpc5xxx_can.c` is the platform/OF glue for Freescale MPC5xxx MSCAN controllers. It maps registers, obtains IRQ and SoC-specific clocks, allocates the generic MSCAN netdev, registers it, and handles remove plus basic suspend/resume register save/restore.

## Important APIs, Types, And Functions
- `struct mpc5xxx_can_data` selects controller type and clock get/put callbacks per compatible.
- `mpc52xx_can_get_clock()` handles MPC5200 clock source selection between bus and oscillator, including the old revision A erratum.
- `mpc512x_can_get_clock()` interprets `fsl,mscan-clock-source` and `fsl,mscan-clock-divider`, configures clock parents/rates, enables the IPG register clock, and stores clock handles in `mscan_priv`.
- `mpc512x_can_put_clock()` disables the IPG clock.
- `mpc5xxx_can_probe()` maps OF resources, parses IRQ, allocates `alloc_mscandev()`, fills private fields, derives the CAN clock, and calls `register_mscandev()`.
- `mpc5xxx_can_remove()` unregisters the generic device, releases clocks, unmaps IO, disposes IRQ mapping, and frees the candev.
- PM callbacks save the MSCAN register block into static `saved_regs` and restore it around INIT mode.

## Control Flow
OF matching selects either MPC5200 or MPC5121 data. Probe maps the first register resource and IRQ, allocates a generic MSCAN netdev, records the base and IRQ, reads the optional clock-source property, asks the SoC callback for a usable CAN clock and `MSCAN_CLKSRC` setting, and registers the device. Registration is delegated to `mscan.c`, which programs acceptance filters and registers with SocketCAN.

MPC512x clock setup can auto-select a system clock divisible to 16 MHz, fall back to reference clock, or obey explicit `ip`, `sys`, or `ref` choices. It also enables the separate IPG clock needed for register access.

Suspend copies the register layout to a static buffer. Resume requests INIT mode, restores control, bit timing, acceptance, buffer, interrupt, and TX selection registers, then returns to the previous control state.

## State And Persistence
State lives in the platform device driver data as the netdev and in `mscan_priv` fields populated here. Clock handles are devm-managed but enabled/disabled explicitly for MPC512x IPG. The PM save area is a single static `struct mscan_regs`, which persists only in kernel memory and is shared across instances.

## Dependencies And Integration Points
The file depends on OF address/IRQ APIs, platform devices, PPC SoC helpers, MPC52xx register definitions, the common clock framework for MPC512x, and generic MSCAN APIs from `mscan.h`/`mscan.c`.

## Risks And Edge Cases
- The static `saved_regs` suspend buffer is not per-device, so multiple MSCAN instances suspended concurrently could overwrite each other.
- Clock derivation returns zero on many failures, which collapses distinct clock errors into a generic probe failure.
- `of_iomap()`/`irq_of_parse_and_map()` are manually paired with `iounmap()`/`irq_dispose_mapping()`, so error paths must remain balanced.
- MPC5200 oscillator selection depends on SoC-specific CDM mapping and PVR erratum handling.

## Test Signals
Test MPC5200 and MPC5121 compatible probing, explicit and automatic clock-source properties, invalid clock-source failure, register clock enable/disable, remove error-path cleanup, suspend/resume with active configuration, and multiple-channel suspend behavior if hardware exposes more than one node.
