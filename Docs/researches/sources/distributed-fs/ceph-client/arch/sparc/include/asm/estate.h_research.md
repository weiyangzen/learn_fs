<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/estate.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/estate.h

## Purpose
This header defines UltraSPARC error-state register bits.

## Important APIs, Types, and Functions
It provides masks/shifts for error-state fields used by trap and machine-check code.

## Control Flow
Error handlers read the register and decode processor state using these constants during fault reporting/recovery.

## State and Persistence Behavior
State lives in CPU error registers.

## Dependencies and Integration Points
It integrates with SPARC64 trap/error handling and platform diagnostics.

## Risks
Wrong decoding can obscure fatal hardware errors or misclassify recoverability.

## Test Signals
Validate error logs on hardware/fault injection and compare decoded fields to processor documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/estate.h -->
