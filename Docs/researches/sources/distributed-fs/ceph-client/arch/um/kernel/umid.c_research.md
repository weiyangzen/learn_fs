# sources/distributed-fs/ceph-client/arch/um/kernel/umid.c

## Purpose
Handles the kernel-facing `umid=` setup parameter, which assigns a unique UML instance identity used by host-side pid and management files.

## Important APIs, Types, and Functions
`set_umid_arg()` parses `umid=`, suppresses passing it to the generic kernel command line, calls host-side `set_umid()`, warns on duplicate initialization or existing use, and records successful initialization. `__uml_setup("umid=", ...)` registers help text.

## Control Flow, State, and Persistence
The only state is `umid_inited`, preventing multiple `umid=` applications. The actual persistent directory/pid file lifecycle is implemented in `os-Linux/umid.c`.

## Dependencies and Integration Points
Depends on setup parameter scanning in `um_arch.c` and host functions `set_umid()`/warnings from `os-Linux/umid.c` and `os-Linux/util.c`.

## Risks and Test Signals
Risks are duplicate or too-long IDs, failure to suppress host-only options, and collision handling. Test explicit `umid=`, duplicate args, concurrent UML instances with same ID, and fallback random IDs.
