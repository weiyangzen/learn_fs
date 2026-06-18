<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/in-kernel-o2iblnd/Makefile -->
# sources/distributed-fs/lustre-release/lnet/klnds/in-kernel-o2iblnd/Makefile

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/in-kernel-o2iblnd/Makefile_research.md`.

Purpose: builds the in-kernel OFED variant of Lustre's o2iblnd module by deriving sources from the sibling `o2iblnd` directory and rewriting OFED feature macros for the in-kernel namespace.

Important APIs/types/functions: kbuild target `obj-m += ko2iblnd.o`; object list `ko2iblnd-objs := o2iblnd.o o2iblnd_cb.o o2iblnd_modparams.o`; generated-source target `sources`; `o2ib_sed_flags` rewrites `HAVE_OFED_` to `IN_KERNEL_HAVE_OFED_`.

Control flow: the `sources` target depends on generated headers and C files. Each generated file has a rule that runs `sed $(o2ib_sed_flags)` over the corresponding `../o2iblnd/` source. Optional `CONFIG_GCOV_PROFILE_LNET` sets `GCOV_PROFILE := y`.

State and persistence behavior: generated files persist in the build tree until cleaned. The Makefile itself carries no runtime state.

Dependencies and integration: depends on kbuild module semantics, sibling external o2iblnd sources, sed, and Lustre's in-kernel OFED compatibility macros.

Risks: regex rewriting is broad by token prefix and can miss nonstandard feature names or rewrite unintended text. Generated files can become stale if source generation is skipped. Object lists must stay synchronized with the external o2iblnd module.

Test signals: run `make sources`, diff generated files for only expected macro rewrites, build with in-kernel OFED headers, build with GCOV enabled, and verify changes in `../o2iblnd` trigger regenerated files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/in-kernel-o2iblnd/Makefile -->
