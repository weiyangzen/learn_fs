# sources/distributed-fs/ceph-client/tools/testing/radix-tree/Makefile

## Purpose
This Makefile builds user-space radix-tree, XArray, Maple tree, IDR, IDA, regression, iteration, and benchmark tests from kernel library sources plus local harness files.

## Important APIs, Types, And Functions
Important variables are `TARGETS`, `CORE_OFILES`, and `OFILES`. Targets include `main`, `idr-test`, `multiorder`, `xarray`, and `maple`. Special object dependencies map `xarray.o` to `../../../lib/test_xarray.c` and `idr-test.o` to `../../../lib/test_ida.c`.

## Control Flow
The `targets` target builds generated headers and all test binaries. `main` links the full object set. Focused binaries link subsets such as `idr-test.o $(CORE_OFILES)`. `clean` removes binaries, objects, generated headers, and generated source copies.

## State And Persistence
The Makefile persists generated headers under `generated/` and compiled objects/binaries. No runtime state is defined.

## Dependencies And Integration Points
It includes `../shared/shared.mk`, which supplies common user-space kernel-test build rules and generated headers. It integrates local test harness code with selected kernel library test sources.

## Risks
The object list must stay synchronized with test source files and upstream kernel library test locations. The `clean` target deletes generated local copies such as `radix-tree.c` and `idr.c`, so any manual edits to generated files would be lost.

## Test Signals
Successful builds of `main` and focused targets verify that user-space shims and generated headers are compatible with current kernel tree code.
