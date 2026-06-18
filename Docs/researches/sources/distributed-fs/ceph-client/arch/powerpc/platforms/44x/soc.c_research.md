<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/soc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/soc.c

Purpose: provides shared PPC4xx SoC support for enabling the on-chip L2 cache, handling L2 parity errors, disabling SRAM windows, configuring snoop regions, and resetting the system through DBCR0.

Important APIs/types/functions: `l2c_diag()` issues L2 diagnostic commands; `l2c_error_handler()` decodes cache/tag parity errors and clears them; `ppc4xx_l2c_probe()` locates `ibm,l2-cache`, maps DCR bases, installs IRQ handler, disables SRAM, configures L2 mode/snoop/ports, clears errors, and enables L2; `ppc4xx_reset_system()` reads optional CPU `reset-type` and writes `SPRN_DBCR0`.

Control flow: arch init probes L2 cache if present. It reads `cache-size` and `dcr-reg`, maps IRQ, registers error handler, disables SRAM blocks, enables L2 mode without CPU ports, clears cache contents and parity/tag errors, programs two 32G snoop windows, then enables ICU/DCU ports and special 460EX/GT behavior. Reset writes core/chip/system reset bits and spins.

State and persistence: global `dcrbase_l2c` holds the L2 DCR base; hardware L2/SRAM/snoop/error registers persist. The IRQ handler clears hardware error state.

Dependencies and integration: depends on OF L2 cache node properties, DCR register definitions, IRQ mapping, PPC4xx reset consumers, and CPU node `reset-type`. Board machine descriptors call `ppc4xx_reset_system()`.

Risks and test signals: L2 enablement is hardware-sensitive and disables SRAM use; DCR properties must have four cells; busy-wait loops have no timeout; reset-type values outside 1-3 are ignored. Test boot with and without L2 cache nodes, parity-error IRQ injection, 460EX/GT L2 compatibility, SRAM users, and core/chip/system reset modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/soc.c -->
