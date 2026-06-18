# sources/distributed-fs/ceph-client/arch/arm/kernel/smccc-call.S

Purpose: provides assembly wrappers for ARM SMCCC SMC/HVC calls and optional quirk handling.

Important APIs/types/functions: exports `__arm_smccc_smc` and `__arm_smccc_hvc`, loading argument registers, issuing `smc` or `hvc`, and storing result registers into the caller-provided result structure.

Control flow: wrappers preserve callee-saved state, place up to eight SMCCC arguments in r0-r7, execute the conduit instruction, optionally apply Qualcomm A6 quirk register handling when configured, store r0-r3 results, and return.

State and persistence: no local persistent state; firmware calls may change secure/EL2 state outside Linux.

Dependencies and integration: PSCI, firmware mitigation calls, spectre hardening, and generic SMCCC core depend on these wrappers. ABI must match `linux/arm-smccc.h`.

Risks: register clobber or quirk mishandling corrupts firmware calls; conduit choice must match firmware. Test signals include PSCI boot/hotplug, SMCCC feature discovery, firmware spectre mitigation, and quirk platform tests.
