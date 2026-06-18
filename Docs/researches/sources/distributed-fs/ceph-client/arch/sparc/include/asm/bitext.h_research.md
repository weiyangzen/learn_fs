<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitext.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitext.h

## Purpose
This header declares a bitmap extent allocator interface used by SPARC memory-management code.

## Important APIs, Types, and Functions
It defines the bitext map structure and prototypes for allocating/freeing/searching bit extents.

## Control Flow
Callers initialize a bitmap extent area, request contiguous bit ranges, and release ranges when mappings/resources are freed.

## State and Persistence Behavior
Persistent allocator state is the caller-owned bitmap/metadata. The header itself only declares the interface.

## Dependencies and Integration Points
It integrates with SPARC MM/resource allocation code that needs compact bitmap extent tracking.

## Risks
Off-by-one range handling can leak or double-allocate scarce architecture resources.

## Test Signals
Exercise allocator users under allocation/free churn, with boundary-size requests and full-map exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitext.h -->
