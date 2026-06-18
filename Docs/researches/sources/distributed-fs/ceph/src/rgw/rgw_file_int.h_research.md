# sources/distributed-fs/ceph/src/rgw/rgw_file_int.h

## Purpose
Internal header for librgw file support. It defines the handle model, filesystem object, cache machinery, request adapters, and inline RGWOp subclasses used by `rgw_file.cc`.

## Important APIs, Types, And Functions
`fh_key` encodes hashed bucket/object identity and supports ordering/equality. `RGWFileHandle` wraps public `rgw_file_handle`, state/stat fields, directory/file variants, parent/bucket pointers, flags, LRU hooks, and methods such as `stat()`, `full_object_name()`, `make_fhk()`, `readdir()`, `write()`, `write_finish()`, `close()`, `encode_attrs()`, `decode_attrs()`, and `invalidate()`. `RGWLibFS` owns root state, user/key authorization data, FH cache/LRU, invalidate callbacks, write timer, and operation methods. Request adapters include list buckets, list bucket, rmdir check, create/delete bucket, put/get/delete/stat object, stat bucket/leaf, continued write, copy object, get/set/remove attrs, and cluster stat.

## Control Flow
Public C API calls enter `RGWLibFS` and create request objects declared here. Each request initializes a synthetic `req_state` with method/op/URI, overrides parameter and response hooks, then executes through `g_rgwlib->get_fe()`. File handles are found or inserted through `lookup_fh()`, which latches cache partitions, refs through LRU, and handles deletion/retry races.

## State And Persistence Behavior
`RGWFileHandle::State` mirrors Unix stat data, while persistent metadata is serialized by `encode_attrs()` into RGW attrs. Directories keep last marker and last readdir timestamp; files keep an active `RGWWriteRequest`. `RGWLibFS::State` queues namespace invalidation events. `RGWWriteRequest` owns streaming write pipeline state including SAL writer, compression filter, MD5 etag, byte counters, and timer id.

## Dependencies And Integration Points
Includes RGW lib, LDAP/token auth, put object processors, AIO throttle, compression, perf counters, checksums, common LRU/timer, and SAL driver/user classes. The request classes inherit existing RGW ops and rely on `RGWHandler::driver` setup by the lib frontend.

## Risks
The header is large and behavior-heavy, so inline changes affect ABI-like internal contracts. Locking mixes cache latches, FH mutexes, and LRU refs. Flags are dense; `FLAG_SYMBOLIC_LINK = 0x0009` overlaps other bits and is marked suspicious. Many request `header_init()` methods use synthetic URI/request fields with comments noting rough edges. Continued writes reject out-of-order chunks and rely on close/timer completion.

## Test Signals
Tests should stress FH cache ref/reclaim, locked/unlocked lookup paths, deleted-handle retries, attr encode/decode compatibility, directory marker continuation, request header setup, xattr prefixing, continued write start/continue/finish, and auth fallback paths.
