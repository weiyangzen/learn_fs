<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc_dt.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc_dt.c

## Purpose
Builds a Linux OpenFirmware-style device tree from OLPC OFW callbacks and applies compatibility fixups for older firmware.

## Important APIs, Types, And Functions
`prom_olpc_ops` supplies `of_pdt` callbacks for sibling/child/property/path traversal. `prom_early_alloc()` allocates boot memory for the tree. `olpc_dt_fixup()` adds battery, DCON, and RTC compatible nodes via OFW `interpret`. `olpc_dt_build_devicetree()` performs fixups and calls `of_pdt_build_devicetree()`.

## Control Flow
The builder exits if OFW is absent. It fixes the live firmware tree based on board revision and existing compatible markers, gets the root node, then recursively builds the Linux device tree through OFW client interface calls.

## State And Persistence
Tracks bytes allocated during boot in `prom_early_allocated`. Fixups mutate the firmware device tree before Linux imports it. The resulting Linux OF tree persists after init.

## Dependencies And Integration Points
Uses OLPC OFW client calls, memblock, `of_pdt`, OLPC board revision helpers, and later OLPC drivers that match compatible strings such as `olpc,xo1-rtc`.

## Risks And Edge Cases
OFW callback failures can produce incomplete DTs. Property buffers are small for compatibility strings. Firmware tree mutation via interpreted Forth words is brittle and board-revision-specific.

## Test Signals
Boot log reporting PROM DT memory use, presence of expected OF nodes/compatibles, and successful binding of RTC/DCON/battery drivers validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc_dt.c -->
