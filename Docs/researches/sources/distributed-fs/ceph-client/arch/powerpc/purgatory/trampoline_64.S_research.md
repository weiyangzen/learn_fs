<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/purgatory/trampoline_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/purgatory/trampoline_64.S

Purpose: 64-bit PowerPC kexec purgatory trampoline. It preserves a backup memory region, patches boot metadata, switches endian mode if needed, and branches into the next kernel.

Important APIs/types/functions: global `purgatory_start`, `run_at_load`, `kernel`, `dt_offset`, `backup_start`, `opal_base`, `opal_entry`, `purgatory_sha256_digest`, and `purgatory_sha_regions`. The first 0x100 bytes are ABI-controlled and replaced by setup code.

Control flow: execution branches from `purgatory_start` to `master`, saves CPU ID and physical address registers, computes the current PC, optionally copies `BACKUP_SRC_SIZE` bytes from `BACKUP_SRC_START` to `backup_start`, delays for secondary threads, updates the device-tree boot CPU field for v2+ flattened trees, loads OPAL and kernel addresses, patches the target kernel's `run_at_load` flag, restores the device-tree pointer in r3, clears r5, then either branches directly for big-endian or uses SRR0/SRR1 and `rfid` to clear MSR_LE before entering the kernel.

State and persistence: mutable fields are patched by kexec before execution: target kernel address, device tree offset, backup destination, OPAL base/entry, run-at-load flag, digest, and SHA region list. No normal kernel state survives except what the trampoline deliberately copies and passes in registers.

Dependencies and integration points: depends on PowerPC kexec ABI offsets, crashdump constants, flattened device tree layout, OPAL handoff conventions, and the generic kexec purgatory integrity machinery.

Risks: fixed `.org` ABI offsets are brittle. Copy loop assumes 8-byte granularity. Endian transition must clear only MSR_LE while preserving valid MSR bits. Device-tree version offsets must match the flattened tree ABI.

Test signals: ppc64 kexec and crash-kexec boots, little-endian-to-big-endian transition coverage, backup region verification, correct boot CPU in the FDT, and purgatory SHA validation are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/purgatory/trampoline_64.S -->
