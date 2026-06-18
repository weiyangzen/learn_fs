# sources/distributed-fs/ceph-client/drivers/iommu/intel/Makefile

## Purpose

The Intel IOMMU Makefile lists object files built for VT-d support and gates optional files by Kconfig symbols.

## Important APIs, Types, and Functions

- Core `obj-y`: `iommu.o`, `pasid.o`, `nested.o`, `cache.o`, and `prq.o`.
- `CONFIG_DMAR_TABLE`: adds `dmar.o` and `trace.o`.
- `CONFIG_DMAR_PERF`: adds `perf.o`.
- `CONFIG_INTEL_IOMMU_DEBUGFS`: adds `debugfs.o`.
- `CONFIG_INTEL_IOMMU_SVM`: adds `svm.o`.
- `CONFIG_IRQ_REMAP`: adds `irq_remapping.o`.
- `CONFIG_INTEL_IOMMU_PERF_EVENTS`: adds `perfmon.o`.

## Control Flow

Kbuild includes core Intel IOMMU code whenever the directory is selected, then adds optional features based on symbols from `intel/Kconfig` and common IRQ-remap config.

## State and Persistence Behavior

No runtime state exists. Build composition controls which runtime subsystems are present.

## Dependencies and Integration Points

It ties Intel IOMMU Kconfig symbols to source objects and ensures `cache.o`, the cache-tag implementation in this work item, is always part of the core Intel IOMMU build.

## Risks and Edge Cases

Object ordering can matter for initcall/link dependencies in built-in code. Optional trace/perf/debug files must only reference symbols available under their Kconfig gates.

## Test Signals

Run compile tests for minimal Intel IOMMU, with DMAR table parsing, debugfs, SVM, IRQ remapping, and perf events toggled individually and together.
