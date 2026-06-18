# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_axuser_nonsecured_regs.h

Purpose: generated register map for non-secured AXUSER attributes in `DCORE0_TPC0_QM`. It exports 19 `mmDCORE0_TPC0_QM_AXUSER_NONSECURED_*` constants from `0x400AB80` to `0x400ABCC`.

Important APIs/types/functions: macro-only API for HB AXUSER ASID, MMU bypass, strong order, no-snoop, write reduction, read atomic, QoS, reserved/core/emem page fields, E2E coordination, and HB/LB write/read override low/high controls.

Control flow: none. External QM setup or security initialization code programs these attributes to define how non-secure queue-manager transactions appear on the AXI fabric.

State and persistence behavior: names persistent hardware transaction-attribute registers. Incorrect values affect memory translation, ordering, coherency, and QoS for non-secure QM traffic.

Dependencies and integration points: included by `gaudi2_regs.h`; associated with the main QMAN map in `dcore0_tpc0_qm_regs.h` and protected by security policy code. Similar naming exists in TPC CFG AXUSER and VDEC bridge AXUSER headers.

Risks: high security risk because MMU bypass and ASID fields directly affect memory isolation. The `NONSECURED` suffix must not be confused with secure AXUSER contexts.

Test signals: secure/non-secure queue submission tests, MMU translation and isolation tests, register readback after initialization, and generated map diff checks.
