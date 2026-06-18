# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/Kconfig

Purpose: sources Kconfig fragments for STI-generation ST media drivers.

Important APIs and symbols: sources `bdisp/Kconfig`, `delta/Kconfig`, and `hva/Kconfig`.

Control flow: selecting the ST platform Kconfig subtree causes these three driver configuration files to be parsed in order.

State and persistence: no runtime state. Kconfig selections persist in the kernel `.config`.

Dependencies and integration points: connects STI BDISP, DELTA, and HVA media drivers to the ST Kconfig tree.

Risks: path mismatches hide driver options. Since this file defines no common dependency, each child Kconfig must enforce architecture, media framework, and compile-test constraints.

Test signals: Kconfig parse tests and menu visibility for BDISP, DELTA, and HVA symbols.
