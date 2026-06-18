# sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-ipa-pass.h

Purpose: Macro generator for IPA optimization pass boilerplate.

Important APIs/types: Requires `PASS_NAME`; optionally consumes `NO_GENERATE_SUMMARY`, `NO_READ_SUMMARY`, `NO_WRITE_SUMMARY`, `NO_READ_OPTIMIZATION_SUMMARY`, `NO_WRITE_OPTIMIZATION_SUMMARY`, `NO_STMT_FIXUP`, `NO_FUNCTION_TRANSFORM`, `NO_VARIABLE_TRANSFORM`, `NO_GATE`, `NO_EXECUTE`, `PROPERTIES_*`, `TODO_FLAGS_*`, and `FUNCTION_TRANSFORM_TODO_FLAGS_START`. Emits an `ipa_opt_pass_d` subclass and `make_PASS_NAME_pass()`.

Control flow: The generated constructor wires summary, optimization-summary, statement-fixup, function-transform, and variable-transform callbacks into GCC's IPA pass manager.

State/persistence: No independent state; generated pass instances are managed by GCC.

Dependencies/integration: Relies on GCC IPA pass APIs exposed by `gcc-common.h`.

Risks: The visible code places `clone()` inside the `#ifndef NO_GATE` block, so defining `NO_GATE` can affect clone method generation unexpectedly. IPA constructor signatures are particularly sensitive to GCC version changes.

Test signals: Compile IPA passes with different omitted callbacks, with and without gates, and under LTO-oriented builds.
