# sources/distributed-fs/ceph-client/drivers/remoteproc/pru_rproc.h

## Purpose

`pru_rproc.h` defines PRU firmware interrupt-map data structures consumed by `pru_rproc.c`. It documents the compact `.pru_irq_map` section format used by PRU firmware to describe PRUSS system-event, channel, and host interrupt routing.

## Important APIs, types, and data

- `struct pruss_int_map` maps one PRU system event to one PRUSS interrupt channel and one host interrupt.
- `struct pru_irq_rsc` is a packed variable-length section header containing a resource type, event count, and flexible array of `struct pruss_int_map`.

## Control flow

The header has no executable flow. `pru_rproc_parse_fw()` locates `.pru_irq_map`, saves a pointer and size, and `pru_handle_intrmap()` validates `type`, `num_evts`, and total size before creating IRQ mappings from the flexible array.

## State and persistence behavior

No state lives in the header. The structures define firmware ABI. During runtime, `pru_rproc.c` holds a temporary pointer into the firmware image until start consumes it; created IRQ mappings persist until stop or start failure cleanup.

## Dependencies and integration points

This header is shared between PRU firmware layout expectations and Linux PRU remoteproc parsing. It uses fixed-width integer types and `__packed` for ABI layout. It integrates with PRUSS INTC routing through `irq_create_fwspec_mapping()`.

## Risks and edge cases

- The flexible array has no inherent bounds; consumers must validate `num_evts` and total section size, which `pru_handle_intrmap()` does.
- `type` currently supports only zero. Future types require coordinated parser changes.
- Because the structures are packed firmware ABI, padding or type changes would break existing firmware blobs.

## Test signals

Firmware parser tests should cover no section, header-only/truncated section, invalid type, `num_evts` above `MAX_PRU_SYS_EVENTS`, size mismatch, valid single mapping, many-to-one channel/host mappings, and cleanup when one mapping fails.
