# sources/distributed-fs/ceph-client/include/linux/mfd/hi655x-pmic.h

Purpose: This header defines common HiSilicon HI655x PMIC addressing, interrupt registers, version bounds, interrupt bit positions, and parent device state.

Important APIs, types, and constants: `HI655X_STRIDE` and `HI655X_BUS_ADDR(x)` encode the 4-byte bus address stride. IRQ constants define 32 interrupts over four status/mask bytes, base addresses for IRQ status/mask and analog IRQ masks, clear and mask values, version register and version range, individual interrupt bit positions, and corresponding `BIT()` masks. `struct hi655x_pmic` holds the device, regmap, IRQ, IRQ domain, and cached version.

Control flow, state, and persistence: The parent driver reads version information, sets up interrupt masking and domains, clears latched interrupts, and passes regmap access to child devices. Persistent state is PMIC register state; cached `ver` is live driver state used for variant behavior.

Dependencies and integration points: It depends on regmap and IRQ-domain infrastructure. It integrates with PMIC regulator, power key, thermal/fault, and platform child drivers that need the shared interrupt namespace.

Risks and test signals: Risks include stride/address confusion, failing to clear all four IRQ arrays, treating reserved interrupt bits as real signals, and version range checks that reject valid silicon. Test signals include IRQ domain mapping for 32 lines, status/mask/clear sequencing, version readback tests, and PMIC fault interrupt simulations.
