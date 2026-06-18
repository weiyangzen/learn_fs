# sources/distributed-fs/ceph-client/drivers/soc/dove/Makefile

Purpose: Kbuild file for Marvell Dove SoC support.

Important build behavior: `obj-y += pmu.o` builds the Dove PMU driver whenever the Dove SoC directory is selected.

Control flow and integration: runtime power-domain, reset, and IRQ-controller behavior lives in `pmu.c`.

State and persistence: no runtime state.

Risks and test signals: risk is object inclusion outside intended machine scope if parent selection changes. Test signals are build success for Dove platforms and successful link with PM domain/reset/IRQ dependencies.
