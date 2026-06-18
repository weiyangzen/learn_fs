# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_main.c

## Purpose

`vbox_main.c` performs VirtualBox graphics hardware/protocol initialization and finalization. It discovers VRAM size and host capabilities, maps the guest heap and VBVA buffers, initializes the gen_pool transport, reports guest capabilities, and enables per-screen VBVA acceleration buffers.

## Important APIs, Types, and Functions

- `vbox_report_caps`: sends VBVA capability bits, first without and then with mode-hint support for host compatibility.
- `vbox_accel_init` and `vbox_accel_fini`: reserve per-CRTC VBVA buffers at the end of usable VRAM, map them, initialize buffer contexts, and enable/disable them.
- `have_hgsmi_mode_hints`: queries mode-hint and guest-cursor reporting support.
- `vbox_check_supported`: probes VBE/VBox interface IDs through I/O ports.
- `vbox_hw_init` and `vbox_hw_fini`: top-level hardware setup and teardown.

## Control Flow

`vbox_hw_init` reads full VRAM size from the VBE data port, checks ANYX support, reserves PCI BAR 0, maps the guest heap at the end of VRAM, creates a 16-byte-granularity gen_pool over the usable guest heap, verifies HGSMI query behavior, sets available VRAM below the guest heap, queries monitor count, clamps it, requires mode hints and guest cursor reporting, allocates `last_mode_hints`, and enables VBVA acceleration buffers. Finalization disables all VBVA buffers.

## State and Persistence Behavior

It initializes persistent fields in `struct vbox_private`: `full_vram_size`, `available_vram_size`, `any_pitch`, `guest_heap`, `guest_pool`, `num_crtcs`, `last_mode_hints`, `vbva_info`, and `vbva_buffers`. It also establishes host-side capability and VBVA enable state until finalization or VM/device reset.

## Dependencies and Integration Points

It depends on PCI BAR mapping, gen_pool allocation, VBE I/O ports, VirtualBox HGSMI/VBVA protocol helpers, and `vbox_drv.h` VRAM layout macros. Mode setup and IRQ code assume this initialization has completed successfully.

## Risks and Edge Cases

- The code reads `full_vram_size` from the data port after earlier ID probing; the port index state must match host expectations.
- Available VRAM is reduced by guest heap and VBVA buffers; small VRAM configurations could underflow if host reports too many CRTCs.
- Older hosts without 4.3 mode-hint/cursor reporting are rejected.
- `vbox_accel_fini` assumes `vbva_info` and `num_crtcs` were initialized; partial init failure tolerance matters.

## Test Signals

Probe on VirtualBox versions with different capability sets, multiple monitor counts, small/large VRAM sizes, VBVA enable failure paths, capability reporting acceptance, and bind/unbind leak checks for gen_pool and mapped ranges.
