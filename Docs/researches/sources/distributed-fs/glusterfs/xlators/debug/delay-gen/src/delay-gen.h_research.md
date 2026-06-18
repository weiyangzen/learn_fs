# sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen.h

## Purpose
This header defines the private state structure for the delay-gen debug translator.

## Important APIs, Types, And Functions
It includes delay-gen memory and message headers and defines `dg_t` with `uint32_t delay_ppm`, `uint32_t delay_duration`, and `bool enable[GF_FOP_MAXVALUE]`.

## Control Flow
No executable control flow exists. `delay-gen.c` reads and mutates the fields during initialization and FOP delay checks.

## State And Persistence Behavior
The `dg_t` instance is runtime-only and stored in `xlator_t->private`. It is allocated on `init()` and freed on `fini()`.

## Dependencies And Integration Points
The header relies on GlusterFS FOP enumeration size (`GF_FOP_MAXVALUE`) and the local mem/message headers. It is the shared contract between delay-gen implementation and any future helpers.

## Risks
If GlusterFS adds FOPs without increasing or correctly maintaining `GF_FOP_MAXVALUE`, the enable bitmap assumptions would break. `delay_ppm` is an integer threshold derived from a double percentage, so precision is bounded by `DELAY_GRANULARITY`.

## Test Signals
Build coverage is primary. Option parsing tests indirectly validate the bitmap length and state layout.
