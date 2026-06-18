# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kdump.h

Purpose: Declares PowerPC kdump/crash-dump helpers and constants for detecting and preparing crash kernels.

Important APIs, types, and functions: Provides crash dump macros and declarations such as kdump state checks, reserve/setup helpers, and architecture-specific crash memory handling when crash dump support is configured.

Control flow: Boot code reserves crash kernel memory, crash paths prepare CPU/register state and memory metadata, and kdump kernels identify that they are running as a dump capture kernel.

State and persistence: Runtime state includes reserved crash memory and crash flags. Dump output persistence is handled outside this header by kdump tooling.

Dependencies and integration points: Integrates kexec, crash reserve, FDT/elfcorehdr setup, RTAS/OPAL/platform crash code, and CPU stop/IPI flows.

Risks: Reserved ranges must not overlap normal allocations. Crash context is fragile, with interrupts/CPUs possibly broken. Hotplug memory/CPU changes must update dump metadata where supported.

Test signals: Crashkernel reservation, panic-to-kdump boot, elfcorehdr validity, CPU hotplug crash metadata, memory hotplug, and builds with crash dump disabled.
