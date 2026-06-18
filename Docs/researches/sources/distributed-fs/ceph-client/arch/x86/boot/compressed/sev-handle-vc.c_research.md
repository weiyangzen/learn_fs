# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sev-handle-vc.c

Purpose: provides the compressed-kernel #VC handler used after the GHCB page is available for SEV-ES/SNP guests. It supports the small instruction-emulation subset needed during decompression.

Important APIs and state: exports `do_boot_stage2_vc(struct pt_regs *regs, unsigned long exit_code)` and aliases `sev_insn_decode_init()` to `inat_init_tables`. Local helpers implement instruction decode, memory reads/writes, I/O checks, and stub segment handling for the included shared #VC handler. It includes `inat.c`, `insn.c`, and `coco/sev/vc-shared.c` into the compressed environment.

Control flow: the handler ensures `boot_ghcb` exists via `early_setup_ghcb()`, invalidates it, initializes an emulation context, verifies opcode bytes, dispatches RDTSC/RDTSCP, IOIO, and CPUID exits to shared handlers, advances RIP on success, retries on `ES_RETRY`, and terminates the guest for unsupported or failed exits.

Dependencies and integration: depends on `boot_ghcb`, GHCB setup from `sev.c`, Linux instruction decoder tables, and AMD SEV shared GHCB protocol definitions. It is installed only for early boot, before the full kernel exception and #VC infrastructure is live.

Risks and test signals: the supported exit set is intentionally narrow; new early instructions that can #VC must be added or boot will terminate. Tests are SEV-ES/SNP boots through decompression, CPUID exits using the SNP table, early port I/O, RDTSC handling, and negative tests confirming unsupported exits terminate rather than silently corrupting register state.
