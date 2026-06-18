<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/menelaus.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/menelaus.h

This OMAP Menelaus PMIC header exposes board integration and helper APIs for MMC slot power, voltage rails, sleep regulator configuration, and VCORE hardware limits. `struct menelaus_platform_data` provides an optional `late_init` callback. Exported functions register/unregister an MMC callback, configure MMC open-drain and slot power/card-detect behavior, set VMEM/VIO/VMMC/VAUX/DCDC voltages, select slot routing, read slot pin states, program VCORE roof/floor hardware values, and set regulator sleep bits.

Control flow is platform-service oriented: board or MMC code calls Menelaus helpers after the MFD driver is available, callbacks report card-mask changes, and voltage/sleep settings are applied to PMIC registers by the implementation. State lives in hardware regulator configuration, MMC slot state, callback registration, and sleep-enable bit masks such as `EN_VPLL_SLEEP` through `EN_VC_SLEEP`. This header does not expose a device struct, so the implementation likely owns singleton-style state.

Dependencies include the Menelaus MFD implementation, OMAP board/MMC users, integer voltage units in millivolts, and `u8`/`u32` kernel types. Risks include global callback lifetime, slot number ambiguity, voltage-range validation being hidden in implementation, and sleep bit masks accidentally disabling essential rails. Test signals include callback registration/unregistration order, MMC slot power and card-detect tests, voltage boundary checks, suspend/resume regulator sleep programming, and VCORE roof/floor validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/menelaus.h -->
