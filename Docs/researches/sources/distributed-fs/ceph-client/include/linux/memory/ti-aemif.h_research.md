<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory/ti-aemif.h -->
# sources/distributed-fs/ceph-client/include/linux/memory/ti-aemif.h

## Purpose
This header defines chip-select timing data and validation/programming APIs for TI AEMIF asynchronous external memory interfaces.

## Important APIs, types, and functions
`struct aemif_cs_timings` holds turnaround, read hold/strobe/setup, and write hold/strobe/setup values expressed as clock cycles minus one. APIs are `aemif_set_cs_timings()` and `aemif_check_cs_timings()`.

## Control flow
Board or memory drivers populate timing values, optionally validate them, then program a selected chip select through `aemif_set_cs_timings()`.

## State and persistence
Timing state persists in AEMIF controller registers while powered. The header stores no runtime state.

## Dependencies and integration points
It depends on integer types and the opaque `struct aemif_device`. It integrates memory/flash/NAND style devices with TI AEMIF controller drivers.

## Risks and test signals
Risks include off-by-one timing conversion, chip-select index mistakes, invalid timing ranges, and programming timings while a device is active. Test boundary timing validation, each chip select, read/write waveform correctness, and controller suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory/ti-aemif.h -->
