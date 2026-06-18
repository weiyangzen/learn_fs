## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemWithLogging.java

### Purpose
`UnderFileSystemWithLogging` is a decorator around any `UnderFileSystem` implementation. It logs entry/exit for IO-capable methods, records per-method timers and failure counters, warns on slow calls, filters invalid listing names containing `?`, and tags metrics with UFS identity and optionally user.

### Important APIs, Types, And Functions
The wrapper stores the delegate, UFS configuration, original path, escaped metric path, and logging threshold. Nearly all `UnderFileSystem` methods are forwarded through the private `call(UfsCallable<T>)` helper. `UfsCallable` supplies `call`, `methodName`, and argument string formatting. `filterInvalidPaths` exists for arrays and iterators. `getQualifiedMetricName` and `getQualifiedFailureMetricName` build metric names with `TAG_UFS`, `TAG_UFS_TYPE`, and possibly `TAG_USER`.

### Control Flow
For wrapped calls, `call` logs debug entry, starts a Dropwizard timer, invokes the delegate, logs debug success, emits a warning if duration exceeds `UNDERFS_LOGGING_THRESHOLD`, and returns. On `IOException`, it increments the failure counter, logs debug error, optionally warns, and rethrows. Methods that do not throw IO, such as operation mode, physical stores, object-storage flag, seekable flag, and active-sync support, usually forward directly. `performListingAsync` is wrapped despite being callback-based; any unexpected `IOException` becomes an internal runtime exception.

### State And Persistence
No UFS data is persisted by the wrapper. It persists runtime observability into the metrics system and logs. The wrapper does not own the delegate lifecycle beyond forwarding `close` and `cleanup`.

### Dependencies And Integration Points
Created by `UnderFileSystem.Factory` around successful provider clients. It integrates with `MetricsSystem`, `Metric`, authenticated client user state, security utilities, and Alluxio logging.

### Risks
Observability code can change behavior: listing results with `?` are silently filtered with warnings. `getFileStatus(String, GetFileStatusOptions)` forwards to `mUnderFileSystem.getFileStatus(path)` instead of passing the options, so option flags such as real content hash can be ignored through the wrapper. A method name typo, `RenameRenableDirectory`, affects metric naming. Slow-call logging may expose path/option strings in logs.

### Test Signals
No direct wrapper test is in this subset. Indirect factory tests create wrapped clients only when factories are present. Listing filter behavior and option forwarding merit targeted tests.
