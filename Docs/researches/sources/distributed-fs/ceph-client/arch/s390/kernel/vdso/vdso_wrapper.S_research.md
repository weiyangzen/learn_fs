## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso_wrapper.S

Purpose: Embeds the built `vdso.so` binary into the kernel image as page-aligned data.

Important symbols: Global `vdso_start` and `vdso_end`.

Control flow: Switches to page-aligned data, aligns to `PAGE_SIZE`, incbins `arch/s390/kernel/vdso/vdso.so`, aligns again, and returns to the previous section.

State and persistence: The incbined vDSO image is persistent kernel data used by `vdso.c` to build the special mapping page list.

Dependencies and integration: Depends on the Makefile forcing `vdso_wrapper.o` to depend on `vdso.so`, linker page alignment, and runtime vDSO mapping code.

Risks and test signals: Risks are stale incbin dependency, misalignment, or missing symbols. Test signals are vDSO mapping page count, `vdso_start`/`vdso_end` symbols, and clean rebuild after vDSO source changes.
