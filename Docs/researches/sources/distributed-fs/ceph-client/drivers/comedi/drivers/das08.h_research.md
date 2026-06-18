# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08.h

## Purpose

This header is the shared contract between the DAS08 common module and its ISA, PCI, and PCMCIA bus front ends. It defines the board descriptor shape, per-device private state, encoding/range enums, and the common attach function used after each wrapper has claimed its resources.

## Important APIs, Types, and Functions

`enum das08_ai_encoding` describes how the two ADC data registers encode samples: standard 12-bit, 16-bit sign-magnitude, and PCMCIA 12-bit. `enum das08_lrange` selects common AI range/gain tables. `struct das08_board_struct` carries board name, JR flag, AI/AO bit width, AI range and encoding, digital channel counts, 8255/8254 offsets, and I/O size. `struct das08_private_struct` stores the shared DO/mux register shadow and active gainlist. The only exported function prototype is `das08_common_attach()`.

## Control Flow, State, and Persistence

The header has no runtime flow but establishes state ownership. Bus wrappers set `dev->board_ptr` to one of their static board records and allocate `struct das08_private_struct`; `das08_common_attach()` then initializes `pg_gainlist` and maintains `do_mux_bits` at runtime. The fields are in-memory driver state only and are rebuilt on attach.

## Dependencies and Integration Points

It depends only on `linux/types.h` and a forward declaration of `struct comedi_device`, avoiding bus-specific headers. It is included by `das08.c`, `das08_isa.c`, `das08_pci.c`, and `das08_cs.c`.

## Risks and Test Signals

The main risk is descriptor mismatch: a wrong `ai_encoding`, gain enum, offset, or channel count propagates directly into common register programming. Test signals are successful compilation of all wrappers, correct subdevice inventory for each board table entry, and no out-of-range indexing into the common range/gain arrays.
