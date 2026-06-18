<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/fsp2.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/fsp2.c

Purpose: implements IBM FSP-2 476FPE board support, including bus population, critical hardware error IRQ handlers, early DCR/L2/CMU error setup, UIC initialization, and board reset/progress hooks.

Important APIs/types/functions: diagnostic helpers `l2regs()` and `show_plbopb_regs()` dump L2 and bridge state; IRQ handlers `bus_err_handler()`, `cmu_err_handler()`, `conf_err_handler()`, `opbd_err_handler()`, `mcue_handler()`, and `rst_wrn_handler()` log hardware status and panic; `node_irq_request()` maps compatible error nodes to handlers; `critical_irq_setup()` installs all critical handlers; `fsp2_probe()` performs early hardware programming; `fsp2_irq_init()` chains UIC setup and critical IRQ registration.

Control flow: `fsp2_probe()` first checks flat-DT compatibility `ibm,fsp2`, clears/masks PLB6 errors, ungates/fixes TVSENSE, enables broad L2 machine-check/interrupt reporting, and enables configuration-logic parity errors. Later `fsp2_device_probe()` populates PLB/OPB buses. IRQ setup initializes UICs and registers fatal handlers based on OF compatible names.

State and persistence: persistent state is hardware register configuration in PLB, CMU, L2, DDR, and configuration logic DCRs plus registered IRQ handlers. The handlers intentionally terminate the system on fatal hardware errors.

Dependencies and integration: depends on FSP2 DCR macros in `fsp2.h`, UIC, OF IRQ parsing, PPC4xx reset, and board-specific compatible nodes for critical errors.

Risks and test signals: fatal handlers panic unconditionally; duplicated `P0EARH`/`P1EARH` prints may hide low register values; missing IRQ nodes leave errors unhandled; early DCR magic values are hardware-sensitive. Test FSP2 boot, critical IRQ registration, injected bus/CMU/config/DDR errors, reset-warning path, and OF bus device enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/fsp2.c -->
