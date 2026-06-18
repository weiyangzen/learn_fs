# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dchubbub.h

## Purpose

`dchubbub.h` defines the common DCHUBBUB abstraction, the DCN data-fabric request/return and memory-arbitration block shared by pipes. It handles VM context, DCC capability, watermarks, self-refresh/p-state controls, DET/compbuf allocation, MALL, arbiter programming, and performance monitoring.

## Important APIs, Types, And Functions

Important types include DCC control/segment order enums, `dcn_hubbub_wm_set`, `dcn_hubbub_wm`, page-table depth/block-size enums, physical/virtual address configs, `hubbub_addr_config`, state/reg snapshots, latency/urgent params, nested perfmon/qos vtables, `hubbub_funcs`, and `hubbub`. Operations include DCHUB init/update, VM setup, DCC cap/support queries, watermark read/program/init/propagation, self-refresh and p-state controls, DET/compbuf programming, CRB/MALL helpers, arbiter programming, and performance/QoS measurement controls.

## Control Flow

During init, DC programs physical/virtual apertures and DCHUB context. Validation produces watermarks, DET sizes, compbuf sizes, mcache/arbiter data, and DCC decisions. Commit code programs watermarks with safe-to-lower semantics, applies DET/compbuf changes, controls self-refresh/p-state during transitions, and optionally reads performance counters for memory QoS.

## State And Persistence Behavior

`hubbub` persists in the resource pool and stores context plus RIOMMU-active state. Hardware persists VM tables, watermarks, DET/compbuf segmentation, DCHUB arbiter settings, self-refresh/p-state controls, and performance counters. State snapshots expose fault/status and register state for diagnostics.

## Dependencies And Integration Points

It includes DC hardware types and integrates with DML/DML2 bandwidth output, HUBP memory fetch, clock manager watermarks, VM/GART aperture setup, MALL/SubVP, DCC support checks, and HWSS p-state/self-refresh flows.

## Risks And Edge Cases

Watermark lowering must be safe or underflows can occur. VM aperture and default fault addresses are security/reliability-sensitive. DCC support depends on swizzle, plane pitch, pixel format, and bytes per element. DET/compbuf segment allocation must match active pipes and compression needs. Performance counters require correct refclk conversion.

## Test Signals

Tests should cover VM faults, DCC capability by format/swizzle, watermark sets, self-refresh/p-state transitions, DET/compbuf resizing, MALL use, arbiter programming, and perfmon/QoS readings. Signals include underflow, VM fault status, watermark readback, DET config errors, and measured memory latency/bandwidth.
