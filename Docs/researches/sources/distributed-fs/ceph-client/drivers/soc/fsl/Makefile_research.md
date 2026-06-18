# sources/distributed-fs/ceph-client/drivers/soc/fsl/Makefile

Purpose: Kbuild routing for Freescale/NXP SoC driver subdirectories and objects.

Important build behavior: DPAA builds `qbman/`, QUICC/CPM build `qe/`, and individual options add `rcpm.o`, `guts.o`, `dpio/`, and `dpaa2-console.o`.

Control flow and integration: it maps the Kconfig feature set to concrete object directories, keeping DPAA1 and DPAA2 components separate.

State and persistence: no runtime state.

Risks and test signals: risks are object selection drift or whitespace-sensitive Kbuild mistakes. Test signals are enabled options producing expected objects and disabled options not exporting unwanted APIs.
