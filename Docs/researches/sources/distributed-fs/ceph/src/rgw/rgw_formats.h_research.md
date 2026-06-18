# sources/distributed-fs/ceph/src/rgw/rgw_formats.h

## Purpose
Declares RGW formatter helpers used by REST and website-listing response code.

## Important APIs, Types, And Functions
`plain_stack_entry` records array/object state and item count. `RGWFormatter_Plain` derives from `Formatter` and exposes plain dump/flush/reset methods. `RGWSwiftWebsiteListingFormatter` emits website listing HTML. `RGWFormatterFlusher` abstracts delayed formatter flushing; `RGWStreamFlusher` writes to an `ostream`; `RGWNullFlusher` discards flushes.

## Control Flow
Callers write through `Formatter` methods, then `RGWFormatterFlusher::start()` and `flush()` coordinate response start/flush. Website callers generate header, object/subdir rows, then footer.

## State And Persistence Behavior
Only transient formatting state. `RGWFormatterFlusher` records whether output was started/flushed, which response code can inspect.

## Dependencies And Integration Points
Depends on Ceph `Formatter`, standard strings/streams/lists, and `rgw_bucket_dir_entry` from included RGW headers in implementation contexts.

## Risks
`RGWNullFlusher` has a null formatter pointer, so callers must not dereference it. Plain formatter owns a raw char buffer. The header notes the plain formatter is misnamed and legacy.

## Test Signals
Compile tests should validate polymorphic formatter use; behavior tests should cover flush state transitions and null flusher use in paths that intentionally suppress body output.
