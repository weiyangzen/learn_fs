<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/parselog.h -->
# sources/distributed-fs/coda/coda-src/resolution/parselog.h

Purpose: declares the remote-log grouping structures and parser helpers used by log-based directory resolution.

Important APIs/types: `remoteloglist` is an `olink` with `vnode`, `unique`, and an `olist slelist` of `rsle` pointers for one vnode at one host. `ParseRemoteLogs` parses serialized log bytes into `olist **` host grouping and `rsle **` entry storage. `DeallocateRemoteLogs`, `FindLogList`, and `FindRemoteLog` support cleanup and lookup.

State/persistence: no persistent state; represents temporary views over shipped log buffers. `remoteloglist` destructor intentionally does not assert that its list is empty.

Dependencies/integration: includes `olist` and `vcrcommon`; relies on `he` from `resutil.h` and `rsle` declarations available through included resolution headers in users.

Risks/test signals: ownership of the `RemoteLogEntries` array is not expressed in the header. Callers need a clear cleanup convention: delete the array after deallocating wrapper lists. Test cleanup under parse failure and lookup of absent remote vnode logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/parselog.h -->
