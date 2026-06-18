# sources/distributed-fs/ceph-client/drivers/thunderbolt/cap.c

## Purpose
`cap.c` implements Thunderbolt switch and port capability-list traversal and lookup, including vendor-specific capability search.

## Important APIs, Types, and Functions
Public APIs are `tb_port_next_cap`, `tb_port_find_cap`, `tb_switch_next_cap`, `tb_switch_find_cap`, and `tb_switch_find_vse_cap`. Internal helpers handle legacy TMU access enable/disable and Light Ridge dummy reads.

## Control Flow
Port search optionally enables TMU access for Light Ridge/Eagle Ridge, walks linked capabilities from `first_cap_offset`, reads each header, compares the capability id, performs a dummy read for Light Ridge cleanup, and disables TMU access. Switch traversal reads capability headers and interprets next pointers differently for TMU, short VSE, and long VSE formats; invalid or unknown caps return errors or terminate when offsets exceed the VSE max.

## State and Persistence Behavior
The code temporarily toggles legacy TMU access bits in switch config space during port capability lookup. No driver-owned persistent state is created.

## Dependencies and Integration Points
It depends on Thunderbolt config-space read/write helpers, switch generation predicates, capability header layouts from `tb_regs.h`, and caller-held topology state.

## Risks and Edge Cases
Malformed capability lists can loop or point outside valid space; the code relies on hardware next pointers and max checks. Legacy TMU enable must be unwound even if capability search fails. Unknown switch capabilities return `-EINVAL`.

## Test Signals
KUnit or mocked config-space tests for no capability, matching capability, read failures, VSE short/long headers, Light Ridge dummy read, and TMU enable/disable error paths.
