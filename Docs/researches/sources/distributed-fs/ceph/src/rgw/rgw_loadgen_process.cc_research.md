# sources/distributed-fs/ceph/src/rgw/rgw_loadgen_process.cc

Purpose: Implements the RGW load generation process that creates buckets, uploads objects, reads objects, deletes objects, deletes buckets, and then shuts the RGW process down.

Important APIs and functions: `RGWLoadGenProcess::run()` orchestrates the load sequence. `checkpoint()` drains queued work. `gen_request()` allocates and queues `RGWLoadGenRequest` objects. `handle_request()` converts each queued request into a signed loadgen IO path and calls `process_request()`.

Control flow: `run()` starts the thread pool, reads `num_objs` and `num_buckets` from frontend config, creates random bucket names, queues bucket PUTs and drains, creates random object names, queues object PUTs and drains, then queues GETs, object DELETEs, and bucket DELETEs with drain points between phases. It stops the thread pool, deletes the object name array, and signals RGW shutdown. `handle_request()` builds `RGWLoadGenRequestEnv`, signs it, wraps it in `RGWRestfulIO`, processes the request, and deletes the request.

State and persistence: The generated workload mutates normal RGW bucket/object state through the standard request path. Local state includes bucket and object name vectors/arrays, an access key, a request queue, and an optional failure flag shared by setup phases.

Dependencies and integration points: Depends on RGW process/work queue infrastructure, `RGWLoadGenIO`, request processing, frontend config, random name helpers, and RGW signal shutdown. It is a synthetic frontend-like process rather than an external benchmark client.

Risks: On request failure, `handle_request()` does `req->fail_flag++` instead of incrementing the atomic value it points to, so the phase failure flag may not be set as intended. Error messages after object PUT failures still say bucket creation failed. The object array is allocated after bucket creation and deleted unconditionally at `done`, which is safe in the current flow because allocation precedes the first `goto done` after that point.

Test signals: Tests should cover generated phase ordering, config defaults, request signing and processing, failure flag mutation, cleanup after failures, thread pool drain behavior, and final shutdown signaling.
