# sources/distributed-fs/ceph-client/include/soc/starfive/reset-starfive-jh71x0.h

Purpose: defines the auxiliary-device wrapper used by StarFive JH71x0 reset drivers.

Important APIs/types/functions: provides `struct jh71x0_reset_adev` with an MMIO `base` pointer and embedded `struct auxiliary_device`, plus `to_jh71x0_reset_adev()` container macro.

Control flow: StarFive clock/syscon code creates an auxiliary reset device; reset drivers cast back to this wrapper to access the reset register base.

State and persistence: persistent state is the MMIO base and auxiliary-device lifetime. The header does not manipulate reset state directly.

Dependencies and integration: depends on auxiliary bus, compiler type, and container helpers. Used by StarFive JH7110 reset and clock support.

Risks: wrong auxiliary-device type or invalid base lifetime breaks reset register access. Test signals include JH7110 clock/reset probe, reset controller registration, and peripheral reset operations.
