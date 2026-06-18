# sources/distributed-fs/ceph-client/include/linux/soc/pxa/mfp.h

Purpose: This header defines the PXA/MMP Multi-Function Pin configuration encoding and public pin-configuration APIs.

Important APIs/types/functions: It enumerates MFP pin IDs for GPIOs and named peripheral pins, defines `mfp_cfg_t`, bitfield macros for pin, alternate function, drive strength, low-power state, low-power edge detection, and pull state, and provides construction macros `MFP_CFG`, `MFP_CFG_DRV`, `MFP_CFG_LPM`, and `MFP_CFG_X`. For PXA3xx/MMP it defines `struct mfp_addr_map`, address-map macros, and functions `mfp_init_base`, `mfp_init_addr`, `mfp_read`, `mfp_write`, `mfp_config`, `mfp_config_run`, and `mfp_config_lpm`.

Control flow: Platform code maps MFPR registers, initializes pin offset tables, applies arrays of encoded pin configs, and switches between run and low-power configurations around suspend/resume.

State and persistence: MFP register values define pin muxing, drive, pulls, and low-power behavior. The core also maintains pin offset/default tables initialized by platform code.

Dependencies and integration: Integrates with PXA/MMP board files, pin control, GPIO, suspend/resume, and peripheral drivers.

Risks and test signals: Encoded bitfields are dense; wrong pin IDs or low-power states can break boot pins, wake sources, or bus signals. Test pin mux arrays, suspend/resume low-power switching, GPIO mapping through `mfp_to_gpio`, and register readback.
