# sources/distributed-fs/ceph-client/arch/x86/include/asm/posted_intr.h

Purpose: defines Intel posted-interrupt descriptor layout and helpers for manipulating posted interrupt request/control bits, including posted MSI support.

Important APIs, types, and functions: constants include `POSTED_INTR_ON`, `POSTED_INTR_SN`, `PID_TABLE_ENTRY_VALID`, `NR_PIR_VECTORS`, and `NR_PIR_WORDS`. `struct pi_desc` is a 64-byte aligned descriptor containing PIR bitmap and control fields `notifications`, `nv`, and `ndst`. Helpers include `pi_harvest_pir()`, atomic `pi_test_and_set_on()`, `pi_test_and_clear_on()`, `pi_test_and_clear_sn()`, `pi_test_and_set_pir()`, `pi_is_pir_empty()`, setters/clearers/testers for ON/SN/PIR bits, non-atomic `__pi_set_sn()`/`__pi_clear_sn()`, optional `pi_pending_this_cpu()`, and `intel_posted_msi_init()`.

Control flow: software harvest first reads all PIR words into a caller buffer and ORs them to avoid expensive cacheline bouncing; only nonzero words are then cleared with `arch_xchg()`. Control helpers manipulate bits in the descriptor control word. Posted MSI code checks the per-CPU posted MSI descriptor for pending external vectors.

State and persistence: `pi_desc` instances are runtime shared state between CPU, IOMMU, and virtualization code. No persistent storage exists.

Dependencies and integration points: depends on x86 interrupt vectors, bitmap helpers, atomic bitops, per-CPU `posted_msi_pi_desc`, IOMMU interrupt remapping, posted MSI, and KVM posted interrupts.

Risks: descriptor cacheline layout and harvesting order are performance-critical and concurrency-sensitive. CPU and IOMMU concurrently access the same cacheline. Vector validation in `pi_pending_this_cpu()` prevents invalid PIR reads.

Test signals: KVM posted-interrupt delivery, posted MSI interrupt remapping, PIR harvest with multiple vectors, suppress-notification behavior, IOMMU stress, CPU hotplug/per-CPU descriptor setup, and cacheline-aligned structure layout checks.
