# sources/distributed-fs/ceph/src/rgw/rgw_lib.h

Purpose: Declares the librgw embedding API and request abstractions that let non-HTTP clients drive RGW operations through in-process request and IO objects.

Important APIs and types: `RGWLib` owns `AppMain`, a Ceph context, and a frontend pointer. `RGWLibIO` implements `BasicClient` and `Accounter` around `RGWEnv` and optional `RGWUserInfo`. `RGWRESTMgr_Lib` and `RGWHandler_Lib` adapt REST handler behavior. `RGWLibRequest` combines `RGWRequest` and `RGWHandler_Lib` and requires descendants to implement `header_init()`, `op_init()`, and `only_bucket()`. `RGWLibContinuedReq` adds `exec_start()`, `exec_continue()`, and `exec_finish()` for multi-step operations.

Control flow: A librgw request is constructed with a user, initialized with an environment and driver, populated with req ids, tenant, and user state, then passed to process code in `rgw_lib.cc`. Descendant request classes provide operation-specific header and op initialization.

State and persistence: `RGWLibIO` owns the environment and loaded user info for a request. `RGWLibRequest` temporarily owns a SAL user during initialization and then transfers it into `req_state`. Continued requests embed their own IO context and request state so they can survive across start/continue/finish calls.

Dependencies and integration points: Depends on RGW client IO, REST, request, LDAP, main initialization, SAL driver/user types, and frontend classes. It is the boundary between external librgw callers and normal RGW operation execution.

Risks: Several IO methods are minimal or return zero accounting, so callers expecting byte-accurate accounting need to verify behavior. `RGWLibRequest` uses global `g_rgwlib` to obtain driver ids during construction. Descendants must set up `op` correctly or processing falls back to runtime dynamic casting.

Test signals: Tests should validate request state initialization, tenant/user transfer, bucket-only permission reads, continued request state retention, IO environment setup, and behavior when descendant initialization omits required operation state.
