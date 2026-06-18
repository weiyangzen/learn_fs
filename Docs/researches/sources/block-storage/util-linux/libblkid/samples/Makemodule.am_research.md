# File Research: sources/block-storage/util-linux/libblkid/samples/Makemodule.am

## Purpose
Autotools build fragment for libblkid sample programs.

## Main Components
- Adds four `check_PROGRAMS`: `sample-mkfs`, `sample-partitions`, `sample-superblocks`, and `sample-topology`.
- Assigns each sample to one C source under `libblkid/samples/`.
- Links all samples against `libblkid.la` and the project `$(LDADD)`.
- Adds the generated libblkid include directory to sample `CFLAGS`.

## Dependencies and Interactions
Included by the parent `libblkid/Makemodule.am` only when `BUILD_LIBBLKID` is enabled. The programs are test/check artifacts rather than installed user commands.

## Research Notes
The sample programs demonstrate both low-level binary APIs and NAME=value probing APIs, making this build fragment useful for validating public API examples.
