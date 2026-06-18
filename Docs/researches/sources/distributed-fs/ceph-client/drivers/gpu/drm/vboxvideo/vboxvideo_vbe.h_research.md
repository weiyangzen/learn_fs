# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vboxvideo_vbe.h

## Purpose

`vboxvideo_vbe.h` defines the legacy VirtualBox/Bochs VBE DISPI I/O-port interface and capability IDs used by the driver for probing and initial mode programming.

## Important APIs, Types, and Functions

- I/O ports: `VBE_DISPI_IOPORT_INDEX`, `VBE_DISPI_IOPORT_DATA`, DAC ports, `VGA_PORT_HGSMI_HOST`, and `VGA_PORT_HGSMI_GUEST`.
- Register indices: ID, X/Y resolution, BPP, enable, bank, virtual width/height, X/Y offset, VBox video command, and framebuffer base high.
- Interface IDs: Bochs IDs, `VBE_DISPI_ID_VBOX_VIDEO`, `VBE_DISPI_ID_HGSMI`, and `VBE_DISPI_ID_ANYX`.
- Enable flags: disabled, enabled, get caps, and 8-bit DAC.

## Control Flow

Probe and feature checks write an ID/register index then read or write data. CRTC 0 modeset code writes resolution, pitch, bpp, enable, and offsets for compatibility with older hosts. HGSMI submission writes command offsets to `VGA_PORT_HGSMI_GUEST`, and IRQ clear writes to `VGA_PORT_HGSMI_HOST`.

## State and Persistence Behavior

The constants address host-emulated device registers. Writes persist in the virtual graphics adapter until changed or reset.

## Dependencies and Integration Points

Used by `vbox_drv.h`, `vbox_main.c`, `vbox_mode.c`, `vbox_hgsmi.c`, and `vbox_irq.c`. Kconfig limits this to X86/PCI where port I/O is valid.

## Risks and Edge Cases

Incorrect index/data ordering can read or write the wrong virtual register. Values are ABI constants shared with VirtualBox and Bochs-compatible hosts.

## Test Signals

Probe supported IDs, legacy first-screen modeset behavior, HGSMI port submission, IRQ clearing, and ANYX capability handling under multiple VirtualBox versions.
