# Folder Research: sources/distributed-fs/ceph/src/osd

This folder summary is inferred from accepted per-file research outputs.

- Direct researched files: 92
- Recursive researched files: 121
- Direct child folders represented: 2

## Direct Files

- `sources/distributed-fs/ceph/src/osd/CMakeLists.txt`
- `sources/distributed-fs/ceph/src/osd/ClassHandler.cc`
- `sources/distributed-fs/ceph/src/osd/ClassHandler.h`
- `sources/distributed-fs/ceph/src/osd/Coroutines.h`
- `sources/distributed-fs/ceph/src/osd/DynamicPerfStats.h`
- `sources/distributed-fs/ceph/src/osd/ECBackend.cc`
- `sources/distributed-fs/ceph/src/osd/ECBackend.h`
- `sources/distributed-fs/ceph/src/osd/ECBackendL.cc`
- `sources/distributed-fs/ceph/src/osd/ECBackendL.h`
- `sources/distributed-fs/ceph/src/osd/ECCommon.cc`
- `sources/distributed-fs/ceph/src/osd/ECCommon.h`
- `sources/distributed-fs/ceph/src/osd/ECCommonL.cc`
- `sources/distributed-fs/ceph/src/osd/ECCommonL.h`
- `sources/distributed-fs/ceph/src/osd/ECExtentCache.cc`
- `sources/distributed-fs/ceph/src/osd/ECExtentCache.h`
- `sources/distributed-fs/ceph/src/osd/ECExtentCacheL.cc`
- `sources/distributed-fs/ceph/src/osd/ECExtentCacheL.h`
- `sources/distributed-fs/ceph/src/osd/ECInject.cc`
- `sources/distributed-fs/ceph/src/osd/ECInject.h`
- `sources/distributed-fs/ceph/src/osd/ECListener.h`
- `sources/distributed-fs/ceph/src/osd/ECMsgTypes.cc`
- `sources/distributed-fs/ceph/src/osd/ECMsgTypes.h`
- `sources/distributed-fs/ceph/src/osd/ECOmapJournal.cc`
- `sources/distributed-fs/ceph/src/osd/ECOmapJournal.h`
- `sources/distributed-fs/ceph/src/osd/ECSwitch.h`
- `sources/distributed-fs/ceph/src/osd/ECTransaction.cc`
- `sources/distributed-fs/ceph/src/osd/ECTransaction.h`
- `sources/distributed-fs/ceph/src/osd/ECTransactionL.cc`
- `sources/distributed-fs/ceph/src/osd/ECTransactionL.h`
- `sources/distributed-fs/ceph/src/osd/ECTypes.h`
- `sources/distributed-fs/ceph/src/osd/ECUtil.cc`
- `sources/distributed-fs/ceph/src/osd/ECUtil.h`
- `sources/distributed-fs/ceph/src/osd/ECUtilL.cc`
- `sources/distributed-fs/ceph/src/osd/ECUtilL.h`
- `sources/distributed-fs/ceph/src/osd/HitSet.cc`
- `sources/distributed-fs/ceph/src/osd/HitSet.h`
- `sources/distributed-fs/ceph/src/osd/MissingLoc.cc`
- `sources/distributed-fs/ceph/src/osd/MissingLoc.h`
- `sources/distributed-fs/ceph/src/osd/OSD.cc`
- `sources/distributed-fs/ceph/src/osd/OSD.h`
- `sources/distributed-fs/ceph/src/osd/OSDCap.cc`
- `sources/distributed-fs/ceph/src/osd/OSDCap.h`
- `sources/distributed-fs/ceph/src/osd/OSDMap.cc`
- `sources/distributed-fs/ceph/src/osd/OSDMap.h`
- `sources/distributed-fs/ceph/src/osd/OSDMapMapping.cc`
- `sources/distributed-fs/ceph/src/osd/OSDMapMapping.h`
- `sources/distributed-fs/ceph/src/osd/ObjectVersioner.h`
- `sources/distributed-fs/ceph/src/osd/OpRequest.cc`
- `sources/distributed-fs/ceph/src/osd/OpRequest.h`
- `sources/distributed-fs/ceph/src/osd/PG.cc`
- `sources/distributed-fs/ceph/src/osd/PG.h`
- `sources/distributed-fs/ceph/src/osd/PGBackend.cc`
- `sources/distributed-fs/ceph/src/osd/PGBackend.h`
- `sources/distributed-fs/ceph/src/osd/PGLog.cc`
- `sources/distributed-fs/ceph/src/osd/PGLog.h`
- `sources/distributed-fs/ceph/src/osd/PGPeeringEvent.cc`
- `sources/distributed-fs/ceph/src/osd/PGPeeringEvent.h`
- `sources/distributed-fs/ceph/src/osd/PGStateUtils.cc`
- `sources/distributed-fs/ceph/src/osd/PGStateUtils.h`
- `sources/distributed-fs/ceph/src/osd/PGTransaction.h`
- `sources/distributed-fs/ceph/src/osd/PeeringState.cc`
- `sources/distributed-fs/ceph/src/osd/PeeringState.h`
- `sources/distributed-fs/ceph/src/osd/PrimaryLogPG.cc`
- `sources/distributed-fs/ceph/src/osd/PrimaryLogPG.h`
- `sources/distributed-fs/ceph/src/osd/ReplicatedBackend.cc`
- `sources/distributed-fs/ceph/src/osd/ReplicatedBackend.h`
- `sources/distributed-fs/ceph/src/osd/Session.cc`
- `sources/distributed-fs/ceph/src/osd/Session.h`
- `sources/distributed-fs/ceph/src/osd/SnapMapReaderI.h`
- `sources/distributed-fs/ceph/src/osd/SnapMapper.cc`
- `sources/distributed-fs/ceph/src/osd/SnapMapper.h`
- `sources/distributed-fs/ceph/src/osd/TierAgentState.h`
- `sources/distributed-fs/ceph/src/osd/Watch.cc`
- `sources/distributed-fs/ceph/src/osd/Watch.h`
- `sources/distributed-fs/ceph/src/osd/error_code.cc`
- `sources/distributed-fs/ceph/src/osd/error_code.h`
- `sources/distributed-fs/ceph/src/osd/objclass.cc`
- `sources/distributed-fs/ceph/src/osd/object_state.h`
- `sources/distributed-fs/ceph/src/osd/object_state_fmt.h`
- `sources/distributed-fs/ceph/src/osd/osd_internal_types.h`
- `sources/distributed-fs/ceph/src/osd/osd_op_util.cc`
- `sources/distributed-fs/ceph/src/osd/osd_op_util.h`
- `sources/distributed-fs/ceph/src/osd/osd_perf_counters.cc`
- `sources/distributed-fs/ceph/src/osd/osd_perf_counters.h`
- `sources/distributed-fs/ceph/src/osd/osd_tracer.cc`
- `sources/distributed-fs/ceph/src/osd/osd_tracer.h`
- `sources/distributed-fs/ceph/src/osd/osd_types.cc`
- `sources/distributed-fs/ceph/src/osd/osd_types.h`
- `sources/distributed-fs/ceph/src/osd/osd_types_fmt.h`
- `sources/distributed-fs/ceph/src/osd/pg_features.h`
- `sources/distributed-fs/ceph/src/osd/recovery_types.h`
- `sources/distributed-fs/ceph/src/osd/scrubber_common.h`

## Research Role

This directory participates in subset B filesystem research through the listed source files.
