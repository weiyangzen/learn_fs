# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/bcm-voter.c

Purpose: Qualcomm RPMh Bus Clock Manager voter. It aggregates BCM votes from interconnect providers, generates TCS commands, and writes active/wake/sleep RPMh batches.

Important APIs/types/functions: `struct bcm_voter` tracks device, DT node, lock, commit/wake-sleep lists, and wait mask. Exports `of_bcm_voter_get()`, `qcom_icc_bcm_voter_add()`, and `qcom_icc_bcm_voter_commit()`.

Control flow: providers find a voter via `qcom,bcm-voters`, queue dirty BCMs, and commit. Commit aggregates BCMs, sorts by VCD, writes active commands, then writes wake/sleep commands only for BCMs whose wake and sleep votes differ.

State and persistence: global `bcm_voters`; per-voter commit and wake/sleep lists; BCM vote arrays and aux data owned by provider descriptors.

Dependencies/integration: RPMh, TCS, command DB/RPMh interconnect structures, DT phandles, list sorting.

Risks and test signals: test VCD batching, payload boundaries, vote saturation, keepalive, enable-mask BCMs, wake/sleep deltas, missing voter deferral, `qcom,tcs-wait`, and concurrent commits.
