# sources/distributed-fs/ceph-client/drivers/scsi/fdomain_isa.c

## Purpose

`fdomain_isa.c` is the ISA autodetection and resource wrapper for the Future Domain TMC-16x0 driver. It scans BIOS ROM addresses and I/O ports, parses signatures and optional I/O-base hints, derives IRQ/SCSI ID, reserves I/O regions, calls the shared core, and releases resources on remove. It also supports explicit `io`, `irq`, and `scsi_id` arrays.

## Important APIs, types, and functions

Important tables are `addresses[]`, `ports[]`, `irqs[]`, and `signatures[]`. Main functions are `fdomain_isa_match()`, `fdomain_isa_param_match()`, `fdomain_isa_remove()`, `fdomain_isa_init()`, and `fdomain_isa_exit()`. `fdomain_isa_driver` wires match/remove and shared PM ops into the ISA bus.

## Control flow

Autodetect mode probes BIOS ROM slots first, searching known signatures and optionally reading a base address from ROM. If a signature lacks a base, it is saved for later port probing. Port probes reserve the I/O region, decode IRQ from `REG_CFG1`, pick a SCSI ID, call `fdomain_create()`, and store the host in drvdata. Parameter mode probes up to four explicit I/O bases and uses provided or decoded IRQs.

## State and persistence behavior

Module parameter arrays persist for module lifetime. A static `saved_sig` bridges ROM detection to port probing. Per-device state is the SCSI host pointer in drvdata. The wrapper owns I/O regions; the core owns IRQ/SCSI host state.

## Dependencies and integration points

The file depends on Linux ISA support, I/O memory mapping, I/O region reservation, signature checking, port I/O, and the shared `fdomain` core.

## Risks and edge cases

`saved_sig` is global across probes and can be ambiguous with multiple boards. IRQ autodetection is configuration-register decoding, not active probing. Explicit parameter mode is selected solely by `io[0]` and disables mixed autodetect. Unsupported or unusual BIOS versions may be missed.

## Test signals

Test BIOS-provided base, BIOS signature without base plus later port probe, fixed-port probe, explicit parameters, busy-region failure, invalid chip cleanup, IRQ decode, remove cleanup, and PM resume.
