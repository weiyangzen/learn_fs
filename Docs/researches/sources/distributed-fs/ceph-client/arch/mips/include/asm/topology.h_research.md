# sources/distributed-fs/ceph-client/arch/mips/include/asm/topology.h

## Purpose

`topology.h` maps generic topology queries to MIPS `cpu_data`, sibling/core cpumasks, package/core IDs, and the primary-thread mask.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `topology.h`, `linux/smp.h`. Macros/constants: `__ASM_TOPOLOGY_H`, `topology_physical_package_id`, `topology_core_id`, `topology_core_cpumask`, `topology_sibling_cpumask`, `cpu_primary_thread_mask`. Types/enums/unions: `cpumask`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with scheduler topology, hotplug, and SMP sibling management.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 25 lines and 754 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
