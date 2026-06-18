
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CodecPool.java

## Purpose
`CodecPool` is a global in-process pool for reusable `Compressor` and `Decompressor` instances, especially native codec wrappers whose construction and teardown are expensive.

## Important APIs and Types
Public APIs are `getCompressor(codec, conf)`, `getCompressor(codec)`, `getDecompressor(codec)`, `returnCompressor`, `returnDecompressor`, `getLeasedCompressorsCount`, and `getLeasedDecompressorsCount`. It maintains class-keyed `Map<Class<T>, Set<T>>` pools and Guava `LoadingCache<Class<T>, AtomicInteger>` lease counters.

## Control Flow
Borrowing checks the pool for an instance of the codec's implementation class. If absent, the codec creates a new object; if present, compressors are reinitialized using either the provided configuration or the codec's `Configurable` configuration. Returning resets reusable instances and puts them back in the class set. Types annotated with `@DoNotPool` are ended and not added to the pool.

## State and Persistence
The pool is static process-local state. Pool maps are synchronized at the map and set levels; lease counts are updated only for non-`DoNotPool` instances and only decremented when `payback` actually adds the object to the set, preventing double-return from underflowing counts.

## Dependencies and Integration
`CompressionCodec.Util` calls the pool and attaches borrowed codecs to streams so close returns them. Concrete codecs provide the implementation class keys through `getCompressorType` and `getDecompressorType`. `ReflectionUtils.getClass` is used to key returned instances.

## Risks
The pool is global and unbounded by size, so workloads using many codec classes or large native buffers can retain memory. Correctness depends on reset/reinit implementations clearing all per-stream state. Borrowing and returning the same object multiple times is guarded by set semantics for counts but can still make application misuse visible as closed or corrupted compressors.

## Test Signals
`TestCodecPool` covers lease counts, duplicate returns, multithreaded borrow/return, compressor reconfiguration on reuse, and `DoNotPool` behavior for built-in gzip classes.
