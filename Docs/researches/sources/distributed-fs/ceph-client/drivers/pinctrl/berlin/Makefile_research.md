# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/Makefile

Purpose: Build rules for the Berlin pinctrl core and per-SoC descriptor drivers.

Important APIs/types/functions: unconditional `obj-y += berlin.o` builds the common core whenever the directory is included; conditional objects build BG2, BG2CD, BG2Q, BG4CT, and AS370 drivers from their Kconfig symbols.

Control flow: Kbuild links `berlin.o` before selected SoC files. SoC objects call the common exported probe helpers in `berlin.c`.

State and persistence: compile-time only; no runtime state.

Dependencies/integration: paired with `drivers/pinctrl/berlin/Kconfig`; relies on all selected per-SoC objects sharing `berlin.h`.

Risks: unconditional common object means the directory inclusion must remain gated by Kconfig. Missing object entry for a new SoC would produce a config that cannot probe despite descriptor code existing.

Test signals: inspect built-in object list for each config and run allmodconfig/allyesconfig style compile coverage.
