# sources/distributed-fs/ceph-client/lib/raid/xor/um/xor_arch.h

Purpose: reuses x86 XOR registration for User Mode Linux builds.

Important APIs and flow: includes `<../x86/xor_arch.h>`, so UML inherits the x86 architecture XOR selection definitions.

State and persistence: no state.

Dependencies and integration: depends on the x86 XOR header being suitable for the UML include context.

Risks and test signals: risk is include-path or feature-helper incompatibility between UML and native x86. Signals include UML builds with XOR blocks enabled and KUnit XOR execution in UML.
