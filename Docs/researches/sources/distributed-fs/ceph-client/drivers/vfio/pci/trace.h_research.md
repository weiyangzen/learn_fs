# sources/distributed-fs/ceph-client/drivers/vfio/pci/trace.h

Purpose: defines VFIO PCI tracepoints for mmap and mmap fault diagnostics.

Important APIs: trace events `vfio_pci_nvgpu_mmap_fault`, `vfio_pci_nvgpu_mmap`, and `vfio_pci_npu2_mmap` capture PCI device name, host physical address, user address, mapping size when applicable, and return status.

Control flow and integration: standard Linux tracepoint header pattern declares `TRACE_SYSTEM vfio_pci`, event payloads, print formats, and includes `trace/define_trace.h` outside the include guard. `TRACE_INCLUDE_PATH` points back to the driver source directory.

State and persistence: tracepoints persist only in tracing buffers when enabled; they do not change device state.

Dependencies and risks: depends on tracepoint infrastructure and `struct pci_dev`. Event names include older NVGPU/NPU2 mapping flows; userspace tooling may depend on field names. Incorrect include path breaks trace generation.

Test signals: compile with tracing enabled, validate trace event format files under tracefs, and exercise mmap fault paths in drivers that call these tracepoints.
