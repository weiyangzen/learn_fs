<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/icst.h -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/icst.h

## Purpose

`icst.h` declares the ICST rate-math data structures, functions, and chip limits.

## Important APIs, Types, And Functions

`struct icst_params` captures reference rate, VCO bounds, V and R divider ranges, and chip-specific `s2div`/`idx2s` tables. `struct icst_vco` carries encoded `v`, `r`, and `s` values. The header declares `icst_hz()` and `icst_hz_to_vco()` plus exported lookup arrays for ICST307 and ICST525.

## Control Flow

No executable flow exists. Callers pass filled parameter tables into the math helpers.

## State And Persistence Behavior

No runtime state is stored. Constants define hardware constraints used by rate calculations.

## Dependencies And Integration Points

It is shared by Versatile ICST CCF wrappers and platform-specific descriptors.

## Risks And Test Signals

Risks are misunderstanding inclusive/exclusive VCO limits or encoded divider offsets. Build tests catch declaration drift; rate tests should compare helper output against board manuals for ICST307 and ICST525 examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/icst.h -->
