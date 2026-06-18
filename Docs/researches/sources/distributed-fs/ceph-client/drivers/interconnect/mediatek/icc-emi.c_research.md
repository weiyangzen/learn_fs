# sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/icc-emi.c

Purpose: common MediaTek EMI provider that translates interconnect votes into DVFSRC bandwidth requests.

Important APIs/types/functions: exports `mtk_emi_icc_probe()` and `mtk_emi_icc_remove()`. Provider callbacks are `mtk_emi_icc_aggregate()` and `mtk_emi_icc_set()`.

Control flow: probe reads OF match data, allocates provider/onecell data, creates non-NULL SoC nodes, creates links, registers provider, and stores driver data. Set sends normal peak/average requests for endpoint type 1 and HRT requests for endpoint type 2.

State and persistence: static SoC node structs hold mutable `sum_avg` and `max_peak`; provider nodes persist until remove.

Dependencies/integration: MediaTek DVFSRC, OF match data, onecell xlate, interconnect core.

Risks and test signals: test overflow saturation, DVFSRC errors, unknown endpoint values, sparse node arrays, active path removal, and unchecked `icc_link_create()` return values.
