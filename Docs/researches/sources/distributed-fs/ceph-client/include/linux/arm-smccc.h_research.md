# sources/distributed-fs/ceph-client/include/linux/arm-smccc.h

## Purpose
Defines ARM SMC Calling Convention IDs, return values, version/conduit helpers, KVM and standard service IDs, and inline/assembly-backed invocation APIs for SMC/HVC calls.

## Important APIs, Types, And Functions
The header builds function IDs with `ARM_SMCCC_CALL_VAL()` and extracts call properties with `ARM_SMCCC_IS_FAST_CALL()`, `ARM_SMCCC_IS_64()`, `ARM_SMCCC_FUNC_NUM()`, and `ARM_SMCCC_OWNER_NUM()`. It defines owner ranges, SMCCC versions 1.0-1.3, architecture feature/workaround IDs, KVM vendor hypervisor IDs for PTP, pKVM memory share/unshare, MMIO guard, implementation discovery, PV time calls, TRNG calls, and return codes. Runtime APIs include `arm_smccc_1_1_get_conduit()`, `arm_smccc_get_version()`, `arm_smccc_version_init()`, SoC ID getters, `arm_smccc_hypervisor_has_uuid()`, `smccc_res_to_uuid()`, `smccc_uuid_to_reg()`, low-level `__arm_smccc_smc()`/`__arm_smccc_hvc()`, v1.2 register calls on arm64, and variadic `arm_smccc_1_1_{smc,hvc,invoke}()` plus `arm_smccc_1_2_invoke()`.

## Control Flow, State, And Persistence
SMCCC call flow packages up to eight arguments into fixed registers for v1.1 or `a0..a17` for v1.2, issues `smc #0` or `hvc #0` based on conduit, and writes result registers back to caller-provided structures. If no conduit is valid, the invoke macros place `SMCCC_RET_NOT_SUPPORTED` in `a0`. Persistent state is the initialized SMCCC version/conduit maintained by architecture code, not by the header.

## Dependencies And Integration Points
Depends on `linux/args.h`, `linux/init.h`, `linux/uuid.h`, `linux/linkage.h`, `linux/types.h`, and architecture opcode definitions. Integrated by ARM/arm64 firmware, PSCI-like services, KVM guests/hosts, pKVM protected memory, TRNG, PV time, Spectre/erratum workarounds, and SoC ID discovery.

## Risks And Test Signals
Register constraints and variadic macro arity are sensitive; wrong argument count or width can corrupt firmware calls. Missing conduit handling must return not-supported rather than executing invalid instructions. Tests should cover SMC and HVC conduits, no-conduit fallback, UUID conversion, KVM feature probing, TRNG/PV time callers, arm64 v1.2 extended registers, and builds across ARM, ARM64, and non-SMCCC configs.
