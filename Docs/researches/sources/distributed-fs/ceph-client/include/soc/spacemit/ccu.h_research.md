# sources/distributed-fs/ceph-client/include/soc/spacemit/ccu.h

Purpose: defines the auxiliary-device wrapper shared by SpacemiT CCU clock and reset drivers.

Important APIs/types/functions: provides `struct spacemit_ccu_adev` containing an embedded `struct auxiliary_device` and `struct regmap *regmap`, plus `to_spacemit_ccu_adev()`.

Control flow: the CCU common/clock code creates auxiliary reset devices, and reset drivers recover the wrapper through the inline container helper before using the shared regmap.

State and persistence: persistent state is the auxiliary device and regmap pointer. Hardware state is accessed by consumers through regmap, not by this header.

Dependencies and integration: depends on `linux/auxiliary_bus.h` and `linux/regmap.h`. Used by SpacemiT clock and reset common code.

Risks: helper misuse with a non-SpacemiT auxiliary device corrupts container access. Regmap lifetime must outlive child reset devices. Test signals include K1/K3 CCU probe, reset auxiliary binding, and reset assert/deassert operations.
