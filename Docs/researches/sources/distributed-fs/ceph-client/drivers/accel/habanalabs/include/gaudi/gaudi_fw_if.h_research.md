## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_fw_if.h

### Purpose
`gaudi_fw_if.h` defines small Gaudi firmware-interface constants and payload structures shared by the driver and device firmware. It covers MSI vector assignments, firmware image offsets, thermal adjustment, NIC AXI error encoding, cold-reset data, and a low PLL frequency threshold.

### Important APIs, Types, And Functions
Important constants include `GAUDI_EVENT_QUEUE_MSI_IDX`, NIC port MSI indices for ports 1, 3, 5, 7, and 9, `UBOOT_FW_OFFSET`, `LINUX_FW_OFFSET`, `HBM_TEMP_ADJUST_COEFF`, and `GAUDI_PLL_FREQ_LOW`. `enum gaudi_nic_axi_error` names NIC AXI error sources such as `RXB`, `RXE`, `TXS`, `TXE`, `QPC_RESP`, `NON_AXI_ERR`, and `TMR`. `struct eq_nic_sei_event` is an 8-byte event payload with `axi_error_cause`, `id`, and padding. `struct gaudi_cold_rst_data` overlays a little-endian 32-bit word with an `spsram_init_done` bit.

### Control Flow
The header has no functions. Runtime code uses the MSI indices while requesting interrupt vectors and mapping event queues, firmware-loader paths use the offsets when staging U-Boot or Linux firmware, thermal code adjusts HBM-derived composite temperatures, NIC SEI handling decodes `eq_nic_sei_event`, and cold-reset paths exchange `gaudi_cold_rst_data` through scratch registers.

### State, Persistence, And Dependencies
The persistent state described by this file is firmware-owned or device-owned: MSI routing, SRAM/HBM firmware placement, event queue payloads, scratch cold-reset data, and PLL status. The structures use fixed-width Linux/UAPI-style types such as `__u8`, `__le32`, and `u32`, so endian and packing assumptions are important.

### Integration Points
`gaudiP.h` includes this header for private driver state and event definitions; `gaudi.c` uses `GAUDI_EVENT_QUEUE_MSI_IDX` in interrupt setup and event queue logic. NIC error handling combines `eq_nic_sei_event` with async events such as `GAUDI_EVENT_NIC_SEI_*`.

### Risks
Firmware ABI mismatch is the main risk. Changing MSI indices or firmware offsets can break boot and event delivery. Padding in `eq_nic_sei_event` keeps the payload 64-bit aligned; changing it can desynchronize firmware event parsing. Bitfield layout in `gaudi_cold_rst_data` must match the little-endian scratchpad word.

### Test Signals
Validate interrupt allocation and event queue delivery on MSI vector 8, NIC port interrupts on their assigned vectors, firmware load addresses, HBM temperature reporting with the adjustment coefficient, NIC SEI payload decoding for each `gaudi_nic_axi_error`, and cold-reset scratchpad handoff for `spsram_init_done`.
