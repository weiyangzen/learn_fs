<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-ppmu.h -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-ppmu.h

Purpose: defines register offsets, counter IDs, event encodings, operating modes, and bit masks for Exynos PPMU v1.1 and v2.0 blocks.

Important APIs and control flow: enums identify enable/disable state, four PM counters, v1 event types such as read/write data/request/busy/latency counts, v1 register offsets, v2 modes, v2 event types, and v2 register offsets. Macros define PMNC reset/enable bits, counter masks, and indexed register helpers `PPMU_PMNCT()`, `PPMU_BEVTxSEL()`, `PPMU_V2_PMNCT()`, and `PPMU_V2_CH_EVx_TYPE()`.

State and persistence behavior: none at runtime; this header fixes the register ABI used by the PPMU provider.

Dependencies and integration points: included by `exynos-ppmu.c`. It depends on `BIT()` through the including kernel headers.

Risks and test signals: duplicated PMNC macro names in v1 and v2 sections are currently identical but can hide hardware-version differences. Any offset or mask error changes measured load and governor decisions. Test signals are register programming traces for v1/v2, counter reset and enable bits matching datasheets, and event type values matching DT bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-ppmu.h -->
