# sources/distributed-fs/ceph-client/drivers/soc/qcom/Makefile

## Purpose
Maps Qualcomm SoC Kconfig symbols to object files and composite modules.

## Important APIs, Types, And Functions
Relevant rules build `cmd-db.o`, `apr.o`, `icc-bwmon.o`, `kryo-l2-accessors.o`, and composite `qcom_ice-objs += ice.o` linked under `CONFIG_QCOM_INLINE_CRYPTO_ENGINE`. It also sets local include CFLAGS for several objects.

## Control Flow
The kernel build includes each object according to the selected `CONFIG_QCOM_*` symbol. Composite modules such as `qmi_helpers-y` and `qcom_rpmh-y` aggregate multiple objects.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Consumes the local Kconfig symbols and participates in module naming, e.g. the ICE source becomes the `qcom_ice` module rather than `ice`.

## Risks
Object naming matters for module aliases and exported symbols. Moving `ice.o` out of `qcom_ice-objs` would change module identity.

## Test Signals
Build output should contain expected Qualcomm objects/modules for each config permutation, especially module builds of APR, BWMON, command DB, and ICE.
