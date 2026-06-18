# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08_cs.c

## Purpose

This file is the PCMCIA wrapper for the ComputerBoards PCM-DAS08. It handles card matching, PCMCIA resource enablement, private allocation, and then delegates all board operation to the shared DAS08 common code.

## Important APIs, Types, and Functions

The static `das08_cs_boards[]` entry describes a 12-bit PCM-DAS08 with bipolar 5 V AI, PCMCIA sample encoding, 3 DI lines, 3 DO lines, and 16 I/O ports. `das08_cs_auto_attach()` sets `dev->board_ptr`, enables PCMCIA I/O with `comedi_pcmcia_enable()`, allocates `struct das08_private_struct`, and calls `das08_common_attach()`. The PCMCIA integration uses `das08_pcmcia_attach()`, `das08_cs_id_table`, `struct pcmcia_driver`, and `module_comedi_pcmcia_driver()`.

## Control Flow, State, and Persistence

Probe enters through the PCMCIA core, which calls `comedi_pcmcia_auto_config()`. Auto-attach requests automatic I/O assignment with `CONF_AUTO_SET_IO`, reads `link->resource[0]->start` as the base port, and lets common attach create subdevices. Remove uses `comedi_pcmcia_auto_unconfig()` and Comedi detach uses `comedi_pcmcia_disable()`. Runtime state is only the PCMCIA resource, `dev->iobase`, and common DAS08 private state.

## Dependencies and Integration Points

The file depends on `linux/comedi/comedi_pcmcia.h` and `das08.h`. It binds PCMCIA manufacturer/card ID `0x01c5:0x4001` and exports a Comedi driver named `das08_cs` plus a PCMCIA driver named `pcm-das08`.

## Risks and Test Signals

Risks are incorrect PCMCIA ID coverage, failed automatic I/O window assignment, and the special `das08_pcm_encode12` data layout being required for correct samples. Test by inserting a matching card, confirming auto-config creates AI/DI/DO subdevices, reading several AI channels, toggling DO, and checking removal disables the PCMCIA resource cleanly.
