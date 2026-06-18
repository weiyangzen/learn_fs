<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10.h

## Purpose
`solo6x10.h` is the main internal interface for the SOLO6x10 driver, defining device constants, shared structures, register helpers, IRQ helpers, and subsystem prototypes.

## Important APIs, Types, and Functions
It defines PCI IDs, device type constants, channel/I2C/P2M/encoder constants, custom V4L2 controls, motion-grid sizing, `enum SOLO_I2C_STATE`, `struct solo_p2m_desc`, `struct solo_p2m_dev`, `struct solo_vb2_buf`, `enum solo_enc_types`, `struct solo_enc_dev`, and the central `struct solo_dev`. Inline helpers `solo_reg_read()`, `solo_reg_write()`, `solo_irq_on()`, and `solo_irq_off()` are used throughout the driver.

## Control Flow
The header has no independent control flow, but its prototypes define subsystem lifecycle ordering: display, GPIO, I2C, P2M, V4L2 display, encoder core, encoder V4L2, G.723 audio, ISR handlers, I2C byte access, P2M DMA, video standard setting, motion thresholds, OSD, EEPROM, and JPEG QP helpers.

## State and Persistence
`struct solo_dev` aggregates all runtime state for PCI, MMIO, IRQ masks, V4L2, GPIO, TW28 detection, I2C transfer progress, P2M engines, display capture, encoder nodes, current video geometry, JPEG QP, ALSA audio, sysfs SDRAM, ring threads, VOP header DMA, and active buffer lists. The header itself persists nothing.

## Dependencies and Integration Points
It includes kernel PCI/I2C/mutex/list/wait/atomic/slab/video/gpio headers and V4L2/vb2 media headers, plus the register map. Every SOLO subsystem includes this file.

## Risks and Edge Cases
Because this is a broad shared header, changes to `struct solo_dev` or inline IRQ/register helpers have driver-wide impact. `solo_reg_write()` reads PCI status after every MMIO write, likely as a posting flush; removing it could alter hardware timing. `irq_mask` updates are not internally locked, so callers rely on higher-level serialization or low contention.

## Test Signals
Full driver build, probe/remove, suspend-style teardown if available, all subsystem init/exit paths, IRQ mask behavior under concurrent audio/video/I2C/P2M use, and ABI-sensitive V4L2/ALSA/gpio behavior are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10.h -->
