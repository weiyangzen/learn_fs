# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_ttm.c

## Purpose

`vbox_ttm.c` initializes the VirtualBox DRM VRAM memory manager over PCI BAR 0 and installs write-combining for better framebuffer performance.

## Important APIs, Types, and Functions

- `vbox_mm_init`: obtains BAR base/size, adds a write-combining MTRR/PAT mapping with `devm_arch_phys_wc_add`, and calls `drmm_vram_helper_init` over `vbox->available_vram_size`.

## Control Flow

Probe calls this after hardware init has reduced available VRAM for the guest heap and VBVA buffers. The DRM VRAM helper then manages GEM VRAM allocations for framebuffers and scanout.

## State and Persistence Behavior

The DRM managed VRAM helper stores memory-manager state in the DRM device for the device lifetime. The write-combining mapping is devm-managed. This file stores no independent state.

## Dependencies and Integration Points

It depends on PCI resources, architecture WC setup, DRM VRAM helpers, and `vbox->available_vram_size` from `vbox_hw_init`. `vbox_mode.c` later allocates/uses GEM VRAM objects from this manager.

## Risks and Edge Cases

- WC setup failure is intentionally ignored for correctness but can reduce performance.
- The VRAM helper must not cover the guest heap/VBVA command area; correctness depends on `available_vram_size` being accurate.
- BAR size smaller than reported available VRAM would make initialization fail or map invalid ranges.

## Test Signals

Probe with different VRAM sizes, framebuffer allocation and mmap tests, write-combining performance/attribute checks, and failure injection for `drmm_vram_helper_init`.
