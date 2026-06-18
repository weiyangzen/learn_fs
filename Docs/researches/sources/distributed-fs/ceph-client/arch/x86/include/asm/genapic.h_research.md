<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/genapic.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/genapic.h

## Purpose
Compatibility include that forwards generic APIC users to asm/apic.h. The header is 1 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/apic.h>`

Notable constants/macros: None visible in this header.

Notable declarations and inline helpers: None visible in this header.

## Control Flow
No control flow or state; it is a one-line include shim.

## State and Persistence
State and persistence are inherited from APIC code, not this file.

## Dependencies and Integration Points
Integrated by older code that still includes genapic.h after APIC header consolidation.

## Risks
Risk is limited to include-order or stale dependency assumptions.

## Test Signals
Test signal is compile coverage of legacy include users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/genapic.h -->
