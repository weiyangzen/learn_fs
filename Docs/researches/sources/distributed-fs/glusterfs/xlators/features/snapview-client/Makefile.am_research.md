# sources/distributed-fs/glusterfs/xlators/features/snapview-client/Makefile.am

Purpose: top-level Automake file for the snapview-client feature translator.

Important declarations: `SUBDIRS = src` delegates all build work to the `src` directory.

Control flow/state: no runtime control flow or persisted state. Build traversal is the only behavior.

Dependencies/integration: integrates the translator into the parent GlusterFS feature-xlator build by recursing into `src`.

Risks/test signals: low risk; build-system tests should confirm `make dist`, recursive build, and clean targets include this subdirectory.
