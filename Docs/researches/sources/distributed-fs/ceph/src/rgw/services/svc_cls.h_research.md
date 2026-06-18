<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_cls.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_cls.h

Purpose: Declares `RGWSI_Cls`, the RGW service facade for selected RADOS object-class features.

Important APIs, types, and functions: The service owns nested subservices `MFA`, `TimeLog`, and `Lock`, all derived from `ClsSubService` so they can reach the parent `RGWSI_Cls`. The header declares all MFA OTP APIs, time-log add/list/info/trim APIs, and lock/unlock APIs. `init()` binds `RGWSI_Zone` and `librados::Rados` and initializes subservices.

Control flow: Consumers call `RGWSI_Cls::init()`, then start the service, then use `mfa`, `timelog`, and `lock` members directly. Subservices delegate pool lookup to the parent zone service and execute cls operations in the implementation.

State and persistence: The header holds only pointers to zone and RADOS services plus subservice instances. Persistent state lives in RADOS object class objects.

Dependencies and integration points: Depends on cls OTP/log types, RGW service base, and RGW RADOS helpers. It is a common dependency for metadata log and security operations.

Risks and test signals: Because subservices are public members, lifetime/order bugs can occur if they are used before `init()` or service startup. Compile tests should verify cls type availability; integration tests should validate each subservice against real RADOS pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_cls.h -->
