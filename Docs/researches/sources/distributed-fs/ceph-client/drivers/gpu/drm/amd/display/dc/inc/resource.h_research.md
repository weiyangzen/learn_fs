# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/resource.h

## Purpose

`resource.h` declares the central DC resource-management API. It constructs/destroys resource pools, maps streams and planes onto hardware resources, manages pipe topology, clock sources, scaling, encoder resources, pipe synchronization, and shared topology helpers for MPC/ODM and DML.

## Important APIs, Types, And Functions

The header defines memory type constants, pipe-sync bit macros, `resource_caps`, `resource_straps`, `dc_mcache_allocations`, and `resource_create_funcs` for straps, audio, stream encoders, HPO DP encoders, and HW sequencer creation. It declares pool construction/destruction, stream-to-resource mapping, test pattern/scaling/infoframe builders, clock source refcount helpers, timing/vblank synchronization tests, PLL sharing/free lookup, surface attachment, cursor-disable eligibility, and a detailed `enum pipe_type` for OTG master, OPP head, DPP pipe, MPC combine, ODM, and related topology roles.

Topology APIs add/remove OTG masters, append/remove DPP pipes, update slice counts for streams/planes, query OTG master/OPP head/primary DPP, compute MPC/ODM slice index/count and rects, detect topology changes, log topology updates, find free pipes under several current-context constraints, validate surface attachment, map clock/PHY resources, decide pipe reprogramming, build bit-depth reduction, update audio usage, compute bpp, get temporary DP link resources, reset/check syncd pipes, choose link HWSS, acquire secondary pipes, update DP encoder resources for test harnesses, expose DSCL program data, initialize DML2 callbacks, calculate DET, detect HPO acquisition, and get temporary DIO encoders.

## Control Flow

Resource creation parses ASIC capabilities and builds a pool. During validation/commit, mapping functions assign streams, planes, clocks, encoders, pipes, and topology slices. Helper queries then let hardware sequencing walk OTG/OPP/DPP relationships and update only changed topology. Free-pipe search routines reuse current-context pipes when possible.

## State And Persistence Behavior

Resource state persists in `resource_pool`, `resource_context`, `dc_state`, pipe contexts, clock-source reference counts, link encoder assignments, and pipe sync flags. The macros encode synced-pipe validity in the high bit of `pipe_idx_syncd`.

## Dependencies And Integration Points

The file depends on core DC types/status, ASIC IDs, and SMU/PP interfaces. It integrates with almost every display path: link encoders, stream encoders, timing generators, OPP/MPC/DPP, DML2 validation, audio, clocks, DP test harnesses, and pipe topology logging.

## Risks And Test Signals

Risks include resource leaks, incorrect pipe reuse, topology role confusion, stale clock references, bad slice counts, and transient commit mismatches. Test signals include multi-monitor modesets, plane scaling/slicing, ODM/MPC combine, MST/DP encoder allocation, audio route changes, DML validation, topology logs, and resource leak/assert checks across hotplug and suspend/resume.
