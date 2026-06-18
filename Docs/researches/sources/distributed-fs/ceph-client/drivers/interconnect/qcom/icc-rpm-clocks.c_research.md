# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpm-clocks.c

Purpose: const SMD RPM bus clock resource descriptors used by legacy Qualcomm interconnect drivers.

Important APIs/types/functions: exports descriptors for aggregate, BIMC/memory, bus, MMAXI, QUP, and aggregate branch clocks.

Control flow: legacy topology descriptors reference these constants; `icc-rpm.c` sends rates for the referenced RPM resource type and clock ID.

State and persistence: const module data only.

Dependencies/integration: SMD RPM resource IDs and `struct rpm_clk_resource`.

Risks and test signals: validate resource type/ID pairs, branch clock behavior, and exported symbols under module builds.
