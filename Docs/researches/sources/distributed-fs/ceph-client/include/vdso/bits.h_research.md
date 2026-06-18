<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/bits.h -->
# sources/distributed-fs/ceph-client/include/vdso/bits.h

Purpose: provides minimal `BIT()` and `BIT_ULL()` macros suitable for vDSO code.

Important APIs and types: `BIT(nr)` uses `UL(1)` and `BIT_ULL(nr)` uses `ULL(1)` from `vdso/const.h`.

Control flow: vDSO data masks such as supported clock IDs use these macros at compile time.

State and persistence: no state; pure macros.

Dependencies and integration points: depends on `vdso/const.h`; used by `vdso/datapage.h` and other small vDSO headers.

Risks and test signals: risks include undefined shifts for out-of-range bit numbers and type-width assumptions. Test compile-time masks for clock IDs on all vDSO architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/bits.h -->
