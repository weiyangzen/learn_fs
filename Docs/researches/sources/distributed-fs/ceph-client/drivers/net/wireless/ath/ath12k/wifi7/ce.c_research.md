## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ce.c

Purpose: defines Wi-Fi 7 Copy Engine configuration tables for supported chips. These tables tell firmware and host code how HTC/WMI/HTT/pktlog/diagnostic services map onto CE pipes and how large each host/target ring should be.

Important APIs/data: exports `ath12k_wifi7_target_ce_config_wlan_qcn9274`, `ath12k_wifi7_target_service_to_ce_map_wlan_qcn9274`, `ath12k_wifi7_host_ce_config_qcn9274`, and equivalent WCN7850/IPQ5332 arrays. Host CE attributes include callbacks such as `ath12k_htc_rx_completion_handler` and `ath12k_dp_htt_htc_t2h_msg_handler`.

Control flow: no executable control flow beyond static initialization. Runtime hardware setup selects arrays through hardware parameter tables elsewhere. Target CE configs are little-endian firmware-facing descriptors; service maps are terminated by an all-zero entry; host configs size source/destination rings and opt selected pipes out of interrupts with `CE_ATTR_DIS_INTR`.

State and persistence: tables are constant kernel data. Runtime CE rings are allocated elsewhere from these templates.

Dependencies/integration: depends on common `ce.h`, `core.h`, service IDs, CE direction constants, and RX/HTC callbacks. It integrates with QMI target configuration, CE pipe allocation, HIF service-to-pipe mapping, and firmware boot.

Risks: table/index mismatches can break firmware communication early in boot. Some pipes are reserved for MHI, IPA, CV prefetch, or autonomous memcpy; using the wrong ring count/callback can cause interrupt storms, dropped WMI, or silent HTT loss. WCN7850 pktlog host CE5 has zero destination entries despite target CE5 pktlog, which should match product capability expectations.

Test signals: boot each chip, validate WMI control/data, HTT data path, pktlog/diag services, CE interrupt masking, and service-to-pipe lookup for every service ID in the tables.
