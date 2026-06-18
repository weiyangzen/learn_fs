# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/ibuf_ctrl_global.h

Purpose: defines public IBUF controller configuration structures and supplemental FSM/status constants.

Important APIs/types/functions: constants name main-controller FSM masks/states and DMA sync states not present in generated defs. `isp2401_ib_buffer_t` describes an input-buffer address/stride/line count. `ibuf_ctrl_cfg_t` describes online mode, DMA channel/command/reconfiguration packing, input buffer, destination buffer, store counts, and Stream2MMIO sync/store commands. `N_IBUF_CTRL_PROCS` declares per-controller process limits.

Control flow: no direct logic. Configuration code fills `ibuf_ctrl_cfg_t` and writes registers defined in `ibuf_cntrl_defs.h`.

State and persistence: config structures are caller-owned; applied values persist in hardware registers.

Dependencies and integration: includes generated IBUF controller defs and bridges DMA, Stream2MMIO, and IBUF controller configuration.

Risks and test signals: command fields must use exact DMA and Stream2MMIO token values. Tests should cover online/offline configs, buffer end-address calculations, element packing shifts, and FSM status interpretation.
