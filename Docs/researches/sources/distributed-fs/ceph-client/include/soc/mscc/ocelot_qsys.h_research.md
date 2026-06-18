# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_qsys.h

Purpose: defines register bitfields for the Ocelot QSYS queuing and scheduling block. It covers port dequeue modes, drop/stat counter modes, EEE thresholds, external CPU queues, queue-to-scheduler mapping, timed-frame control, RED profiles, resource counters, queue maximum SDU, frame preemption, shapers, scheduler elements, DLB sensing, TAS gate-list programming, and tag configuration.

Important APIs/types/functions: macro-only API. Important groups include `QSYS_PORT_MODE_*`, `QSYS_QMAP_*`, `QSYS_TFRM_*`, `QSYS_PREEMPTION_CFG_*`, `QSYS_CIR_CFG_*`, `QSYS_EIR_CFG_*`, `QSYS_SE_*`, `QSYS_TAG_CONFIG_*`, and `QSYS_TAS_*`.

Control flow: runtime code writes queue/shaper/scheduler fields, connects scheduler elements, updates preemption/TAS parameters, and polls status registers for pending configuration or resource state. The header encodes hardware operations but does not execute them.

State and persistence: persistent hardware state includes scheduler tree topology, shaper rates and buckets, queue limits, frame preemption configuration, gate-control lists, and statistics modes. State is reset or replaced by later switch configuration.

Dependencies and integration: included by Ocelot/Felix Ethernet and DSA code and by MAC Merge support. It integrates with tc/taprio, mqprio, frame preemption, QoS, pause/PFC, CPU-port handling, and switch statistics.

Risks: scheduler and TAS fields are timing-sensitive. Bad queue maps or shaper values can starve traffic, violate gate schedules, or break preemption. Test signals include traffic shaping, taprio gate schedules, preemption verification, max-SDU enforcement, queue stats, and CPU-port forwarding tests.
