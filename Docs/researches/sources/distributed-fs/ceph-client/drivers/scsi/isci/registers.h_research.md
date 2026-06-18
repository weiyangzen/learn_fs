# sources/distributed-fs/ceph-client/drivers/scsi/isci/registers.h

Purpose: defines the Intel SCU memory-mapped register layout, register offsets, bit masks, and helper macros used by the ISCI driver. It is the low-level hardware contract for SMU, SDMA, transport/link layers, port task schedulers, VIIT/IIT tables, SGPIO, AFE, scratch RAM, and protocol engine groups.

Important APIs/types/functions: generic helpers include `SCU_GEN_VALUE()`, `SCU_GEN_BIT()`, `SCU_SET_BIT()`, and many register-family-specific generators such as `SMU_*_GEN_*`, `SCU_UFQ*`, `SCU_SAS_*`, and `SCU_PTS*`. Major structs include `scu_viit_entry`, `scu_iit_entry`, `smu_registers`, `scu_sdma_registers`, `scu_transport_layer_registers`, `scu_link_layer_registers`, `scu_sgpio_registers`, `scu_port_task_scheduler_registers`, `scu_port_task_scheduler_group_registers`, `scu_afe_transceiver`, `scu_afe_registers`, `scu_peg_registers`, and top-level `scu_registers`.

Control flow: there is no executable control flow. The file provides constants and C struct overlays used with `readl()`/`writel()` from other files. Drivers compute bitfield values with the macros, then write through pointers to these structs after BAR mapping.

State and persistence: all state represented here is hardware state in MMIO registers or controller RAM windows. Software state is not stored in this header. Register effects persist until hardware reset, driver reprogramming, or power state changes.

Dependencies and integration points: consumed broadly by ISCI host, PHY, port, request, and remote-node context code. `port.c` uses VIIT status fields, link-layer control, port task scheduler control, and hang-detection registers. `remote_device.c` posts context commands through host helpers whose bit layouts come from related SCU definitions. Host initialization uses SMU, SDMA, completion queue, task-context, and AFE layouts.

Risks: this file is typo-sensitive because a single wrong mask, shift, offset, or reserved range corrupts hardware programming. There are visible suspicious definitions worth review, including `SCU_CLEAR_BIT(name, reg_value)` containing `((reg_value)$ ~(SCU_GEN_BIT(name)))`, `SCU_SDMA_UNSOLICITED_FRAME_QUEUE_GET_CYCLE_BIT_MASK` defined as `(12)` rather than a shifted mask, `SCU_UFQGP_CYCLE_BIT(value)` passing an extra argument to `SCU_UFQGP_GEN_BIT`, and `SCU_UFQGP_GET_POINTER(value)` referencing `SCU_UFQGP_GEN_VALUE` while only `SCU_UFQGP_GEN_VAL` is defined. These may be dead macros, but compile coverage should confirm.

Test signals: build tests with all ISCI paths enabled are essential because many macros are only compiled when referenced. Hardware or MMIO-emulation tests should validate register offsets with `offsetof()`, queue pointer encoding, task scheduler suspend/enable bits, VIIT programming, link-layer speed/timeout fields, SGPIO offsets, and AFE register programming against hardware documentation.
