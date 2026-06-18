# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/wmi.c

## Purpose

`wmi.c` initializes firmware resource configuration for Wi-Fi 7 ath12k hardware families. It fills `struct ath12k_wmi_resource_config_arg` differently for QCN9274-style full chips and WCN7850/QCC2072-style client chips before WMI init commands are sent to firmware.

## Important APIs And Functions

`ath12k_wifi7_wmi_init_qcn9274()` sizes resources from `ab->num_radios`, target constants, and `ath12k_core_get_max_peers_per_radio()`. It configures vdevs, peers, offload peers/reorder buffers, peer keys, AST skid, chain masks, RX timeouts, decap mode (raw or native Wi-Fi depending on `ATH12K_FLAG_RAW_MODE`), scan/roam/beacon/EMA settings, multicast/WDS/DMA resources, TWT AP counts, peer map/unmap version `0x32`, and peer metadata version `ATH12K_PEER_METADATA_V1B` when supported.

`ath12k_wifi7_wmi_init_wcn7850()` uses smaller fixed client-oriented resources: four vdevs, 16 peers, 32 TIDs, native Wi-Fi decap, zero multicast-to-unicast/WDS/DMA burst values, GTK/beacon offload limits of two, `num_msdu_desc = 0x400`, peer map/unmap version `0x1`, `use_pdev_id = 1`, TDLS/WOW/multicast-filter limits, and peer metadata version V1A if supported or the firmware-reported DP peer metadata version otherwise.

## Control Flow And Integration

`hw.c` stores one of these functions in `ath12k_hw_params.wmi_init`. During firmware initialization, common WMI code calls the selected function with the device base and a resource config structure, then sends that populated configuration to firmware. The functions are pure initializers with no allocation and no return value.

## State And Persistence Behavior

The functions mutate only the supplied resource config argument. The resulting values persist in firmware after WMI init and affect target resource allocation, peer/vdev capacity, RX decapsulation, offloads, multicast behavior, TWT/EMA capabilities, peer metadata format, and WOW/TDLS support. They also read runtime state such as `ab->target_caps.num_rf_chains`, `ab->dev_flags`, `ab->wmi_ab.svc_map`, and `ab->wmi_ab.dp_peer_meta_data_ver`.

## Dependencies

The file includes `../core.h` and local `wmi.h`. It depends on many common WMI target constants, service bits, ath12k base fields, and raw-mode flags. It integrates with `hw.c` hardware parameter selection and shared WMI firmware boot code.

## Risks And Edge Cases

Wrong resource sizing can cause firmware init failures or later peer/vdev exhaustion. QCN9274 scales several values by radio count; WCN7850 uses fixed small limits, so assigning the wrong initializer to hardware would be visible quickly. Peer metadata version selection is service-bit dependent and must match DP RX peer metadata parsing. Raw mode is honored for QCN9274 but WCN7850 forces native Wi-Fi decap, which is intentional but should be tested if raw-mode support changes.

## Test Signals

Firmware boot should accept the resource config on each hardware family. Functional tests should cover max vdev/peer creation near limits, raw mode on QCN9274, native Wi-Fi RX on WCN7850, peer map/unmap events, metadata parsing, WOW filters, TDLS entries, GTK offload, beacon offload, scan/roam limits, and TWT/EMA AP behavior where supported.
