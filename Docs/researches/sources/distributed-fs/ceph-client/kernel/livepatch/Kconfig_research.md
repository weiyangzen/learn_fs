# sources/distributed-fs/ceph-client/kernel/livepatch/Kconfig

## Purpose
This Kconfig file defines feature gates for kernel live patching and klp-build support.

## Important APIs, Types, And Functions
It declares `HAVE_LIVEPATCH` as an architecture capability, `LIVEPATCH` as the user-visible "Kernel Live Patching" option, `HAVE_KLP_BUILD` as an architecture capability for klp-build, and `KLP_BUILD` as a default-on option when both livepatching and architecture support are present.

## Control Flow
Kconfig dependency resolution enables `LIVEPATCH` only with dynamic ftrace register/argument support, modules, sysfs, complete kallsyms, architecture support, and without `TRIM_UNUSED_KSYMS`. `KLP_BUILD` selects `OBJTOOL` and depends on `LIVEPATCH && HAVE_KLP_BUILD`.

## State And Persistence
The file has no runtime state. It determines compile-time availability of livepatch objects and related build tooling.

## Dependencies And Integration Points
It integrates livepatching with ftrace, modules, sysfs, kallsyms, architecture Kconfig selects, unused-symbol trimming policy, and objtool.

## Risks And Edge Cases
Incorrect dependencies could produce a kernel where livepatch modules cannot resolve symbols or redirect calls safely. `TRIM_UNUSED_KSYMS` is explicitly incompatible because live patches may need symbols that appear unused at base build time.

## Test Signals
Signals include Kconfig dependency tests across architectures, expected visibility of `CONFIG_LIVEPATCH`, `CONFIG_KLP_BUILD` selecting `OBJTOOL`, and successful build of livepatch core objects only when enabled.
