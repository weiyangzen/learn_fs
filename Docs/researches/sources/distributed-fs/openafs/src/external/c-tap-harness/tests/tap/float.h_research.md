## sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/float.h

Purpose: public declaration for the floating-point TAP comparison helper.

Important APIs/types/functions: declares `is_double(double, double, double epsilon, const char *format, ...)` with printf-format attribute on the fourth argument. Uses `BEGIN_DECLS`/`END_DECLS` for C++ callers.

Control flow: none; the header communicates that callers pass an expected epsilon and optional TAP description.

State and persistence: no state declared.

Dependencies: includes `tests/tap/macros.h` for compiler attributes and C++ linkage wrappers. The implementation adds the math dependency.

Integration points: included by tests that link `float.c` alongside `basic.c`.

Risks: consumers must remember the extra object/library and possible math-library link flag. The header does not include `basic.h`, so it remains narrow but relies on the implementation for TAP integration.

Test signals: compile/link tests should cover C and C++ inclusion and format-attribute diagnostics where supported.
