## sources/distributed-fs/ceph-client/arch/arm64/kernel/smccc-call.S

### Purpose
`smccc-call.S` implements the assembly call shims for ARM SMCCC SMC/HVC calls, including the classic result structure ABI and the SMCCC 1.2 register-block ABI.

### Important APIs, Types, And Functions
It exports `__arm_smccc_smc`, `__arm_smccc_hvc`, `arm_smccc_1_2_hvc`, and `arm_smccc_1_2_smc`. The `SMCCC` macro stores `x0`-`x3` into `struct arm_smccc_res` and handles the Qualcomm A6 quirk by saving `x6`. The `SMCCC_1_2` macro loads and stores `x0`-`x17` through `struct arm_smccc_1_2_regs`.

### Control Flow
The classic path executes `smc #0` or `hvc #0`, reads the result pointer from the stack, writes result registers, optionally records quirk state, and returns. The 1.2 path saves the result pointer and `x19`, loads argument registers from the caller-provided block, executes the conduit instruction, stores all result registers back, restores `x19`, and returns.

### State, Persistence, And Dependencies
The only persistent state is what the secure monitor, hypervisor, or firmware changes and what the shim writes into caller-owned result structures. There is no kernel global state here.

### Integration Points
The exports are used by firmware, PSCI, hypervisor, errata, secure service, and paravirtualization code needing SMCCC conduits. The file relies on offsets generated from `linux/arm-smccc.h` structures.

### Risks
Register save/restore mistakes corrupt caller state or SMCCC results. Stack argument layout must remain ABI-compatible with the C prototypes. Quirk handling must not clobber normal callers, and firmware may have conduit-specific calling convention constraints.

### Test Signals
Build and boot PSCI/SMCCC users on both SMC and HVC platforms; run firmware feature detection, KVM hypercalls, and Qualcomm quirk coverage; compare generated offsets against structure layout changes.
