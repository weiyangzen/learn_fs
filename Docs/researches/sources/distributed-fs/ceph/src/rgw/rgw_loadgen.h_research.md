# sources/distributed-fs/ceph/src/rgw/rgw_loadgen.h

Purpose: Declares request environment and IO classes used by the RGW load generator to synthesize signed in-process S3 requests.

Important APIs and types: `RGWLoadGenRequestEnv` stores port, content length, content type, method, URI, query string, date, and headers, with `set_date()` and `sign()` helpers. `RGWLoadGenIO` derives from `rgw::io::RestfulClient` and implements environment initialization, synthetic body receive/send, response status/header hooks, flush, and request completion.

Control flow: The load generator constructs an environment, signs it, then passes an `RGWLoadGenIO` into `RGWRestfulIO`/RGW request processing. Read calls consume synthetic request bytes; write/status/header calls discard output.

State and persistence: The IO object points at an external request environment and owns an `RGWEnv`. `left_to_read` is initialized from content length on env init. No persistent state is created here.

Dependencies and integration points: Depends on `rgw_client_io.h`, RGW access keys, Ceph time formatting, and the loadgen process. It provides enough of the client IO contract for RGW ops to execute.

Risks: The request environment pointer must outlive the IO object. Output is ignored and byte accounting is minimal, so failures may only surface through return codes in the process layer. It is not appropriate as a correctness oracle for HTTP serialization.

Test signals: Tests should verify environment lifetime assumptions, content length handling, receive-body exhaustion, header propagation, signing integration, and behavior for GET/PUT/DELETE style generated requests.
