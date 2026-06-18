# sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-rtl-pass.h

Purpose: Macro generator for RTL optimization pass boilerplate.

Important APIs/types: Requires `PASS_NAME`; supports `NO_GATE`, `NO_EXECUTE`, `PROPERTIES_*`, and `TODO_FLAGS_*`. Emits RTL pass data, an `rtl_opt_pass` subclass, optional callbacks, clone, and `make_PASS_NAME_pass()`.

Control flow: Included by plugins after defining the pass callbacks and registration metadata. The generated factory is registered with GCC's pass manager.

State/persistence: No independent state; generated passes mutate GCC RTL for the current function when executed.

Dependencies/integration: Depends on GCC RTL pass APIs from `gcc-common.h`; used by `stackleak_cleanup`.

Risks: RTL pass placement is sensitive because late passes have final frame information but limited ability to insert high-level calls. Macro-generator compatibility must be maintained with GCC internals.

Test signals: Compile and run a generated RTL pass with gate and execute callbacks, verify pass position registration, and inspect RTL dumps for expected transformations.
