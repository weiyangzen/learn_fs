# sources/cloud-native/cri-o/internal/runtimehandlerhooks/high_performance_hooks_test.go

Purpose: broad unit/integration-style coverage for high-performance runtime hook helpers and hook selection.

Important APIs/types/functions: mock service/command runners, fixture builders, tests for `setIRQLoadBalancing`, `getHousekeepingCPUs`, `injectHousekeepingEnv`, `doSetCPUPMQOSResumeLatency`, `doSetCPUFreqGovernor`, `RestoreIrqBalanceConfig`, `handleIRQBalanceRestart`, `updateNewIRQSMPAffinityMask`, `convertAnnotationToLatency`, `setSharedCPUs`, `PreCreate`, and `HooksRetriever.Get`.

Control flow: tests create fake container specs, sandbox annotations, sysfs-like directories, irqbalance config files, and cgroup manager mocks. Several scenarios run hooks concurrently to verify locking around IRQ mask updates.

State and persistence behavior: writes temporary files under `fixtures/`, overrides package globals `serviceManager` and `commandRunner`, and resets them after relevant tests.

Dependencies and integration points: uses Ginkgo/Gomega, gomock, CRI-O sandbox/oci/config types, cgroup manager mocks, runtime-spec, runtime-tools generator, and cpuset utilities.

Risks: tests use filesystem fixtures and package-global mocks, so cleanup/reset is critical. Some cgroup operations are mocked and do not prove real kernel compatibility.

Test signals: strongest coverage in this subset for host-tuning behavior: IRQ disable/enable idempotence, housekeeping topology, PM QoS and governor restore, irqbalance restart/oneshot decisions, mask rollback, exec affinity and shared CPU env injection, nil hook vs high-performance hook vs default hook selection.
