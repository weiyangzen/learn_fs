<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/chmctrl.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/chmctrl.h

## Purpose
This header describes UltraSPARC Cheetah memory-controller timing, decode, and address-control registers.

## Important APIs, Types, and Functions
It defines register offsets `CHMCTRL_TCTRL*`, `CHMCTRL_DECODE*`, `CHMCTRL_MACTRL`, timing masks/shifts for SDRAM control, refresh, bank presence, read/write delays, decode valid/match/mask fields, physical-address extraction, and memory-address control/interleave fields.

## Control Flow
Memory-controller code uses these constants to decode configured banks, report errors, or program controller timing during low-level platform setup.

## State and Persistence Behavior
State lives in memory-controller registers. Header constants are stateless; writes by users persist until reset/reprogramming.

## Dependencies and Integration Points
It integrates with UltraSPARC-III memory-controller driver/support and error-reporting paths.

## Risks
The definitions are hardware-critical; incorrect masks or shifts can misdecode physical banks or corrupt timing if used for writes. The `TCTRL4_RDWR_RD_PI_MORE_DLY` literal should be treated cautiously because malformed constants here would break compilation or decoding.

## Test Signals
Build SPARC64 with memory-controller support, read register dumps on US3 systems, and validate decoded bank/timing information against firmware/platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/chmctrl.h -->
