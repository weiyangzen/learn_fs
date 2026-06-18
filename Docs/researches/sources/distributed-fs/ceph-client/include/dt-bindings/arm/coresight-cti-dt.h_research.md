# sources/distributed-fs/ceph-client/include/dt-bindings/arm/coresight-cti-dt.h

Purpose: defines numeric device-tree constants for ARM CoreSight CTI trigger signal types.

Important APIs/types/functions: constants enumerate generic IO/interrupt/halt/restart triggers, PE debug and PMU triggers, ETM external in/out, sink full/acquire/flush signals, STM timeout/event signals, ELA trace start/stop/debug request, and `CTI_TRIG_MAX`.

Control flow: DTS files reference these IDs in CTI trigger descriptions; CoreSight CTI drivers parse the numeric cells and configure trigger routing.

State and persistence: IDs are device-tree ABI and must remain stable. No runtime state is held in the header.

Dependencies and integration: standalone DT binding header integrated by ARM CoreSight device trees and CTI driver bindings.

Risks and test signals: renumbering breaks existing DTBs. Test schema validation, CTI trigger routing on supported SoCs, and bounds checking against `CTI_TRIG_MAX`.
