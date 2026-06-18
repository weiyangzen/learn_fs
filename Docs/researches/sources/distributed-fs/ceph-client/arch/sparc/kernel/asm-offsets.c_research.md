<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/asm-offsets.c

Purpose: Generates C-derived constants consumed by SPARC assembly.

Important APIs and control flow: under `COMPILE_OFFSETS`, build-time functions emit `DEFINE`/`OFFSET` records for `thread_struct`, `task_struct`, `mm_struct`, `vm_area_struct`, and SPARC64 hibernation `saved_context` fields. The compiled assembler output is post-processed by Kbuild into offset headers.

State, dependencies, and risks: state is build-time metadata, not runtime state. Dependencies include scheduler/mm structure definitions, `linux/kbuild.h`, and optional hibernation structures. Risks are assembly/C layout mismatches if offsets are omitted or conditionals are wrong. Test signals are successful generation of asm-offset headers, SPARC32/SPARC64 builds, hibernation-enabled builds, and low-level assembly using the emitted symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/asm-offsets.c -->
