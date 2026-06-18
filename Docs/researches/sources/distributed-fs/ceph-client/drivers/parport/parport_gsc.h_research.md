# sources/distributed-fs/ceph-client/drivers/parport/parport_gsc.h

## Purpose
`parport_gsc.h` defines register offsets, private driver state, and inline accessors for the HP PA-RISC GSC parport driver. It abstracts GSC byte I/O into the operation callbacks used by `parport_gsc.c`.

## Important APIs, Types, and Functions
Macros `DATA(p)`, `STATUS(p)`, `CONTROL(p)`, `EPPADDR(p)`, and `EPPDATA(p)` compute register addresses. `struct parport_gsc_private` caches control register state and writable bits. Inline callbacks implement data read/write, raw and masked control frobbing, direction changes, status reads, and IRQ enable/disable. Extern declarations expose resource/state helpers and use-count hooks.

## Control Flow
Each control operation updates the cached `ctr`, masks writes through `ctr_writable`, writes the hardware control register, and returns or exposes the cached PC-style bits. Direction control uses bit `0x20`; IRQ enable uses bit `0x10`. Debug builds can add trace logging and optional I/O delays.

## State and Persistence
The main state is `priv->ctr` and `priv->ctr_writable`, which represent soft control-register state and allowed hardware bits. This avoids relying on hardware readback for logical control values.

## Dependencies and Integration Points
The header depends on GSC I/O helpers from `asm/io.h`, `linux/delay.h`, and parport structures from including C files. It is tightly coupled to `parport_gsc.c` and the core parport callback contract.

## Risks
Because reads of control return a software copy, any external hardware modification would not be reflected. The legacy warning path accepts attempts to control direction through bit `0x20` in write/frob control but asks callers to use `data_reverse`/`data_forward`. Register offsets must match LASI/GSC PC-style layout.

## Test Signals
Unit-style instrumentation can validate control mask behavior, direction bit updates, and status/data register addressing. Hardware tests should confirm `ctr_writable` is reduced when PS/2 direction is unsupported.
