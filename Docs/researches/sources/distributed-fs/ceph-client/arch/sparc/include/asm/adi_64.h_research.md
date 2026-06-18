<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/adi_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/adi_64.h

## Purpose
This header declares SPARC64 Application Data Integrity capability and configuration state.

## Important APIs, Types, and Functions
It defines `struct adi_caps` and `struct adi_config`, declares global `adi_state`, and provides `adi_capable()`, `adi_blksize()`, `adi_nbits()`, plus `mdesc_adi_init()`.

## Control Flow
Machine-description probing initializes `adi_state`; later callers query inline helpers to decide whether ADI is available and what block/tag geometry applies.

## State and Persistence Behavior
`adi_state` persists global hardware capability information after boot. The inline helpers are read-only views of that state.

## Dependencies and Integration Points
It depends on SPARC64 machine descriptions and Linux type definitions. It integrates with memory tagging/ADI syscall and ELF hardware capability exposure.

## Risks
Incorrect ADI geometry can make tag operations address the wrong granularity. Callers must check `adi_capable()` before using ADI-specific paths.

## Test Signals
Boot ADI-capable and non-ADI SPARC64 systems, verify machine-description parsing, ELF HWCAP_ADI exposure, and ADI userspace tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/adi_64.h -->
