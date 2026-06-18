## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ce.h

Purpose: declares the Wi-Fi 7 CE configuration arrays exported by `ce.c`.

Important APIs/data: extern declarations cover target CE configs, target service-to-CE maps, and host CE configs for QCN9274, WCN7850, and IPQ5332.

Control flow: none; it is a data declaration header.

State and persistence: no state is owned. Consumers receive pointers to immutable static tables.

Dependencies/integration: requires common CE type declarations (`struct ce_pipe_config`, `struct service_to_pipe`, `struct ce_attr`) from included compilation context and is used by hardware parameter setup code.

Risks: missing declarations for new chips will force ad hoc externs or prevent hw table wiring. Array sizes are not declared here, so consumers must use matching count constants from hardware params.

Test signals: compile coverage when adding/changing chip CE tables and hardware init validation that selected arrays match expected sizes.
