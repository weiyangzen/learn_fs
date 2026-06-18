# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_axuser_nonsecured_regs.h

## Purpose
`rot0_qm_axuser_nonsecured_regs.h` names the non-secured AXUSER attribute registers for rotator 0's queue manager. These registers describe how QMAN HBW/LBW transactions are tagged on the fabric.

## Important APIs, Types, And Functions
The macros cover HB ASID, MMU bypass, strong ordering, no-snoop, write reduction, read atomic, QoS, reserved fields, EMEM compact page, core ID, end-to-end coordination, write/read override low/high words, and LB coordination/lock/reserved/override registers.

## Control Flow
There is no code flow. QMAN initialization or security setup writes these addresses so subsequent queue-manager transactions carry the intended AXUSER attributes. Override registers can replace default fabric attributes for read/write paths.

## State, Persistence, And Dependencies
The state is hardware transaction-attribute configuration. It persists until reset or reprogramming and directly affects memory translation, ordering, snooping, QoS, and security classification. It depends on Gaudi2 MMU/ASID conventions and AXUSER bit definitions shared across other generated headers.

## Integration Points
The header integrates with queue-manager setup, protected/non-secured access policy, MMU bypass handling, fabric QoS, and debug/security code that verifies allowed register ranges.

## Risks
Incorrect ASID or MMU-bypass attributes can route accesses through the wrong address space or bypass translation unexpectedly. Strong-order/no-snoop/QoS misconfiguration can cause performance regressions or coherency surprises. Override fields are especially risky because they can affect every QMAN transaction.

## Test Signals
Signals include successful queue DMA through expected ASID, correct MMU fault behavior when bypass is disabled, no unauthorized non-secured access, expected ordering for completion writes, and register readback after context switches or reset recovery.
