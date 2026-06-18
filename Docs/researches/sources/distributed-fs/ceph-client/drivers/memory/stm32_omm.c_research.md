# sources/distributed-fs/ceph-client/drivers/memory/stm32_omm.c

Purpose: STM32 Octo Memory Manager driver for STM32MP25. It validates two OSPI child memory-map regions, configures OMM mux and chip-select override behavior, coordinates child clocks/resets, manages AMCR syscfg memory split, and populates OSPI child devices.

Important APIs/types/functions: `struct stm32_omm` stores memory-map resource, three clocks (`omm`, `ospi1`, `ospi2`), child resets, MMIO base, saved `OMM_CR`, child count, and whether the OMM should be restored. Key helpers are `stm32_omm_set_amcr()`, `stm32_omm_toggle_child_clock()`, `stm32_omm_disable_child()`, `stm32_omm_configure()`, `stm32_omm_check_access()`, probe/remove, and runtime/system PM callbacks.

Control flow: probe maps `regs`, gets the `memory_map` resource, checks exactly two children and firewall grants, gets released child resets, enables runtime PM, then either configures OMM when parent and both children are accessible or only verifies AMCR coherency when access is restricted. Configuration fetches all clocks, resets both OSPI children to ensure disabled state, enables runtime PM, computes max child clock rate, resets OMM, parses optional `st,omm-mux`, `st,omm-req2ack-ns`, and `st,omm-cssel-ovr`, writes `OMM_CR`, sets AMCR, then populates children. If mux mode is enabled, child OSPI clocks remain on.

State and persistence: `omm->cr` caches the programmed control register for resume. `restore_omm` marks whether the driver owns OMM programming. Hardware state includes OMM mux/override bits, AMCR memory split, OSPI reset state, and clock enables. There is no persistent storage outside registers.

Dependencies and integration: depends on clocks, reset control, syscon regmap lookup by `st,syscfg-amcr`, STM32 firewall APIs, OF address resources, pinctrl, runtime PM, and platform child population.

Risks: `stm32_omm_set_amcr()` compares DT memory regions against a syscfg register even when it cannot write it, so preconfigured firmware must match DT. The code assumes two children and memory-region names `ospi1`/`ospi2`. `req2ack` conversion uses the fastest child clock and clamps at 256. On populate failure, mux child clocks are disabled only when mux bit is set. Firewall denial changes behavior from configuration to validation-only.

Test signals: probe with two OSPI children, overlapping memory-region rejection, AMCR mismatch rejection, firewall allowed and denied cases, mux and chip-select override DT options, runtime PM clock control, suspend/resume restoration, and child clock state when mux is enabled.
