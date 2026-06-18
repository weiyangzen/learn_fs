# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdcall.S

Purpose: brings the common Intel TDX TDCALL assembly implementation into the compressed kernel.

Important APIs and state: no new symbols are defined directly here beyond those from `../../coco/tdx/tdcall.S`, which implements low-level TDCALL/TDVMCALL entry mechanics.

Control flow: purely include-based at assembly time.

Dependencies and integration: consumed by compressed TDX support in `tdx.c` and by shared TDX hypercall code. It allows early decompressor code to use the same TDX ABI glue as the normal kernel CoCo TDX implementation.

Risks and test signals: ABI mismatches in the included assembly affect early TDX guest boot and port-I/O hypercalls. Build with `CONFIG_INTEL_TDX_GUEST`, boot a TDX guest, and verify early console/port I/O paths do not execute forbidden raw I/O instructions after detection.
