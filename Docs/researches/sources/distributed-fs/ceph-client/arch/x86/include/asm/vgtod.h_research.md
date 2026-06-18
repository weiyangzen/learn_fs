# sources/distributed-fs/ceph-client/arch/x86/include/asm/vgtod.h

Purpose: Acts as the x86 vDSO gettimeofday bridge header while avoiding unwanted dependencies for UML builds.

Important APIs/types/functions: When `CONFIG_GENERIC_GETTIMEOFDAY` is enabled, it includes compiler helpers, x86 clocksource definitions, vDSO datapage/helpers, and UAPI time types.

Control flow: No runtime code. The preprocessor guard controls which dependencies are visible.

State and persistence: No state. It exposes types and helper declarations used by vDSO time code.

Dependencies and integration points: Integrates `asm/vdso/gettimeofday.h`, generic vDSO time helpers, and x86 clocksource definitions. The comment calls out `ARCH=um` as a reason for the config guard.

Risks: Including too much unconditionally can break UML. Including too little under `CONFIG_GENERIC_GETTIMEOFDAY` can break vDSO time compilation.

Test signals: Builds for native x86 and UML, plus vDSO time selftests.
