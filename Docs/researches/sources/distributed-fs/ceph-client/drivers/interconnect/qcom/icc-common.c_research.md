# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-common.c

Purpose: Qualcomm extended OF xlate helper for optional path tags.

Important APIs/types/functions: exported `qcom_icc_xlate_extended()` wraps `of_icc_xlate_onecell()`, allocates `struct icc_node_data`, stores the node, and copies a second phandle argument as `tag`.

Control flow: providers assign it to `provider->xlate_extended`; the core uses returned source/destination tags when creating paths.

State and persistence: per-call allocation is freed by the core after path creation; no global state.

Dependencies/integration: OF phandle args, onecell xlate, memory allocation, Qualcomm tagged providers.

Risks and test signals: test one/two/too-many arguments, allocation failure, invalid node index, and source/destination tag mismatch.
