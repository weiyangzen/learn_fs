# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_dec_regs.h

Purpose: generated AXUSER register map for the decoder path of `DCORE0_VDEC0_BRDG_CTRL`. It exports 19 `mmDCORE0_VDEC0_BRDG_CTRL_AXUSER_DEC_*` constants from `0x41E3C00` to `0x41E3C4C`.

Important APIs/types/functions: macro-only API for HB ASID/MMU bypass/ordering/no-snoop/write-reduction/read-atomic/QoS/reserved/emem/core attributes, E2E coordination, and HB/LB read/write override registers for the VDEC decoder bridge traffic.

Control flow: none. External VDEC bridge initialization uses these addresses to assign transaction attributes for decoder-originated traffic.

State and persistence behavior: persistent MMIO transaction attributes for the decoder bridge. Values influence memory protection, ordering, snooping, and QoS until reset/rewrite.

Dependencies and integration points: included by `gaudi2_regs.h`; related to main bridge control registers in `dcore0_vdec0_brdg_ctrl_regs.h` and field masks in `dcore0_vdec0_brdg_ctrl_masks.h`.

Risks: MMU bypass or wrong ASID/QoS settings can break memory isolation or performance. Similar AXUSER files for MSIX channels increase copy/paste risk.

Test signals: VDEC bridge initialization readback, memory isolation tests for decoder traffic, AXI violation tests, and generated-address comparison.
