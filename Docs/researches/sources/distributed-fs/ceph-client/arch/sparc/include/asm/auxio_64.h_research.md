<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio_64.h

## Purpose
This header defines SPARC64 AUXIO and PCIO auxiliary register bits plus helper APIs for LED and link-test control.

## Important APIs, Types, and Functions
It defines AUX1/AUX2/PCIO bit masks for floppy density, link test, monitor/mouse mux, terminal count, LED, power fail, and power off. It declares `auxio_set_lte()` and `auxio_set_led()`.

## Control Flow
SPARC64 platform code maps the relevant auxiliary registers and driver code calls the declared helpers to update specific bits.

## State and Persistence Behavior
Persistent state is in the hardware AUXIO/PCIO registers. The header only describes the bit layout.

## Dependencies and Integration Points
It integrates with SPARC64 platform initialization, LED support, network link-test behavior, floppy support, and power-management paths.

## Risks
Different systems expose different AUXIO variants; using the wrong mask can manipulate unrelated platform signals.

## Test Signals
Boot SPARC64 platforms with AUXIO/PCIO, toggle LEDs/link-test where supported, and validate power-fail/off register handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio_64.h -->
