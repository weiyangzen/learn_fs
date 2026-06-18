# sources/distributed-fs/ceph-client/tools/perf/util/include/asm/asm-offsets.h

Purpose: a two-line perf tools stub used to satisfy kernel assembly includes that expect `asm/asm-offsets.h`. It has no real offsets because the tools build is not compiling kernel objects that need generated structure offsets.

Important APIs and types: none. The only content is the SPDX tag and a `/* stub */` comment.

Control flow: none at runtime or compile time beyond successful inclusion.

State and persistence: none.

Dependencies and integration: exists under perf's local `util/include/asm` compatibility include tree. It lets imported architecture assembly, especially x86 helper assembly, include kernel-like paths without pulling generated kernel build artifacts into the tools build.

Risks: adding real definitions here could create divergence from generated kernel offsets and hide build problems. Removing it can break imported assembly includes.

Test signals: a tools/perf build that compiles imported assembly is the relevant signal. No unit-level behavior exists.
