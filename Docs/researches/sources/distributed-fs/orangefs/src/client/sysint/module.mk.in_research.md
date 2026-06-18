# sources/distributed-fs/orangefs/src/client/sysint/module.mk.in
## sources/distributed-fs/orangefs/src/client/sysint/module.mk.in

**Purpose:** Build manifest fragment for the client sysint library sources and generated state-machine C files.

**APIs and control flow:** Defines `DIR := src/client/sysint`, lists hand-written `CSRC` files, lists generated `CLIENT_SMCGEN` C outputs from `.sm` sources, conditionally adds `mgmt-get-user-cert.c` when `ENABLE_SECURITY_CERT` is set, appends generated files to `SMCGEN`, and appends all sysint sources to `LIBSRC`.

**State and dependencies:** Drives the repository build system rather than runtime. It depends on the state-machine generator producing the named `.c` files and on configure-time variables.

**Risks and tests:** Missing a new hand-written or generated source here excludes it from the library. Conditional security file handling must match generated symbols declared in `client-state-machine.h`. Build tests should run with and without `ENABLE_SECURITY_CERT`, validate dist-clean generated file tracking, and ensure every extern SM has a compiled implementation.
