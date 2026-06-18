# sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-simple_ipa-pass.h

Purpose: Macro generator for simple IPA pass boilerplate where only gate/execute style callbacks are needed.

Important APIs/types: Requires `PASS_NAME`; supports `NO_GATE`, `NO_EXECUTE`, `PROPERTIES_*`, and `TODO_FLAGS_*`. Emits simple IPA pass metadata, class/factory, and macro cleanup.

Control flow: Intended for inclusion after defining callbacks; generated pass is registered through GCC's pass manager.

State/persistence: No independent state.

Dependencies/integration: Uses GCC pass APIs from `gcc-common.h`.

Risks: Same macro-inclusion risks as the other generators: leaked macros, missing callback names, or GCC API drift break builds. Simple IPA passes still run at whole-program points where side effects can be broad.

Test signals: Compile a minimal simple IPA plugin, exercise no-gate/no-execute variants, and verify pass-manager registration.
