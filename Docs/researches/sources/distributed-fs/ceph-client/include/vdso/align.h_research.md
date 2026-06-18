<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/align.h -->
# sources/distributed-fs/ceph-client/include/vdso/align.h

Purpose: supplies vDSO-safe alignment macros for integer and pointer values without depending on broader kernel alignment headers.

Important APIs and types: `ALIGN`, `ALIGN_DOWN`, `__ALIGN_MASK`, `PTR_ALIGN`, `PTR_ALIGN_DOWN`, and `IS_ALIGNED` wrap kernel constant alignment helpers from `vdso/const.h`.

Control flow: vDSO and VVAR layout code uses these macros when sizing pages, aligning architecture data, and validating power-of-two boundaries.

State and persistence: no state; pure preprocessor helpers.

Dependencies and integration points: depends on `vdso/const.h` and the UAPI constant macros it exposes. It integrates with `vdso/datapage.h` and low-level arch vDSO code that cannot include heavy kernel headers.

Risks and test signals: risks include non-power-of-two `a`, pointer truncation through `unsigned long`, and type surprises in `IS_ALIGNED`. Test vDSO builds on 32/64-bit architectures and page/alignment calculations for VVAR symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/align.h -->
