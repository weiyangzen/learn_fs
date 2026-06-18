# sources/distributed-fs/ceph-client/arch/x86/coco/sev/Makefile

Purpose: builds AMD SEV confidential-computing runtime support objects.

Important APIs and state: lists `core.o`, `noinstr.o`, `vc-handle.o`, and `svsm.o`. Disables UBSAN/KASAN/KCSAN/GCOV for `noinstr.o` to preserve noinstr behavior even with compiler inlining limitations.

Control flow: make-time object selection and instrumentation control only.

Dependencies and integration: feeds the AMD SEV runtime subtree used by early #VC handling, SVSM services, and CoCo platform support.

Risks and test signals: sanitizer or coverage instrumentation in noinstr code can make #VC/NMI-sensitive paths unsafe. Test sanitizer-enabled builds, objtool/noinstr validation, and SEV-ES/SNP runtime #VC paths.
