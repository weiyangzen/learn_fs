# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/imc-pmu.h

Purpose: Defines In-Memory Collection PMU structures and constants for PowerNV/PowerPC performance monitoring units backed by OPAL IMC metadata.

Important APIs, types, and functions: Describes IMC domain/type constants, event and counter metadata structures, memory block descriptors, per-PMU data, and helper prototypes for IMC PMU registration and event handling.

Control flow: Platform code discovers IMC catalog data, builds PMU instances and event tables, maps counter memory, registers perf PMUs, and perf event operations read/update counters.

State and persistence: Runtime state includes mapped IMC memory, PMU/event descriptors, active event state, and per-CPU/chip metadata. It is not persistent across reboot.

Dependencies and integration points: Depends on perf PMU core, OPAL IMC catalog/memory interfaces, CPU/chip topology, and PowerNV platform code.

Risks: Catalog parsing and counter offsets are firmware ABI-sensitive. Counter memory may be per-core/chip/thread and needs correct affinity. Hotplug and memory mapping lifetime must be synchronized with perf events.

Test signals: IMC catalog discovery, perf list/stat for core/chip/thread PMUs, CPU hotplug, counter wraparound, invalid event IDs, and firmware absence/failure paths.
