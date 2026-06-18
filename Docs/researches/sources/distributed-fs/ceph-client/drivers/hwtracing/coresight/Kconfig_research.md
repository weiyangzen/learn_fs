# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/Kconfig

## Purpose
This Kconfig file defines the Arm CoreSight tracing framework and its component drivers, including links, sinks, sources, trace buffers, CTI/CTM, STM integration, TPDM/TPDA, TNOC, dummy devices, and KUnit tests.

## Important APIs, Types, And Functions
This is declarative Kconfig. Major symbols include `CORESIGHT`, `CORESIGHT_LINKS_AND_SINKS`, `CORESIGHT_LINK_AND_SINK_TMC`, `CORESIGHT_CATU`, `CORESIGHT_SINK_TPIU`, `CORESIGHT_SINK_ETBV10`, `CORESIGHT_SOURCE_ETM3X`, `CORESIGHT_SOURCE_ETM4X`, `ETM4X_IMPDEF_FEATURE`, `CORESIGHT_STM`, `CORESIGHT_CTCU`, `CORESIGHT_CPU_DEBUG`, `CORESIGHT_CPU_DEBUG_DEFAULT_ON`, `CORESIGHT_CTI`, `CORESIGHT_CTI_INTEGRATION_REGS`, `CORESIGHT_TRBE`, `ULTRASOC_SMB`, `CORESIGHT_TPDM`, `CORESIGHT_TPDA`, `CORESIGHT_DUMMY`, `CORESIGHT_KUNIT_TESTS`, and `CORESIGHT_TNOC`.

## Control Flow
`menuconfig CORESIGHT` gates the rest of the file. The framework depends on ARM or ARM64, and OF or ACPI, and selects AMBA, perf events, and configfs support. Child symbols add component-specific dependencies and select related support where needed, such as ETM sources selecting links/sinks, ETM4 selecting `PID_IN_CONTEXTIDR`, STM selecting the generic `STM` subsystem, TPDM selecting TPDA, and KUnit tests defaulting under `KUNIT_ALL_TESTS`.

## State And Persistence
The file affects build-time symbol selection. Runtime CoreSight topology, trace sessions, sysfs/configfs state, perf integration, and device registrations are implemented by the object files selected here.

## Dependencies And Integration Points
It ties CoreSight to ARM/ARM64, OF/ACPI firmware descriptions, AMBA bus support, perf, configfs, debugfs for CPU debug, KUnit for tests, and component-specific dependencies such as TMC for CATU/CTCU and ETM4 for TRBE.

## Risks
- Symbol dependency mistakes can produce unusable trace topologies, such as sources without viable links/sinks or sinks without the framework.
- Several options are tristate and interdependent; module/built-in combinations need link and runtime testing.
- `CORESIGHT_CTI_INTEGRATION_REGS` intentionally exposes integration registers that can leave devices inconsistent, so it should remain gated and documented.
- `CORESIGHT_CPU_DEBUG_DEFAULT_ON` changes boot-time debug behavior and must be treated as a policy-sensitive option.

## Test Signals
Validate Kconfig combinations for ARM and ARM64, OF-only and ACPI-enabled builds, modular and built-in component combinations, ETM3 exclusion on ARM64, ETM4/TRBE dependencies, KUnit selection defaults, and that Makefile object selection matches every visible symbol.
