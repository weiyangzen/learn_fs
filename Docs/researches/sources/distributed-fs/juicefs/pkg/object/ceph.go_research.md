# sources/distributed-fs/juicefs/pkg/object/ceph.go


Purpose: implements a Ceph RADOS object backend behind the `ceph` build tag and registers it as `ceph`.

Important APIs and flow: `ceph` owns a `rados.Conn` and a bounded pool of `IOContext` objects. `Create` lists pools and creates the target pool if absent. `Get` validates existence through `Head`, then returns `cephReader`, which reads RADOS object ranges incrementally and releases its context on `Close`. `Put` fast-paths non-empty `*bytes.Reader` data below about 85 MiB through `WriteFull`, otherwise streams 1 MiB chunks with increasing offsets. `Delete`, `Head`, and `ListAll` translate RADOS operations into JuiceFS object semantics.

State and persistence: persistent state is the Ceph pool and object namespace. The adapter pools IO contexts and configures `SetPoolFullTry`. It does not persist directory metadata beyond object keys ending in `/`.

Dependencies and integration: uses `github.com/ceph/go-ceph/rados`, shared `obj`, `DefaultObjectStorage`, and `Shutdownable`. `newCeph` reads Ceph config, optional logging/admin-socket environment variables, and opens a connection using cluster and user arguments.

Risks: empty object writes return unsupported or an error, which diverges from most object stores. Most methods ignore caller context. Ordered `ListAll` scans all keys and then stats them concurrently, with comments noting poor performance and possible goroutine leaks on errors. The unordered mode omits sizes and mtimes.

Test signals: `object_storage_test.go` has a commented Ceph test only. Coverage depends on manual build with the `ceph` tag and a live cluster.
