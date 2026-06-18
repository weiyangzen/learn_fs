# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/bcm-voter.h

Purpose: header for Qualcomm RPMh BCM voter helper APIs.

Important APIs/types/functions: declares `of_bcm_voter_get()`, `qcom_icc_bcm_voter_add()`, and `qcom_icc_bcm_voter_commit()`.

Control flow: RPMh provider code includes this header to find a voter, enqueue BCMs, and flush votes.

State and persistence: no direct state; functions operate on persistent voter lists and `qcom_icc_bcm` vote arrays.

Dependencies/integration: command DB, RPMh, TCS, and `icc-rpmh.h`.

Risks and test signals: compile-test module exports and prototype drift with `icc-rpmh.h`.
