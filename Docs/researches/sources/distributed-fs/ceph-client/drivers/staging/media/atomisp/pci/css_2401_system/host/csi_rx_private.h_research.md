# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/csi_rx_private.h

Purpose: provides inline device-level and native-command helpers for CSI RX frontend/backend register access, state capture, and debug dumps.

Important APIs/types/functions: DLI helpers are `csi_rx_fe_ctrl_reg_load()`, `csi_rx_fe_ctrl_reg_store()`, `csi_rx_be_ctrl_reg_load()`, and `csi_rx_be_ctrl_reg_store()`. NCI helpers include `csi_rx_fe_ctrl_get_dlane_state()`, `csi_rx_fe_ctrl_get_state()`, `csi_rx_fe_ctrl_dump_state()`, `csi_rx_be_ctrl_get_state()`, and `csi_rx_be_ctrl_dump_state()`.

Control flow: register helpers assert valid IDs/base addresses and perform 32-bit MMIO loads/stores using register index times word size. State getters read known registers and loop over lane/LUT counts from global arrays. Dumpers print captured fields.

State and persistence: writes mutate hardware registers. State structures are snapshots. No software persistence beyond caller variables.

Dependencies and integration: depends on generated HRT register indices from `rx_csi_defs.h` and `mipi_backend_defs.h`, CSI ID/base arrays, `device_access`, assertions, and print support.

Risks and test signals: this header defines non-static inline-like functions depending on storage-class macros from public headers; duplicate definition rules matter. Some custom-mode backend reads are disabled under `#if 0` due to device access errors, so diagnostic coverage is incomplete. Tests should validate ID assertions, FE lane loops, BE LUT loops, and register address calculations on all CSI instances.
