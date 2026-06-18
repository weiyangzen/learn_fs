# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-config.h

## Purpose
`coresight-config.h` defines the generic data model for CoreSight system configurations: feature descriptors, configuration descriptors, per-device feature/config instances, register value descriptors, parameter instances, and feature load operations.

## Important APIs, Types, And Functions
Register flags describe standard/resource registers, parameter-backed values, masks, 64-bit values, and save-on-disable behavior. Match flags select device classes such as all sources or ETMv4 sources. `struct cscfg_parameter_desc` describes a named parameter. `struct cscfg_regval_desc` combines a compact bitfield register identity with value/mask/parameter-index storage.

`struct cscfg_feature_desc` defines a reusable feature and its register/parameter descriptors. `struct cscfg_config_desc` defines a system configuration that references features and may provide presets. Runtime structures `cscfg_regval_csdev`, `cscfg_parameter_csdev`, `cscfg_feature_csdev`, and `cscfg_config_csdev` bind descriptors to a specific `coresight_device` and its driver storage. `struct cscfg_csdev_feat_ops` lets devices load compatible features. Public helper prototypes cover enable, disable, and feature reset.

## Control Flow
The header has no executable control flow, but it encodes the lifecycle: descriptors are loaded into runtime per-device instances; configs reference loaded features; activation copies parameter/preset values to driver storage; disable can save volatile register state.

## State And Persistence
Descriptor objects are typically static or dynamically loaded metadata. Runtime instances persist per CoreSight device and track current parameter values, whether a config is enabled, and active counts. Config descriptors also carry configfs-related fields and an `available` flag used by multi-stage loading.

## Dependencies And Integration Points
The header depends on `linux/coresight.h`, configfs-visible `struct config_group`, and kernel list/dev-ext-attribute types. It is shared by descriptor providers, syscfg loading code, device-specific feature loaders, and generic config programming code.

## Risks
The compact bitfield layout restricts offsets and hardware info to 12 bits each; descriptors for larger offset spaces would not fit. `struct cscfg_config_csdev` uses a flexible array of feature pointers, so allocation size must be exact. The preset limit is tied to perf event config field width, making ABI changes non-local.

## Test Signals
Compile coverage across config providers is important. Runtime tests should validate descriptor load/unload, configfs exposure, preset limits, active counts, flexible-array allocation, and device match filtering.
