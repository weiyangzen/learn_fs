# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/wmi.h

## Purpose

`wmi.h` declares the Wi-Fi 7 hardware-family WMI resource initialization functions.

## Important APIs

It exports `ath12k_wifi7_wmi_init_qcn9274(struct ath12k_base *ab, struct ath12k_wmi_resource_config_arg *config)` and `ath12k_wifi7_wmi_init_wcn7850(struct ath12k_base *ab, struct ath12k_wmi_resource_config_arg *config)`. Both functions fill a caller-provided WMI resource config for firmware initialization.

## Control Flow And Integration

`hw.c` includes this header and stores the function pointers in `ath12k_hw_params`. Common WMI setup later calls the selected initializer for the active hardware revision before sending resource configuration to firmware.

## State And Persistence Behavior

The header owns no state. The declared functions mutate the resource config passed by the caller and indirectly determine persistent firmware resource allocation after boot.

## Dependencies

The header relies on declarations for `struct ath12k_base` and `struct ath12k_wmi_resource_config_arg` being available to includers. It is protected by `ATH12K_WMI_WIFI7_H`.

## Risks And Edge Cases

Prototype drift between this header and `wmi.c` would break hardware parameter assignment or common WMI calls. Callers must pass a valid, writable config structure; the functions do not report errors.

## Test Signals

Build coverage should ensure both prototypes match their definitions. Probe and firmware boot on QCN9274, WCN7850, and QCC2072 verify correct function pointer selection and valid WMI resource initialization.
