# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.c

## Purpose
`iceland_ih.c` implements the VI/Iceland interrupt-handler IP block. It configures the hardware interrupt ring, provides ring pointer management and interrupt-vector decoding, initializes AMDGPU IRQ software state, and exports `iceland_ih_ip_block`.

## Important APIs, Types, And Functions
The IP lifecycle is in `iceland_ih_ip_funcs`: early/software/hardware init and fini, suspend/resume, idle polling, soft reset, and no-op clock/power gating. `iceland_ih_funcs` provides the IH ring callbacks `get_wptr`, `decode_iv`, and `set_rptr`. Core helpers include `iceland_ih_irq_init()`, `iceland_ih_irq_disable()`, `iceland_ih_enable_interrupts()`, `iceland_ih_disable_interrupts()`, `iceland_ih_get_wptr()`, and `iceland_ih_decode_iv()`.

## Control Flow
`early_init` creates the IRQ domain and installs IH callbacks. `sw_init` allocates the 64 KiB hardware IH ring, creates the software IH ring, and initializes IRQ sources. `hw_init` disables interrupts, programs dummy-page and interrupt control registers, writes ring base and writeback addresses, configures ring size and overflow handling, clears rptr/wptr, sets MSI rearm behavior when enabled, calls `pci_set_master`, enables the ring, and marks the software ring enabled if present.

Runtime interrupt processing asks `get_wptr` for the current write pointer, which prefers writeback memory, checks and clears overflow on the hardware ring, advances `rptr` to a catch-up position after overflow, and masks the pointer. `decode_iv` reads four dwords from the ring, fills legacy client ID, source ID, source data, ring ID, VMID, and PASID, then advances `rptr` by 16 bytes. `set_rptr` writes the hardware read pointer.

## State And Persistence
State lives in `adev->irq.ih`, `adev->irq.ih_soft`, their ring buffers, writeback memory, read pointers, enabled flags, IRQ domain state, and IH hardware registers. On disable, hardware and software rptr/wptr state is reset to zero. No disk persistence is involved.

## Dependencies And Integration Points
The file depends on OSS/BIF VI register headers, PCI bus mastering, AMDGPU IH and IRQ core, ring allocation helpers, dummy-page allocation from the device, MSI state, and SRBM reset/status registers. It integrates with the global IRQ processing path through `adev->irq.ih_funcs`.

## Risks And Test Signals
Risks include incorrect ring size encoding, bad writeback address programming, overflow recovery losing vectors, MSI rearm mismatch, rptr/wptr byte-versus-dword mistakes, and reset while interrupts are live. Test signals are interrupt delivery under MSI and non-MSI, ring overflow stress, suspend/resume, IRQ domain setup/teardown, soft reset when IH busy, and VM fault IRQ delivery through the decoded legacy IV format.
