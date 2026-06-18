# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-errata.h

## Purpose
`cvmx-helper-errata.h` declares helper support for known Octeon hardware errata. In this slice it exposes one QLM workaround hook used to disable second-order clock-data-recovery behavior where required by the affected silicon.

## Important APIs, Types, And Functions
The single exported function is `__cvmx_helper_errata_qlm_disable_2nd_order_cdr(int qlm)`. It takes a QLM lane group number and has no return value, implying the implementation directly programs low-level QLM configuration registers.

## Control Flow
There is no inline flow. Interface bring-up or lane initialization code calls the errata helper before or during high-speed link setup when the chip model and QLM mode require the workaround.

## State And Persistence
Persistent state is the altered QLM hardware configuration. The header itself has no data. Because the function likely changes analog/serdes behavior, effects last until reset or later QLM reconfiguration.

## Dependencies And Integration Points
The declaration is included by `cvmx-helper.h` and is relevant to SGMII, XAUI, PCIe, or other helpers that share QLM lanes. It usually depends on model detection and low-level JTAG/QLM CSR access in its implementation.

## Risks
Errata hooks are deliberately hardware-specific. Calling the workaround on an unaffected model or wrong QLM can degrade link training, while omitting it on affected silicon can cause intermittent high-speed link failures. The absence of a return code means callers need external verification.

## Test Signals
Test by comparing link stability, error counters, and negotiation success across affected and unaffected chip revisions. Validate the hook is invoked only for intended model/QLM combinations and that repeated calls are harmless.
