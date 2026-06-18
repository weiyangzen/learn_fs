# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pearl_pcie_ipc.h

Purpose: defines Pearl PCIe boot-data-area flags, firmware upload constants, descriptor field helpers, and address macros shared by Pearl host and endpoint code.

Important APIs/types/functions: EP state bits include firmware/uboot presence, load-ready/sync/retry/QLINK-done/done and error flags. RC state bits advertise PCIe/net link, flashboot, QLINK, load-ready, and sync. Interrupt bit masks group HDP RX/TX events. `QTN_HOST_HI32`, `QTN_HOST_LO32`, and `QTN_HOST_ADDR` abstract 32-bit versus 64-bit DMA addresses. Constants define BDA version, BDA name length, HHBM max size, firmware upload board flag, block mask, buffer size, descriptor length/port/TQE fields, and firmware load types.

Control flow: `pearl_pcie.c` uses these definitions during BDA state polling, firmware upload packet construction, descriptor programming, interrupt setup, and DMA address reconstruction during cleanup/reclaim.

State and persistence: header constants describe volatile MMIO/BDA state shared with firmware. No host state is stored here.

Dependencies and integration points: includes Linux types and `shm_ipc_defs.h`. It is Pearl-specific and intentionally separate from Topaz, whose BDA state machine differs.

Risks: host and endpoint firmware must agree exactly on bit positions, BDA version, descriptor field layout, and DMA address width. Incorrect `QTN_HOST_ADDR` behavior on 32-bit/64-bit configurations would break DMA unmapping or descriptor programming. Firmware upload constants must match `qtnf_pearl_fw_hdr` packet construction.

Test signals: compile on 32-bit and 64-bit DMA address configurations, Pearl boot handshakes for flashboot and host-upload modes, firmware upload CRC/block sequencing, and descriptor length/port field decoding under traffic.
