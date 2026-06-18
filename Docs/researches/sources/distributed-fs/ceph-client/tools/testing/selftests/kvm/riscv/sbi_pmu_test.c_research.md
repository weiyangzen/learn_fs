# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/sbi_pmu_test.c

## Purpose
This riscv64 KVM selftest validates SBI PMU virtualization. It checks basic PMU discovery, counter information, event counting, snapshot shared-memory operation, and counter overflow interrupt delivery through the Sscofpmf/LCOFI path.

## Important APIs, Types, And Functions
The guest uses `sbi_ecall()` for `SBI_EXT_PMU` calls such as `SBI_EXT_PMU_NUM_COUNTERS`, `COUNTER_GET_INFO`, `COUNTER_CFG_MATCH`, `COUNTER_START`, `COUNTER_STOP`, `COUNTER_FW_READ`, and `SNAPSHOT_SET_SHMEM`. It also uses CSR helpers, vector/interrupt setup helpers, `guest_sbi_probe_extension()`, and `get_host_sbi_spec_version()`. Key globals include `ctrinfo_arr`, `counter_mask_available`, `snapshot_gva`, `snapshot_gpa`, `vcpu_shared_irq_count`, and `targs`. Host helpers create one-vCPU VMs, install exception or interrupt handlers, create an identity-mapped snapshot page, and run selected tests based on `-t` and `-n`.

## Control Flow
`main()` parses CLI selection bits and runs basic, events, snapshot, and overflow tests unless disabled. Basic mode probes PMU, reads counter info, validates hardware CSR access traps through `guest_illegal_exception_handler()`, and checks firmware-counter read behavior. Event mode configures guaranteed cycle and instruction events, starts/stops counters, tests initialization semantics, and resets counters. Snapshot mode sets PMU shared memory and checks counter values in `struct riscv_pmu_snapshot_data`. Overflow mode enables PMU overflow interrupts, starts near-overflow counters, waits, and verifies `guest_irq_handler()` observed expected interrupts.

## State, Dependencies, And Integration
State lives in guest globals synchronized from host where needed. Snapshot data persists only in an anonymous guest page mapped at `PMU_SNAPSHOT_GPA_BASE`. The test depends on KVM RISC-V SBI PMU extension exposure, SBI v2.0 for snapshots, Sscofpmf for overflow, timer frequency for delay helpers, and the KVM selftests ucall/vector frameworks.

## Risks And Test Signals
Risks include host/platform variability in available counters and overflow support, firmware counter gaps, timing sensitivity in overflow delivery, and spec-version differences. The test mitigates with `__TEST_REQUIRE()` for PMU/Sscofpmf availability, invalid-event checks, counter-mask validation, explicit snapshot zero checks, and exact PASS messages for each selected lane.
