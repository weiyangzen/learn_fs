# sources/distributed-fs/ceph-client/drivers/memory/samsung/exynos-srom.h

Purpose: private register definition header for the Exynos SROM controller.

Important APIs/types/functions: defines offsets `EXYNOS_SROM_BW` and `EXYNOS_SROM_BC0` through `EXYNOS_SROM_BC5`, packed bit shifts for data width, address mode, wait enable, byte enable, chip-select shifts, `EXYNOS_SROM_BW__CS_MASK`, and `BCx` timing/page-mode shifts.

Control flow: `exynos-srom.c` uses these constants to update the packed bus-width/control register and compose each bank-control timing value from DT timing cells.

State and persistence: no state is stored in the header. It describes hardware register state that the C driver saves, restores, and configures.

Dependencies and integration: private to the Samsung SROM driver. It intentionally has only include guards and macros.

Risks: the comment says one `BW` register holds four chip-select fields even though offsets and shifts include NCS4/NCS5, so maintainers must verify SoC-specific coverage before adding bank 4/5 programming. Incorrect shift definitions directly alter external-bus timings.

Test signals: compile `exynos-srom.c`, compare generated `BW`/`BCx` values against the Exynos SROM manual, and test page-mode and 16-bit width device-tree configurations.
