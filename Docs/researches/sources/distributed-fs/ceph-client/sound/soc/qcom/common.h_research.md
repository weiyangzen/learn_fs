# sources/distributed-fs/ceph-client/sound/soc/qcom/common.h

Purpose: declares shared Qualcomm ASoC machine-driver helper APIs and LPASS port sizing.

Important APIs/types/functions: defines `LPASS_MAX_PORT` as `SENARY_MI2S_TX + 1`. Declares `qcom_snd_parse_of`, `qcom_snd_wcd_jack_setup`, and `qcom_snd_dp_jack_setup`.

Control flow: no executable flow; machine drivers call these helpers during probe/runtime init.

State and persistence: no state in the header.

Dependencies and integration: includes QCOM LPASS dt-bindings so `LPASS_MAX_PORT` tracks DAI IDs. Used by APQ8016, APQ8096, and other Qualcomm cards.

Risks: `LPASS_MAX_PORT` depends on binding enum ordering; changes to dt-bindings can affect array sizing. Helper signatures must match common.c exports.

Test signals: compile coverage of all Qualcomm machine drivers and array bounds checks in users that size per-port state from `LPASS_MAX_PORT`.
