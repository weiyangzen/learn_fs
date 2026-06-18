
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/random.c

Purpose: obtains entropy from EFI RNG and optional EFI variables, then installs a Linux random seed configuration table for kernel RNG initialization and kexec continuity.

Important APIs/types/functions: exports `efi_get_random_bytes()` and `efi_random_get_seed()`. Defines a local mixed-mode `efi_rng_protocol_t`.

Control flow: direct random bytes locate EFI RNG Protocol and call `get_rng`. Seed installation locates RNG, probes a `RandomSeed` EFI variable, merges a prior bootloader seed table if small, allocates ACPI reclaim memory, tries raw RNG then any RNG algorithm, reads and deletes the nonvolatile seed variable when present, appends prior seed data, installs `LINUX_EFI_RANDOM_SEED_TABLE_GUID`, and wipes/free old or failed seed buffers.

State and persistence behavior: installed seed table persists into the kernel and across kexec while the old table is zeroed/freed after replacement. The `RandomSeed` EFI variable is consumed and deleted. No local static state remains.

Dependencies and integration points: depends on EFI RNG Protocol, EFI variable runtime calls in boot context, config-table lookup/install, and `memzero_explicit()`. Called by common and x86 EFI paths.

Risks and test signals: entropy can be unavailable, raw algorithm unsupported, EFI variable deletion may not erase storage, and corrupted prior seed size is capped. Test signals include RNG present/absent, raw unsupported fallback, `RandomSeed` variable consumption, prior seed concatenation, installed table size, and buffer zeroing on failure.
