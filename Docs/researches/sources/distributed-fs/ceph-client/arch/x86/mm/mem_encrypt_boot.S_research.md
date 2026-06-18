# sources/distributed-fs/ceph-client/arch/x86/mm/mem_encrypt_boot.S

## Purpose
This assembly file provides the position-independent AMD SME routine that encrypts kernel memory in place during early boot, while running from a decrypted work area outside the kernel image being transformed.

## Important APIs, Types, and Functions
- `__pi_sme_encrypt_execute` is the external entry point. It receives encrypted and decrypted virtual aliases, length, workarea virtual address, and encryption page-table physical address.
- Local routine `__enc_copy` is copied into the workarea and performs the actual CR3 switch and chunked copy.

## Control Flow and State
The entry point saves the original stack, switches to a one-page workarea stack, copies `__enc_copy` into the workarea, prepares arguments, and calls the copied routine. `__enc_copy` loads the encryption page tables into CR3, toggles CR4.PGE to flush global TLBs, changes PAT PA5 to write-protected, executes `wbinvd`, then copies up to 2 MiB at a time from the decrypted alias to an intermediate buffer and back through the encrypted alias. It restores PAT state and returns with unret annotations.

## Dependencies and Integration Points
It depends on x86 control registers, PAT MSR encoding, page size constants, retpoline/unret annotations, and the C-side SME early boot setup that prepares aliases, workarea, and page tables. It is part of the SME encrypt-in-place path used before normal kernel execution can assume encrypted contents.

## Risks
This code runs while the kernel image may be in transition between decrypted and encrypted states, so it cannot rely on normal kernel text or stack. Incorrect CR3, PAT, or cache ordering can corrupt the kernel image. The copied routine must remain position-independent and avoid return-thunk offsets that are invalid from the workarea.

## Test Signals
SME-enabled boot is the main validation. Failures usually appear as immediate boot hangs or corrupted kernel execution after encryption. Review signals include objdump checks for position independence, correct workarea sizing, and preservation/restoration of PAT and stack state.
