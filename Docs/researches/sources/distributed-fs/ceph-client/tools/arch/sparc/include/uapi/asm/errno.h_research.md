# sources/distributed-fs/ceph-client/tools/arch/sparc/include/uapi/asm/errno.h

## Purpose
SPARC errno numbering table for tools, matching SunOS-influenced SPARC ABI values.

## Important APIs, Types, and Functions
Includes generic errno base and defines networking, filesystem, STREAMS, key, robust mutex, RF-kill, and hardware poison errnos with SPARC-specific numbers and aliases.

## Control Flow, State, and Persistence
No flow or state; constants are compiled into target-aware tools.

## Dependencies and Integration Points
Integrated with syscall tracing and errno-name mapping for SPARC targets.

## Risks and Test Signals
Risk is host/target errno mismatch because SPARC values differ from generic Linux. Test signals are errno mapping tests and syscall trace decode checks.
