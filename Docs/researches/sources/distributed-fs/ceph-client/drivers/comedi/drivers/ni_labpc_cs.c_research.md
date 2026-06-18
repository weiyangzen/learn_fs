# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_cs.c

## Purpose
`ni_labpc_cs.c` is the PCMCIA front end for the NI DAQCard-1200, a Lab-PC-family board. It sets up PCMCIA resources and delegates device behavior to `labpc_common_attach()`.

## Important APIs, Types, And Functions
`labpc_cs_boards[]` defines the DAQCard-1200 board info: 10 us AI speed, AO present, Lab-PC-1200 register set. `labpc_cs_auto_attach()` assigns the board pointer, enables PCMCIA I/O and IRQ resources, records the I/O base, validates IRQ presence, and calls common attach with `IRQF_SHARED`. `labpc_cs_detach()` calls common detach and disables PCMCIA. `driver_labpc_cs`, `labpc_cs_attach()`, `labpc_cs_ids[]`, and `labpc_cs_driver` register the Comedi/PCMCIA integration.

## Control Flow
PCMCIA ID `0x010b/0x0103` triggers auto config. The driver requests automatic I/O assignment plus enabled pulse IRQ. Once resources are active, it calls common attach exactly like an I/O-port Lab-PC-1200 board. All AI/AO/DIO/calibration/EEPROM behavior is then provided by `ni_labpc_common.c`.

## State And Persistence
No unique private state is allocated here. The board pointer is a static DAQCard-1200 descriptor. Runtime state is `labpc_private` from common attach and PCMCIA resource state from Comedi PCMCIA helpers.

## Dependencies And Integration Points
The file depends on Comedi PCMCIA helpers and `ni_labpc.h`. It integrates with common Lab-PC code and the Linux PCMCIA ID/probe/remove model.

## Risks
The device requires an IRQ; `labpc_cs_auto_attach()` fails with `-EINVAL` if PCMCIA enable does not provide one. The comments document DAQCard-1200-specific chanlist quirks that are enforced in common scan validation through board flags. Resource flags include pulse IRQ behavior, so changing PCMCIA config flags can break interrupt delivery.

## Test Signals
Tests should confirm PCMCIA ID matching, config flags before enable, I/O base assignment, no-IRQ failure, shared IRQ handoff to common attach, common attach failure propagation, detach ordering, and DAQCard-1200 board flags reflected in common subdevices.
