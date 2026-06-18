<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_rom.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_rom.h

## Purpose
`intel_rom.h` declares the opaque option ROM access API used by i915 display BIOS/VBT parsing code.

## Important APIs, Types, And Functions
It forward-declares `struct intel_rom` and `struct drm_device`, then declares constructors for SPI and PCI ROM transports plus read, block-read, signature-find, size, and free functions.

## Control Flow
No executable flow exists in the header. Callers construct a ROM object with one transport, inspect size/find signatures/read blocks, then release it with `intel_rom_free()`.

## State And Persistence Behavior
The header makes `struct intel_rom` opaque, forcing callers to use the accessor API and keeping transport-specific state private to the implementation.

## Dependencies And Integration Points
It includes Linux types for `u32`, `u16`, `loff_t`, and `size_t`. The primary integration point is `intel_bios.c`.

## Risks
The API returns raw integer reads without explicit error returns, so construction failure and offset validation are caller responsibilities. Callers must always pair successful construction with `intel_rom_free()`.

## Test Signals
Build coverage validates declaration consistency. Runtime signals include VBT load success, fallback behavior across ROM transports, and absence of leaked PCI ROM mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_rom.h -->
