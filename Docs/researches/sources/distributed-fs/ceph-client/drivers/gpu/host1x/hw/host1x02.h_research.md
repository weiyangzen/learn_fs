<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x02.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x02.h

## Purpose

`host1x02.h` declares the host1x02 (Tegra114) generation initialization entry point used by the platform driver's match table.

## Important APIs, Types, And Functions

- Forward declaration of `struct host1x`.
- `int host1x02_init(struct host1x *host)`: installs hardware operation tables for Tegra114.
- Capability context from `dev.c`: 9 channels, 32 syncpoints, 16 mlocks, 12 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

The header has no executable control flow. `dev.c` references the prototype when building the `host1x_info` table, and the matching platform probe calls the function after mapping resources and before initializing channels/syncpoints.

## State And Persistence Behavior

No state is stored in this header. The declared function mutates operation-table pointers in `struct host1x`.

## Dependencies And Integration Points

It is paired with `host1x02.c` and included by `dev.c`. The function name is a cross-file contract for SoC match data.

## Risks And Test Signals

Signature drift breaks generation init at build time. Runtime validation is probe on Tegra114 and confirming that all operation pointers are non-NULL after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x02.h -->
