# sources/distributed-fs/ceph-client/arch/mips/dec/kn02-irq.c

Purpose: implements the KN02 Control and Status Register interrupt chip used by DECstation 5000/200.

Important APIs: `init_kn02_irqs(int base)` masks CSR interrupts, assigns `kn02_irq_type` to KN02 IRQ lines, and records the IRQ base. `cached_kn02_csr` stores write-only CSR bits.

Control flow: unmask and mask set or clear interrupt-enable bits at offset `irq - base + 16`, write the cached CSR to hardware, and ack by masking plus I/O barrier.

State and integration: `cached_kn02_csr` persists as the software copy of write-only CSR bits. Dispatch assembly reads CSR status/mask and maps enabled bits to Linux IRQs via `asic_mask_nr_tbl`.

Risks and test signals: stale cache bits can disable unrelated CSR functionality. Test SCSI, Lance, DZ11, TurboChannel, and cascade interrupts on KN02, and confirm mask/unmask updates are reflected in hardware.
