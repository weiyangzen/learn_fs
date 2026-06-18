# sources/distributed-fs/ceph-client/drivers/iommu/intel/Kconfig

## Purpose

`intel/Kconfig` defines Intel VT-d/DMAR IOMMU support options, including base DMA remapping, debugfs, SVM, default enablement, scalable mode defaults, floppy workaround, and performance events.

## Important APIs, Types, and Functions

- `DMAR_TABLE`, `DMAR_PERF`, `DMAR_DEBUG`: internal feature symbols.
- `INTEL_IOMMU`: main Intel DMA-remapping option selecting IOMMU APIs, Generic PT, x86-64 and VT-d second-stage formats, IOVA, IOPF, PCI ATS/PRI/PASID, SWIOTLB, and related state.
- `INTEL_IOMMU_DEBUGFS`: exposes internals and selects debug/perf support.
- `INTEL_IOMMU_SVM`: Shared Virtual Memory support selecting MMU notifier and IOMMU SVA.
- `INTEL_IOMMU_DEFAULT_ON`, `INTEL_IOMMU_FLOPPY_WA`, `INTEL_IOMMU_SCALABLE_MODE_DEFAULT_ON`, `INTEL_IOMMU_PERF_EVENTS`.

## Control Flow

These symbols drive which Intel IOMMU source files and features are compiled. Enabling `INTEL_IOMMU` pulls in the Generic PT stack and PCI capabilities needed for modern VT-d operation. Nested/scalable features are controlled by additional booleans and runtime hardware detection.

## State and Persistence Behavior

No runtime state is stored here. Configuration choices affect boot defaults, feature availability, and built object files.

## Dependencies and Integration Points

The main option depends on `PCI_MSI`, `ACPI`, and `X86`, and integrates with the Generic PT Kconfig in this work item. The Makefile uses these symbols to include Intel IOMMU modules.

## Risks and Edge Cases

- Debugfs option warns it is not for production.
- Default-on and scalable-mode default-on alter boot behavior unless overridden by kernel command-line options.
- The floppy workaround creates identity mapping for legacy ISA DMA behavior.

## Test Signals

Build and boot matrices should include Intel IOMMU on/off/default-on, scalable mode on/off, SVM, debugfs, perf events, and Generic PT format selection. Runtime signals include DMAR ACPI parsing, device DMA translation, ATS/PRI/PASID setup, and perf/debugfs availability.
