<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/Kbuild

## Purpose
This exported-headers Kbuild file controls which SPARC asm headers are generated or exposed to userspace.

## Important APIs, Types, and Functions
It uses Kbuild `generic-y`/`generated-y` style header lists for asm include handling. The file is intentionally small but affects `make headers_install` and generated asm offsets.

## Control Flow
Kbuild reads this file while preparing architecture headers and decides whether a header is provided by SPARC, generated, or inherited from generic asm.

## State and Persistence Behavior
No runtime state exists. The persistent outputs are installed/generated headers in the build tree.

## Dependencies and Integration Points
It integrates `arch/sparc/include/asm` with generic header generation and userspace header export.

## Risks
Misclassifying a header can break userspace header installation or cause kernel code to include a missing generated file.

## Test Signals
Run `make ARCH=sparc headers_install` and `make ARCH=sparc archheaders`; verify generated asm headers and installed UAPI completeness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/Kbuild -->
