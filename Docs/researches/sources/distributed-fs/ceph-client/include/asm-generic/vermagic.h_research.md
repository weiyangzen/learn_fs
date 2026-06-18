# sources/distributed-fs/ceph-client/include/asm-generic/vermagic.h

Purpose: generic module version-magic architecture suffix.

Important APIs/types/functions: defines `MODULE_ARCH_VERMAGIC` as an empty string.

Control flow: none.

State and persistence: none.

Dependencies and integration points: included by module build/versioning code when an architecture has no additional vermagic tokens.

Risks: architectures with ABI-affecting options must override this or incompatible modules may appear loadable.

Test signals: module build/load tests and inspection of generated `.modinfo` vermagic strings.
