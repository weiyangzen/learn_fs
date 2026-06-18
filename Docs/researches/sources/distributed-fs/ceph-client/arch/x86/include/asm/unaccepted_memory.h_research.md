# sources/distributed-fs/ceph-client/arch/x86/include/asm/unaccepted_memory.h

Purpose: architecture hook for accepting confidential-computing memory ranges and finding the EFI unaccepted-memory table.

Important APIs/types/functions: `arch_accept_memory(phys_addr_t start, phys_addr_t end)` and `efi_get_unaccepted_table()`.

Control flow: acceptance dispatches to TDX when `X86_FEATURE_TDX_GUEST` is present, to SEV-SNP when `CC_ATTR_GUEST_SEV_SNP` is set, and panics for unknown platforms. TDX failure also panics. EFI table lookup returns NULL if the firmware address is invalid, otherwise maps it with `__va()`.

State/persistence: reads EFI global table address and CPU/platform confidential-computing feature state. Memory acceptance changes platform-managed page state outside normal kernel RAM metadata.

Dependencies/integration: depends on EFI, TDX, SEV/SNP, CPU feature checks, and early memory initialization accepting pages before use.

Risks/test signals: accepting the wrong range or failing to accept before use can crash encrypted guests; silently accepting on unknown platforms would be unsafe. Test TDX and SEV-SNP boot paths, EFI unaccepted-memory table parsing, partial range acceptance, and failure/panic injection where practical.
