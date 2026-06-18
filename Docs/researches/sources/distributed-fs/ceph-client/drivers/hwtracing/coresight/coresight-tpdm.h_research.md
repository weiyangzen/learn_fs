# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpdm.h

## Purpose

`coresight-tpdm.h` defines the TPDM dataset register map, bit fields, dataset storage structures, sysfs attribute macros, and helper predicates used by the TPDM driver and by TPDA integration.

## Important APIs, Types, and Functions

The header covers CMB/MCMB registers, DSB registers, integration-test registers, PIDR0 dataset presence bits, maximum pattern/MSR/edge-control dimensions, and packing helpers for edge-control arrays. `struct dsb_dataset` stores DSB mode, edge controls, patterns, trigger patterns, MSRs, and timestamp/trigger flags. `struct cmb_dataset` stores trace mode, patterns, MSRs, timestamp flags, and MCMB lane settings. `struct tpdm_drvdata` is the persistent TPDM device state. `enum dataset_mem` and `struct tpdm_dataset_attribute` route generic sysfs handlers. Inline helpers identify TPDM CoreSight devices and static TPDM devices.

## Control Flow

The C driver uses macro-generated attributes to avoid hand-writing dozens of DSB/CMB sysfs entries. On enable, shadow structures defined here are translated into hardware register writes. TPDA uses `coresight_device_is_tpdm` when walking upstream topology and `coresight_is_static_tpdm` helps TPDM skip MMIO programming for static sources.

## State and Persistence Behavior

Dataset structures persist for the device lifetime and are reset, modified via sysfs, and consumed on enable. Array dimensions define the maximum persistent configuration exposed to userspace. The `traceid` field persists the last CoreSight path trace ID while enabled.

## Dependencies and Integration Points

The header integrates with CoreSight source subtype definitions, Linux bit macros, and TPDA. It encodes Qualcomm-specific firmware properties and hardware register layouts.

## Risks and Edge Cases

Macro-generated sysfs attributes make index correctness critical. Attribute visibility must stay aligned with dataset pointer allocation, otherwise show/store functions can dereference NULL dataset structs. Max constants and bit masks must match hardware; expanding hardware support requires careful ABI handling for existing sysfs names.

## Test Signals

Compile coverage should verify all generated attributes. Runtime tests should validate edge-control packing, CMB/MCMB lane masks, DSB mode masks, MSR visibility limits, static TPDM predicate behavior, and TPDA recognition of TPDM devices.
