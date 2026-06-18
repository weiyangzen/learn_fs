# sources/distributed-fs/ceph-client/drivers/scsi/fdomain.h

## Purpose

`fdomain.h` defines shared Future Domain adapter constants, register offsets, bit masks, command phase flags, PM macro wiring, and exported core prototypes for ISA and PCI wrappers.

## Important APIs, types, and functions

It defines `FDOMAIN_REGION_SIZE`, `FDOMAIN_BIOS_SIZE`, SCSI phase flags, register offsets for data/status/control/config/FIFO/loopback registers, bit masks for bus and adapter control/status, `FDOMAIN_PM_OPS`, and prototypes for `fdomain_create()` and `fdomain_destroy()`.

## Control flow

There is no executable flow. `fdomain.c` uses the definitions to program hardware; `fdomain_isa.c` uses them for region sizing and IRQ/config decoding.

## State and persistence behavior

No software state is stored here. The header describes hardware register state manipulated through I/O port operations.

## Dependencies and integration points

Including C files supply kernel bit helpers and SCSI host declarations. The header is the contract between the shared core and bus wrappers.

## Risks and edge cases

Several offsets have read/write-specific meanings, and some bits are absent on older chips. Using a definition on the wrong chip can program unrelated behavior. PM symbol visibility depends on `CONFIG_PM_SLEEP`.

## Test signals

Compile ISA/PCI modules with PM enabled and disabled; run hardware tests on supported chip families, especially registers marked absent on older chips.
