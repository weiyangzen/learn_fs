
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/intrinsics.c

Purpose: provides minimal memory intrinsics for the EFI stub, using firmware copy/set services before ExitBootServices and local byte loops afterward or when boot services are unavailable.

Important APIs/types/functions: exports `memcpy()`, `memmove()` as an alias, `memset()`, and `memcmp()`. Under KASAN it aliases compiler-emitted `__memcpy`, `__memmove`, and `__memset`.

Control flow: `memcpy()` checks whether boot services are available; before EBS it delegates to `boottime->copy_mem`, otherwise it uses overlap-safe `efistub_memmove()`. `memset()` similarly delegates to `boottime->set_mem` or a local loop. `memcmp()` compares byte-by-byte.

State and persistence behavior: no independent state. Behavior depends on the current validity of `efi_system_table->boottime`.

Dependencies and integration points: depends on EFI system table access and arch string declarations. It backs many stub files that cannot rely on full kernel libc.

Risks and test signals: `memcpy()` is overlap-safe because it uses memmove semantics locally, but firmware `copy_mem` semantics must also be valid for its callers. Test signals include pre/post-EBS copy and memset, overlapping ranges, KASAN builds, and compiler intrinsic emission.
