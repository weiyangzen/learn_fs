# sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_pyxis.c

**Purpose:** Implements common PYXIS core-logic IRQ handling: a 32-bit enabled-mask controller for PCI interrupts above ISA, cascade to i8259, and initialization of level-triggered PYXIS IRQ descriptors.

**Important APIs/types/functions:** Exposes `pyxis_device_interrupt()` and `init_pyxis_irqs()`. Internal helpers/state are `cached_irq_mask`, `pyxis_update_irq_hw()`, `pyxis_enable_irq()`, `pyxis_disable_irq()`, `pyxis_mask_and_ack_irq()`, and `pyxis_irq_type`.

**Control flow:** Initialization disables all PYXIS interrupts, clears pending requests, performs an ISA interrupt-ack cycle, installs `pyxis_irq_type` for IRQs 16-47 except ignored ones, marks them level-triggered, and reserves IRQ 23 (`16 + 7`) as the ISA cascade. Device interrupt handling reads `PYXIS_INT_REQ`, filters with `cached_irq_mask`, and handles each set bit; bit 7 delegates to `isa_device_interrupt()`, all others call `handle_irq(16 + bit)`.

**State and persistence behavior:** Maintains a cached enabled mask and writes PYXIS INT_MASK/INT_REQ CSRs. No persistent state.

**Dependencies and integration points:** Depends on CIA/PYXIS core register macros, Alpha I/O barriers, i8259 cascade handling, and generic IRQ descriptors. Used by Pyxis-based system vectors.

**Risks:** Mask bit semantics are “1 means enabled,” unlike i8259. `init_pyxis_irqs()` tests `ignore_mask >> i` while iterating absolute IRQ numbers, so callers must pass an absolute-bit mask. Cascade handling assumes bit 7 is always ISA. Register write/readback ordering is required to force CSR effects.

**Test signals:** Boot a Pyxis platform, confirm IRQs 16-47 map and level flags are set, trigger ISA cascade and non-ISA PCI interrupts, test ignored IRQ mask behavior, and verify pending bits are cleared during init.
