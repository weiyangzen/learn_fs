# sources/distributed-fs/ceph-client/drivers/ssb/host_soc.c

## Purpose
Host operations for memory-mapped SoC SSB buses with no external PCI/PCMCIA/SDIO host, plus invariant extraction from BCM47xx NVRAM and SPROM fallback.

## Important APIs, Types, and Functions
Defines `ssb_host_soc_ops` with byte/word/dword read/write and optional block I/O callbacks. Public `ssb_host_soc_get_invariants` fills `struct ssb_init_invariants` from NVRAM and fallback SPROM.

## Control Flow
Read/write ops compute `bus->mmio + core_index * SSB_CORE_SIZE + offset` and perform direct MMIO accesses. Block I/O loops over the same fixed address using raw accessors at the requested width. Invariant extraction reads `boardvendor`, `boardtype`, and `cardbus` NVRAM variables, defaults vendor to Broadcom when absent, and calls `ssb_fill_sprom_with_fallback`.

## State and Persistence
No private state beyond values written to caller-provided invariants. Hardware MMIO writes directly affect SSB core registers. Parsed board info persists in `struct ssb_bus` after main registration copies it.

## Dependencies and Integration Points
Used by `ssb_bus_host_soc_register` in `main.c`. Depends on BCM47xx NVRAM and SSB fallback SPROM infrastructure.

## Risks
Block I/O warns on unaligned byte counts but still loops by width. Invalid NVRAM values only warn and may leave board fields zero/default. Direct SoC mapping assumes `bus->mmio` covers all cores at `SSB_CORE_SIZE` strides.

## Test Signals
SoC bus registration should scan cores through these ops, board vendor/type should match NVRAM or defaults, fallback SPROM should populate wireless data, and block I/O should match scalar reads/writes.
