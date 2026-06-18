# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-klconfig.c

Purpose: helper searches over SGI KL configuration boards and components.

Important APIs and control flow: `find_component()` returns the next component of a requested type after an optional current component, validating that the current pointer belongs to the board. `find_first_component()` is a convenience wrapper. `find_lboard()` scans linked boards for an exact board type. `find_lboard_class()` scans for a board with the same KL class.

State, persistence, and integration: it has no persistent state and reads firmware KL config structures in memory. Dependencies include KL macros such as `KLCF_NUM_COMPS`, `KLCF_COMP`, and `KLCF_NEXT`. Risks include trusting firmware-provided linked structures and returning NULL on pointer mismatch after logging only. Test signals are successful CPU, memory, router, and xbow discovery by callers.
