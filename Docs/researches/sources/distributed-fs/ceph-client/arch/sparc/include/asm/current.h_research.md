<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/current.h

## Purpose
This header implements `current` task lookup for SPARC.

## Important APIs, Types, and Functions
It defines `get_current()`/`current` access using the SPARC stack/thread-info layout or dedicated register convention.

## Control Flow
Kernel code expands `current` inline to derive the active `task_struct` quickly.

## State and Persistence Behavior
No state is stored here; it reads the active task pointer/thread information.

## Dependencies and Integration Points
It integrates with scheduler, thread-info layout, context switching, and low-level entry code.

## Risks
Wrong stack masking or register assumptions make `current` point at the wrong task, causing broad corruption.

## Test Signals
Boot, context-switch stress, interrupt-in-task tests, and stack/thread-info debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/current.h -->
