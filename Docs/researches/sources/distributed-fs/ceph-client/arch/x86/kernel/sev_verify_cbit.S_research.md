# sources/distributed-fs/ceph-client/arch/x86/kernel/sev_verify_cbit.S

## Purpose
`sev_verify_cbit.S` verifies during early boot that the SEV C-bit position reported by the hypervisor is correct before switching to a new long-mode page table.

## Important APIs, Types, And Functions
The only symbol is `sev_verify_cbit(new_cr3)`, with the candidate CR3 in `%rdi` and the returned page-table pointer in `%rax`. It reads `sme_me_mask` and `sev_status`, and uses `sev_check_data` for the encrypted-memory comparison.

## Control Flow
If AMD memory encryption, SME mask, or SEV status are absent, it returns immediately. Otherwise it saves CR4, disables PGE, loops on `RDRAND` until a random value is available, stores it to encrypted memory, saves current CR3, switches to the new CR3, compares the value through the new mapping, restores CR3/CR4, and returns on success. On mismatch it invalidates the stack and enters a permanent `hlt` loop.

## State, Persistence, Dependencies, Integration
Temporary state is the random value in `sev_check_data`; CR3 and CR4 are restored on success. The code depends on SEV setup, the correctness of the current and candidate mappings for `sev_check_data`, mandatory SEV `RDRAND`, and early page-table transition code.

## Risks And Test Signals
Continuing after a bad C-bit would be unsafe, so failure intentionally halts. Stack and mapping assumptions are fragile during CR3 switching. Test valid SEV, intentionally bad C-bit guests, SME-only and unencrypted boots, CR4.PGE restoration, and return-value preservation.
