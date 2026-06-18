# sources/distributed-fs/ceph-client/arch/x86/lib/copy_user_uncached_64.S

Purpose: implements `copy_to_nontemporal`, an exception-aware uncached/non-temporal copy routine used when copying user data into destinations where kernel writes may machine-check or should bypass cache.

Important APIs/functions: exports `copy_to_nontemporal`. Inputs are `%rdi` destination, `%rsi` source, `%edx` byte count; return `%rax` is uncopied bytes. It uses aligned `movnti` stores for 32/64-bit chunks and normal stores for small unaligned pieces.

Control flow: the function first aligns the destination to 8 bytes, then performs 64-byte unrolled loops of eight loads and eight non-temporal stores. It falls back to qword, dword, word, and byte tails and issues `sfence` before cached tail stores. Exception table fixups distinguish first-half load faults, second-half load faults after 32 bytes have been stored, write faults at each store offset, alignment faults, and a final 4-byte retry path.

State and persistence behavior: writes destination memory partially or fully and returns the remaining count. Non-temporal writes affect cache persistence/order and require `sfence` before completion.

Dependencies/integration points: used by uncached usercopy/nocache paths and machine-check-sensitive copy code. Depends on uaccess exception tables, x86 non-temporal store semantics, and caller-managed user access state.

Risks: exception recovery is intricate; incorrect offset fixups over- or under-report copied bytes. Missing `sfence` can leave non-temporal stores unordered. The code intentionally avoids byte probing after some fatal-looking faults, so callers must handle nonzero returns.

Test signals: usercopy fault injection at every extable site, unaligned destination tests, non-temporal ordering tests where practical, and machine-check/poison copy paths.
