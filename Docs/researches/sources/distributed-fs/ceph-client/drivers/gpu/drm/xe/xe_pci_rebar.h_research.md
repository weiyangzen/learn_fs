<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_rebar.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_rebar.h

## Purpose

`xe_pci_rebar.h` exposes the single ReBAR resize hook used by PCI probe.

## Important APIs

`xe_pci_rebar_resize(struct xe_device *xe)` attempts to resize the local-memory BAR based on the `force_vram_bar_size` module parameter or the maximum supported ReBAR size. The header forward-declares `struct xe_device` and has no inline behavior.

## Control Flow and State

The header itself is stateless. Calling the function can change PCI BAR resource sizing and bus resource assignment.

## Dependencies and Integration Points

The only consumer in this subset is `xe_pci.c`, which calls it during probe after early descriptor setup.

## Risks and Test Signals

The contract is intentionally best-effort and non-fatal. Compile-time tests should ensure only PCI-facing code includes it, while runtime tests should verify that unsupported platforms continue probing with the original BAR size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_rebar.h -->
