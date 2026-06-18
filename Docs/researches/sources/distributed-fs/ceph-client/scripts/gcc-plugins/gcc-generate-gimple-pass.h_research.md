# sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-gimple-pass.h

Purpose: Macro generator for boilerplate GIMPLE optimization passes in GCC plugins.

Important APIs/types: Requires `PASS_NAME`; optionally consumes `NO_GATE`, `NO_EXECUTE`, `PROPERTIES_*`, and `TODO_FLAGS_*`. Emits pass data, a `gimple_opt_pass` subclass, optional `gate()` and `execute()` methods calling `PASS_NAME_gate()` and `PASS_NAME_execute()`, `clone()`, and `make_PASS_NAME_pass()`.

Control flow: Included after a plugin defines callbacks and macros. The generated factory is used in `register_pass_info`.

State/persistence: No state by itself. Generated passes operate in GCC's pass manager and use global `g`.

Dependencies/integration: Depends on GCC plugin headers via `gcc-common.h`. Included by latent entropy, stackleak, and randstruct-related passes.

Risks: The file comments mention GCC 4.5-6, but current code is C++ pass-manager style; compatibility assumptions must be tested with supported compiler range. Macro cleanup is critical because the header may be included multiple times.

Test signals: Compile generated passes with gate/execute present and omitted, custom properties/todos, multiple inclusions in one translation unit, and pass registration.
