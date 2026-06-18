# sources/distributed-fs/ceph/src/rgw/rgw_ssd_driver.h

## Purpose
`rgw_ssd_driver.h` declares the SSD cache driver that implements `rgw::cache::CacheDriver` on top of local files, xattrs, and POSIX AIO.

## Important APIs, Types, and Functions
`SSDDriver` overrides cache operations for initialization, put/get, async put/get, append, delete, rename, attribute CRUD, free-space reporting, partition reporting, and block/object restoration. Private nested handlers bridge Boost/system errors into `rgw::AioResult`. `libaio_aiocb_deleter` closes file descriptors and releases `aiocb` objects. `AsyncReadOp` owns the read result and aiocb; `AsyncWriteRequest` owns paths, copied data, fd, attrs, and backpointer to the driver.

## Control Flow
The public interface follows the `CacheDriver` contract. Synchronous methods call the private async templates with a yield or blocked token. RGW Aio methods return operation functions that schedule local AIO and complete into the upstream throttle.

## State and Persistence Behavior
The class stores `Partition partition_info`, `free_space`, `CephContext*`, a mutex, and `admin`. Nested operation objects own transient async state until callbacks dispatch completion. Persistent behavior is implemented in the `.cc` file through filesystem files and xattrs.

## Dependencies and Integration Points
The header includes `rgw_common.h`, `rgw_cache_driver.h`, POSIX aio, Ceph async completion, Boost ASIO executor support, and RGW Aio types. It is consumed by the D4N cache factory and code that expects a `CacheDriver`.

## Risks
The nested completion data contains non-owning references to `DoutPrefixProvider`, `SSDDriver`, and `rgw::Aio`; callers must keep them live until callbacks complete. The custom deleter assumes `aio_fildes > 0`, so fd zero would not be closed. The API accepts full `Attrs` maps, which can be expensive to copy into async lambdas.

## Test Signals
Compile/link coverage should verify the `CacheDriver` override signatures. Runtime tests should cover async completion lifetime, callback dispatch into `rgw::Aio`, attr propagation, and destructor cleanup of `aiocb` file descriptors.
