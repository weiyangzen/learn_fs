# subset-b-007396 Research

Grouped research report for Hadoop common HTTP and IO test sources. Each source section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServerConfigs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServerConfigs.java

## Purpose
JUnit 5 test suite for HTTPS `HttpServer2` SSL configuration, especially keystore key password, keystore store password, truststore password, and enabled TLS protocol propagation. It complements `TestSSLHttpServer` by using generated test keystores and checking both successful server startup and precise failure causes.

## Important APIs, Types, and Functions
The class uses `HttpServer2.Builder`, `KeyStoreTestUtil.setupSSLConfig`, `SSLFactory.SSL_ENABLED_PROTOCOLS_KEY`, Jetty `ServerConnector`, `SslConnectionFactory`, and `SslContextFactory`. `start()` prepares a clean temp keystore directory, turns on SSL debug logging, stores cipher suite state, and sets a low HTTP max thread count. `shutdown()` deletes temp files, cleans SSL config files, and restores cipher/debug settings. `setupKeyStores()` creates keystore/truststore material with configurable passwords and applies included protocols. `setupServer()` builds a HTTPS-only `HttpServer2` using explicit key/trust store values from `sslConf`. `testServerStart()` starts the server and waits until `server.isAlive()`.

## Control Flow and State
Each test creates fresh `Configuration` objects and filesystem-backed keystore artifacts under `GenericTestUtils.getTempPath`. Positive tests start and stop an HTTPS server. Negative tests intentionally pass null, empty, or incorrect password combinations and assert `IOException` messages or causes. Protocol tests build the server without starting it, inspect the first listener's SSL factory, and assert that include protocols contain only the configured protocol and that the protocol is not also excluded.

## Dependencies and Integration Points
Integrates Hadoop security SSL utilities, Jetty SSL internals, `HttpServer2` builder password handling, and static constants from `TestSSLHttpServer` for cipher/protocol settings. It depends on classpath SSL config output from `KeyStoreTestUtil`.

## Risks and Test Signals
Risk areas are password null-vs-empty semantics, wrong-password diagnostics, temporary global SSL/cipher debug state, and Jetty protocol include/exclude behavior. The suite signals regressions through server startup success, expected `IOException` text, nested cause checks such as `Cannot recover key`, and direct SSL context assertions for default and non-default protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServerConfigs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestServletFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestServletFilter.java

## Purpose
Tests servlet filter registration and initialization failure behavior in `HttpServer2`. It verifies global filter initialization via configuration, context-specific registration through `HttpServer2.defineFilter`, and wrapping of filter init exceptions into server startup failures.

## Important APIs, Types, and Functions
`SimpleFilter` implements `javax.servlet.Filter`, records the request URI in static volatile `uri`, and forwards to the filter chain. `SimpleFilter.Initializer` extends `FilterInitializer` and adds the filter to a `FilterContainer`. `ErrorFilter` extends `SimpleFilter` but throws `ServletException` from `init`. `access()` opens a URL and drains its input stream while tolerating normal HTTP IO exceptions. Tests use `HttpServerFunctionalTest.createTestServer`, `HttpServer2.FILTER_INITIALIZER_PROPERTY`, `NetUtils.getHostPortString`, and `GenericTestUtils.assertExceptionContains`.

## Control Flow and State
The unannotated `testServletFilter()` starts a server with `SimpleFilter`, generates a random access sequence over `/fsck`, `/stacks`, `/a.jsp`, `/logs/a.log`, and `/static/hadoop-logo.jpg`, and checks that `/fsck` bypasses filtering while the other paths update `uri`. Annotated tests start servers with `ErrorFilter` through the initializer and context API and assert startup failures. The only mutable state is static `uri`, reset after each filtered request.

## Dependencies and Integration Points
Depends on servlet API, Hadoop HTTP filter initializer/container contracts, URLConnection, and the test HTTP server harness. The path filtering behavior reflects `HttpServer2`'s default exclusion of certain internal endpoints such as `/fsck`.

## Risks and Test Signals
The static `uri` can be sensitive to concurrent test execution, and `testServletFilter()` lacks `@Test` in this source, so runner behavior may omit it. Strong signals are correct exception wrapping (`Problem starting http server`, `Unable to initialize WebAppContext`) and filter URI capture for non-excluded paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestServletFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/lib/TestStaticUserWebFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/lib/TestStaticUserWebFilter.java

## Purpose
Unit tests for `StaticUserWebFilter`, which wraps HTTP requests so web UIs can expose a configured static user principal when no authentication is active.

## Important APIs, Types, and Functions
Uses Mockito `FilterConfig`, `FilterChain`, `HttpServletRequest`, `ServletResponse`, and `ArgumentCaptor<HttpServletRequestWrapper>`. `mockConfig()` returns a config whose `HADOOP_HTTP_STATIC_USER` init parameter is the requested username. Tests call `StaticUserFilter.init`, `doFilter`, and `destroy`, and call `StaticUserWebFilter.getUsernameFromConf`.

## Control Flow and State
`testFilter()` initializes the filter with `myuser`, invokes it with mocked request/response, captures the wrapped request sent to the chain, and asserts both `getUserPrincipal().getName()` and `getRemoteUser()` return `myuser`. Configuration tests check legacy `dfs.web.ugi` parsing and modern `hadoop.http.staticuser.user` behavior.

## Dependencies and Integration Points
Integrates Hadoop `CommonConfigurationKeys`, servlet filter chain contracts, and Mockito. It validates backward compatibility with the historical `dfs.web.ugi` format used by older HDFS web UI code.

## Risks and Test Signals
Risk centers on preserving legacy config parsing and ensuring wrapper identity is passed down the chain. The test signals are captured wrapper values and direct username extraction from `Configuration`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/lib/TestStaticUserWebFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/resource/JerseyResource.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/resource/JerseyResource.java

## Purpose
Small Jersey resource used by HTTP server tests. It echoes the matched request path and `op` query parameter as JSON so tests can validate Jersey routing and response encoding inside Hadoop's embedded Jetty stack.

## Important APIs, Types, and Functions
Annotated with `@Path("")`; `get()` is a `@GET` handler for `@Path("{path:.*}")` and produces `application/json` with `JettyUtils.UTF_8`. It uses `@PathParam(PATH)` and `@QueryParam(OP)` with default values, builds a `TreeMap`, serializes it via Jetty `JSON.toString`, and returns `Response.ok(js).type(MediaType.APPLICATION_JSON).build()`.

## Control Flow and State
The resource is stateless aside from logging. Each request logs path/op, inserts them into a deterministic sorted map, serializes JSON, and returns a 200 response.

## Dependencies and Integration Points
Integrates JAX-RS annotations, Jetty JSON utility, Hadoop's `JettyUtils` charset constant, and test HTTP server Jersey configuration.

## Risks and Test Signals
Risks are catch-all path matching, default-value semantics, JSON ordering, and response content type/charset. Downstream tests can assert exact JSON keys `path` and `op` and content type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/resource/JerseyResource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/AvroTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/AvroTestUtil.java

## Purpose
Shared helper for tests that validate Avro reflection schemas and binary round trips for Hadoop writable-like classes.

## Important APIs, Types, and Functions
`testReflect(Object value, String schema)` delegates to `testReflect(Object value, Type type, String schema)`. It uses `ReflectData.get().getSchema(type)`, parses the expected schema, writes with `ReflectDatumWriter` and a direct binary encoder, then reads with `ReflectDatumReader` and a binary decoder.

## Control Flow and State
There is no persistent state. The helper first asserts schema equality, then serializes the supplied value to `ByteArrayOutputStream`, deserializes it with the same schema, and asserts value equality.

## Dependencies and Integration Points
Depends on Avro reflection APIs and JUnit assertions. Used by tests such as `TestEnumSetWritable` and `TestText` to ensure Hadoop types remain Avro-reflect compatible.

## Risks and Test Signals
Risk areas include Avro schema drift, package trust requirements, and equality semantics of reflected objects. The signal is strict schema equality plus binary round-trip equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/AvroTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/RandomDatum.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/RandomDatum.java

## Purpose
Test `WritableComparable` data generator used by SequenceFile, ArrayFile, SetFile, and related format tests. It creates variable-length random byte payloads with deterministic seeding support.

## Important APIs, Types, and Functions
Implements `WritableComparable<RandomDatum>`. `write()` stores an int length followed by raw bytes; `readFields()` resizes the backing array when needed and reads `length` bytes; `compareTo()` delegates to `WritableComparator.compareBytes`; `toString()` emits hex. Nested `Generator` produces key/value pairs from a `Random`, and nested `Comparator` extends `WritableComparator` to compare serialized records without object materialization.

## Control Flow and State
Instances carry `length` and `data`. Random construction uses length `10 + 10^(random float * 3)`, then fills bytes. Deserialization reuses or grows `data`, so bytes past `length` can remain but comparison and stringification use only active length. `Generator.next()` replaces both key and value each call.

## Dependencies and Integration Points
Integrates with Hadoop `Writable`, raw comparators, sorted maps, and file-format tests that need reproducible random records. The custom comparator is a performance-sensitive path for `SequenceFile.Sorter`.

## Risks and Test Signals
The main risk is stale trailing bytes influencing `hashCode()` because it hashes the full backing array while equality compares only `length` bytes; test use generally avoids variable shrink reuse in hash containers. It also casts in `equals` without type checks. Format tests signal serializer and comparator correctness by sorting and reading large generated datasets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/RandomDatum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayFile.java

## Purpose
Tests `ArrayFile`, a map-like file of indexed values backed by Hadoop `MapFile`/`SequenceFile` mechanics.

## Important APIs, Types, and Functions
Uses `ArrayFile.Writer`, `ArrayFile.Reader`, `MapFile.delete`, `RandomDatum`, `LongWritable`, `CompressionType.RECORD`, `Progressable`, and local/default `FileSystem`. Helpers `generate`, `writeTest`, and `readTest` create random values, write them with index interval 100, and read them forward/backward by numeric index.

## Control Flow and State
`testArrayFile()` writes 10,000 random records and validates indexed reads in both directions. `testEmptyFile()` writes no records and asserts index 0 returns null. `testArrayFileIteration()` writes ten long values, iterates with `next`, seeks to key 6, checks subsequent key/value 7, and asserts out-of-range seek false. The `main` method is a manual CLI harness for large create/check runs.

## Dependencies and Integration Points
Persists data under `GenericTestUtils` temp paths on local/default filesystems. It exercises `ArrayFile`'s use of `MapFile` index intervals and `SequenceFile` compression options.

## Risks and Test Signals
Risks include leftover temp data, filesystem selection differences, and broad `catch` blocks that hide root causes behind generic failures. Signals are exact random datum equality, null for empty/out-of-range access, stable iteration order, and seek behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayPrimitiveWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayPrimitiveWritable.java

## Purpose
Validates compact serialization of Java primitive arrays via `ArrayPrimitiveWritable` and `ObjectWritable`, including compatibility with older non-compact array encoding.

## Important APIs, Types, and Functions
Uses static primitive arrays for boolean, char, byte, short, int, long, float, and double. `DataOutputBuffer`/`DataInputBuffer` are reset per test. `testMany()` writes each array both through `ObjectWritable.writeObject(..., allowCompactArrays=true)` and direct `ArrayPrimitiveWritable.write`, then reads with `ObjectWritable.readObject` and `ArrayPrimitiveWritable.readFields`. `testObjectLabeling()` inspects serialized class labels using deprecated `UTF8.readString`. `testOldFormat()` writes through old `ObjectWritable.writeObject` and reads individual boxed elements.

## Control Flow and State
The test maintains a result array twice the primitive type count. It checks component types before deep value equality, then explicitly validates label names for internal compact arrays and direct `ArrayPrimitiveWritable` objects.

## Dependencies and Integration Points
Exercised APIs include `ObjectWritable`, `ArrayPrimitiveWritable.Internal`, deprecated `UTF8`, and primitive-array reflection. It protects wire compatibility for RPC/object serialization paths.

## Risks and Test Signals
Risk areas are class label compatibility, compact-array opt-in semantics, primitive component type preservation, and deprecated format support. Signals are exact labels, length fields, component types, and array value equality across all primitive categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayPrimitiveWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayWritable.java

## Purpose
Unit tests for `ArrayWritable` constructor and conversion behavior.

## Important APIs, Types, and Functions
Defines `TextArrayWritable extends ArrayWritable` with `Text.class` value class. Tests use `set`, `write`, `readFields`, `get`, `toArray`, `toStrings`, and constructors for `Class<? extends Writable>` and `String[]`.

## Control Flow and State
The main read/write test serializes a `Text[]` into buffers and reads into a new `TextArrayWritable`, asserting element equality. Conversion tests verify `toArray()` returns a concrete `Text[]`, null value class construction throws `IllegalArgumentException`, and `String[]` construction uses `Text.class` with matching string output.

## Dependencies and Integration Points
Depends on Hadoop writable buffers and JUnit assertion APIs. It validates APIs used when configs or RPC payloads carry homogeneous writable arrays.

## Risks and Test Signals
Risks are undefined value class errors, array type erasure, and string conversion compatibility. Signals are element-by-element equality, thrown exception type, and value class identity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBloomMapFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBloomMapFile.java

## Purpose
Tests `BloomMapFile`, a `MapFile` variant with bloom-filter membership checks. It covers membership accuracy, varying key sizes, delete/get operations, constructor variants, and reader behavior when bloom filter loading fails.

## Important APIs, Types, and Functions
Uses `BloomMapFile.Writer`, `BloomMapFile.Reader`, `MapFile.Writer` options, `MapFile.Reader.comparator`, `SequenceFile.CompressionType`, local filesystem paths, `IOUtils.cleanupWithLogger`, and a mocked `CompressionCodec`. `setUp()` deletes and recreates a temp root. `checkMembershipVaryingSizedKeys()` writes `Text` keys and checks reverse-order membership.

## Control Flow and State
`testMembershipTest()` writes even integer keys up to 1998 with bloom size 2048, then scans 0-1999 to assert zero false negatives and fewer than two false positives. Other tests write short key sets, delete files, mock path filesystem lookup failure to get null bloom filter, verify `get` returns values for present keys and null for absent keys, and instantiate many deprecated/current writer constructors.

## Dependencies and Integration Points
Integrates MapFile storage, bloom filter side data, Hadoop local filesystem, Mockito spies, and compression option plumbing. It shares temp path naming with `TestMapFile`.

## Risks and Test Signals
Bloom filters are probabilistic, so the false-positive threshold is a statistical test. Varying-sized keys guard serialization boundaries. Constructor tests mostly assert non-null and may miss deeper compressed-stream behavior because the codec returns mocks/nulls. Signals include no false negatives, bounded false positives, null fallback on bloom filter IO failure, and expected get/delete behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBloomMapFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBooleanWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBooleanWritable.java

## Purpose
Tests `BooleanWritable` serialized comparator ordering and common object methods.

## Important APIs, Types, and Functions
`writeWritable()` serializes a `Writable` to `DataOutputBuffer`; `compare()` invokes `WritableComparator.compare` on buffer bytes. Tests use `WritableComparator.get(BooleanWritable.class)`, `equals`, `hashCode`, `compareTo`, and `toString`.

## Control Flow and State
The comparator test serializes true/false values and asserts equality against same buffers, true greater than false, and false less than true. Common-method tests create fresh instances for equality, hash, comparison, and string assertions.

## Dependencies and Integration Points
Validates Hadoop's raw comparator registry and object-level writable semantics used in sorted file formats and collections.

## Risks and Test Signals
Signals are exact comparator return signs, hash equality/inequality for true/false, and string `"true"`. Risks are minimal, though assertions use sign-specific values for raw comparator output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBooleanWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBoundedByteArrayOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBoundedByteArrayOutputStream.java

## Purpose
Unit tests for `BoundedByteArrayOutputStream` capacity enforcement, reset behavior, and protected buffer replacement.

## Important APIs, Types, and Functions
Uses `BoundedByteArrayOutputStream.write`, `reset`, `reset(int)`, `getLimit`, `getBuffer`, and subclass-exposed `resetBuffer(byte[], int, int)`. Test input is a static 1024-byte random array.

## Control Flow and State
`testBoundedStream()` fills the stream to capacity, asserts contents, verifies one extra byte throws, resets, writes again, lowers the limit, and verifies an oversized write fails. `testResetBuffer()` repeats the capacity checks after swapping in a new backing buffer through a test subclass.

## Dependencies and Integration Points
The tests target the IO utility directly and depend only on JUnit and Java arrays/random data. This stream is used where Hadoop needs bounded in-memory serialization.

## Risks and Test Signals
Risks include off-by-one capacity enforcement, stale limit after reset, and incorrect backing-buffer replacement. Signals are array equality, limit values, and caught exceptions on overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBoundedByteArrayOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBytesWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBytesWritable.java

## Purpose
Tests `BytesWritable` dynamic sizing, hash/compare/toString semantics, zero-copy construction, and `ByteWritable` common methods.

## Important APIs, Types, and Functions
Exercises `BytesWritable.setSize`, `setCapacity`, `getCapacity`, `getLength`, `getBytes`, `copyBytes`, `hashCode`, `compareTo`, `toString`, zero-copy constructor `(byte[], length)`, and `set(byte[], offset, length)`. Also tests `ByteWritable.set`, `get`, `compareTo`, `equals`, and `toString`.

## Control Flow and State
`testSizeChange()` expands and shrinks a buffer while preserving data and length invariants. `testHash()` verifies hash ignores capacity beyond logical length. `testCompare()` checks reflexive/symmetric lexicographic ordering across several byte arrays. `testZeroCopy()` asserts constructor retains the original backing array and remains equal to copied construction after buffer expansion/reset.

## Dependencies and Integration Points
These writables are core types for sequence/map files, RPC payloads, and writable collections. Tests depend only on JUnit.

## Risks and Test Signals
Risks are logical length vs capacity confusion, zero-copy aliasing surprises, and signed-byte rendering. Signals are exact hash values, formatted hex strings, comparator ordering, and backing-array identity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBytesWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestDataByteBuffers.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestDataByteBuffers.java

## Purpose
Compatibility tests for `DataOutputBuffer`, `DataInputBuffer`, and `DataInputByteBuffer` across Java `DataInput`/`DataOutput` primitive operations.

## Important APIs, Types, and Functions
`writeJunk()` writes deterministic random bytes, shorts, ints, longs, doubles, floats, and byte arrays to a `DataOutput`. `readJunk()` replays the same random sequence and validates reads from a `DataInput`. Tests use `ByteBuffer.wrap` and `DataInputByteBuffer.reset`.

## Control Flow and State
A static `Random` is reset to seed 31 before each write/read phase. `testBaseBuffers()` writes and reads through Hadoop byte-array buffers, resets, and repeats. `testDataInputByteBufferCompatibility()` writes with `DataOutputBuffer`, wraps the result in `ByteBuffer`, and reads through `DataInputByteBuffer`.

## Dependencies and Integration Points
Integrates buffer classes used by writable serialization and nio-backed readers. It validates bit-level compatibility for primitive types.

## Risks and Test Signals
Risk areas are byte order, floating-point bit preservation, buffer offset/limit handling, and reset semantics. Signals are exact primitive equality and byte-array equality over 1000 randomized operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestDataByteBuffers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestDefaultStringifier.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestDefaultStringifier.java

## Purpose
Tests `DefaultStringifier`, which serializes configured object types to strings for storage in Hadoop `Configuration` entries and reverses them later.

## Important APIs, Types, and Functions
Uses `DefaultStringifier<T>.toString`, `fromString`, static `store`, `load`, `storeArray`, and `loadArray`. Configuration key `io.serializations` is switched between `WritableSerialization` and `JavaSerialization`. `LambdaTestUtils.intercept` checks empty-array storage failure.

## Control Flow and State
`testWithWritable()` randomly creates `Text` values and round-trips them through stringification. `testWithJavaSerialization()` round-trips an `Integer`. `testStoreLoad()` stores and loads a `Text` under a config key. `testStoreLoadArray()` rejects an empty integer array, stores a nonempty array, loads it, and compares entries.

## Dependencies and Integration Points
Depends on Hadoop serialization factory configuration, `Configuration` as persistence medium, and Java/Writable serialization implementations.

## Risks and Test Signals
Risks include stale global static `conf` mutation across tests, serialization selection mistakes, empty-array indexing, and base64/string encoding compatibility. Signals are object equality and expected `IndexOutOfBoundsException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestDefaultStringifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestEnumSetWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestEnumSetWritable.java

## Purpose
Tests `EnumSetWritable` serialization for non-empty, empty, and null enum sets, plus Avro reflection and equality/iteration semantics.

## Important APIs, Types, and Functions
Defines enum `TestEnumSet` with `CREATE`, `OVERWRITE`, and `APPEND`. Uses `ObjectWritable.writeObject/readObject`, direct `EnumSetWritable.write/readFields`, `get`, `getElementType`, `iterator`, and `AvroTestUtil.testReflect` over the generic `testField`.

## Control Flow and State
Non-empty sets can infer element type; empty and null sets without an explicit type must throw. With explicit `TestEnumSet.class`, both empty and null values serialize through `ObjectWritable` and round-trip. Direct write/read verifies iterator order and value equality.

## Dependencies and Integration Points
Integrates Java `EnumSet`, Hadoop object serialization, Avro reflection, and generic type introspection.

## Risks and Test Signals
Risks are type erasure for empty/null sets, Avro schema namespace/class mapping, and preserving null vs empty. Signals are expected construction failures, round-trip equality, element type identity, and Avro schema equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestEnumSetWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestGenericWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestGenericWritable.java

## Purpose
Tests `GenericWritable` wrapper behavior, type registration enforcement, and propagation of `Configuration` into wrapped configurable values.

## Important APIs, Types, and Functions
Defines dummy `Foo implements Writable`, `Bar implements Writable, Configurable`, `Baz extends Bar`, and `FooGenericWritable extends GenericWritable` with supported types `Foo`, `Bar`, and `Baz`. Uses `TestWritable.testWritable`, `setConf`, `set`, `get`, and equality overrides.

## Control Flow and State
`setUp()` creates a configuration with a sentinel key. `testFooWritable()` wraps a plain writable. `testBarWritable()` wraps a configurable writable and asserts the deserialized wrapped object has non-null conf. `testBazWritable()` asserts subclass deserialization sees the sentinel config during `readFields`. `testSet()` accepts registered `Foo` and rejects unregistered `IntWritable`. `testGet()` checks object retrieval.

## Dependencies and Integration Points
Integrates with Hadoop `Configurable`, `Configuration`, `Text` serialization, and shared `TestWritable` round-trip utilities. It protects polymorphic writable serialization used by RPCs and protocol containers.

## Risks and Test Signals
Risks are misordered type id mapping, missing configuration propagation before `readFields`, and weak equality/hash implementations in dummy types. Signals are round-trip equality, `Configurable` conf presence, sentinel config assertion, and runtime rejection of unregistered types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestGenericWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestIOUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestIOUtils.java

## Purpose
Unit tests for `IOUtils` stream copy/close policy, file-channel writes, compressed read error wrapping, skip semantics, directory listing, quiet close behavior, and exception wrapping.

## Important APIs, Types, and Functions
Uses `IOUtils.copyBytes` overloads, `writeFully`, `wrappedReadForCompressedData`, `skipFully`, `listDirectory`, `closeStreams`, and `wrapException`. Mockito mocks stream close/read behavior; real `RandomAccessFile` and `FileChannel` validate writes; `NoEntry3Filter` implements `FilenameFilter`.

## Control Flow and State
Copy tests verify close behavior for `close=true/false`, including output/input close exceptions and runtime exceptions. `testWriteFully()` writes a 10k byte array at current position and at an explicit halfway offset. `testWrappedReadForCompressedData()` converts an `InternalError` into an `IOException`. `testSkipFully()` checks exact premature EOF messages. Directory and close-stream tests create temporary filesystem state and clean it. `testWrapException()` checks reflection-based exception wrapping and fallback `PathIOException`.

## Dependencies and Integration Points
Integrates Java IO/NIO, Apache Commons `FileUtils`, Hadoop `PathIOException`, `GenericTestUtils`, and `LambdaTestUtils`. These utilities are used broadly across Hadoop filesystem and compression code.

## Risks and Test Signals
Risks include resource leaks, suppressed close exceptions, partial channel writes, exact EOF accounting, and platform filesystem cleanup. Signals are Mockito close verification, exact messages, on-disk byte comparisons, filtered directory membership, and exception class/path checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestIOUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMD5Hash.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMD5Hash.java

## Purpose
Tests `MD5Hash` serialization, ordering, digest-derived numeric helpers, string conversion, thread safety, and reuse of digest factories after IO failure.

## Important APIs, Types, and Functions
`getTestHash()` builds random MD5 bytes through `MessageDigest`. Tests use `MD5Hash` constructors from byte arrays/string hex, `MD5Hash.digest(String/InputStream)`, `quarterDigest`, `halfDigest`, `hashCode`, `compareTo`, and `TestWritable.testWritable`. `SubjectInheritingThread` runs concurrent construction/equality loops.

## Control Flow and State
`testMD5Hash()` checks all-zero/all-ones/random hashes for writable round trip, equality, ordering, string reconstruction, numeric extraction, hash collision avoidance for nearby values, and concurrent equality. `testFactoryReturnsClearedHashes()` forces an input stream to throw after reads and then asserts later string digest results are still correct.

## Dependencies and Integration Points
Depends on Java security `MessageDigest`, Hadoop thread helper, and writable test utilities. It protects digest use in checksums, block IDs, and metadata comparisons.

## Risks and Test Signals
Risks are signed-byte ordering, digest instance reuse after exceptions, and thread-local/shared state contamination. Signals are exact numeric digest values, equality under concurrency, and digest stability after an injected stream failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMD5Hash.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMapFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMapFile.java

## Purpose
Comprehensive tests for `MapFile` reader/writer behavior, index construction/repair, seek/getClosest/midKey/finalKey APIs, file rename/delete/merge helpers, constructor compatibility, and failure paths.

## Important APIs, Types, and Functions
Uses `MapFile.Writer`, `MapFile.Reader`, `MapFile.rename`, `delete`, `fix`, `Merger`, writer options `keyClass`, `valueClass`, `compression`, reader comparator options, `WritableComparator`, `SequenceFile.CompressionType`, local filesystem, Mockito spies, and cleanup via `IOUtils.cleanupWithLogger`. Helpers create writers/readers under a temp `TEST_DIR` with index interval 4.

## Control Flow and State
`setup()` deletes and recreates the temp root for each test. Current API tests write ordered key/value pairs and validate `getClosest`, `midKey`, `finalKey`, iteration reset, seek success/failure, type mismatches, and key ordering enforcement. File-operation tests validate rename success, false return and thrown IO paths, mkdir failures, path filesystem exceptions, and delete. Index repair tests remove/rename the `index` file and call `MapFile.fix`, including block-compressed data. Deprecated constructor tests instantiate legacy writer/reader signatures. Merge writes five overlapping sorted map files, merges them, checks global sorted iteration, and verifies inputs are deleted. A `main` invocation smoke-tests `MapFile.main`.

## Dependencies and Integration Points
Integrates `SequenceFile` data/index files, Hadoop local filesystem, compression codec plumbing, writable comparators, and MapFile command-line behavior. It is a high-value persistence regression suite because `MapFile` is an indexed directory containing data and index sequence files.

## Risks and Test Signals
Risks include stale temp files, incorrect path in `testFix()` when deleting `./.testFix.mapfile/index`, broad catch/fail blocks obscuring root causes, and mocked codecs not exercising real compression streams. Signals include exact closest-key boundary behavior, `midKey` null for empty files, IO messages for rename/mkdir failures, sorted merge ordering, deleted inputs, repaired indexes with zero misses, and exception on descending append.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMapFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMapWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMapWritable.java

## Purpose
Tests `MapWritable` copy construction, nested maps, unknown class tracking, repeated deserialization safety, equality/hashCode, and string representation.

## Important APIs, Types, and Functions
Uses `MapWritable.put`, copy constructor, `entrySet`, `keySet`, `containsKey`, `get`, `getNewClasses`, `write`, `readFields`, `equals`, `hashCode`, and `toString`. It uses `Text`, `BytesWritable`, deprecated `UTF8`, `IntWritable`, and byte/data streams.

## Control Flow and State
The main test builds a map of text keys to bytes values, copies it, and compares all entries, then builds a map-of-maps and verifies nested copies. `testForeignClass()` verifies deprecated `UTF8` counts as one new class across copies. `testMultipleCallsToReadFieldsAreSafe()` serializes a one-entry map, mutates the instance, rereads the original bytes, and asserts stale entries were cleared. Equality tests compare same/different entries; `testToString()` checks `{5=value}`.

## Dependencies and Integration Points
Protects Hadoop's dynamic writable class-id mapping in map payloads, including nested maps and legacy `UTF8` support.

## Risks and Test Signals
Risks include class registry growth across copies, stale map entries after `readFields`, and equality/hash consistency. Signals are size equality, nested value compare, `getNewClasses()==1`, restored original map size, and deterministic string output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMapWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMoreWeakReferencedElasticByteBufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMoreWeakReferencedElasticByteBufferPool.java

## Purpose
Additional non-parameterized tests for `WeakReferencedElasticByteBufferPool`, focusing on mixed direct/heap buffers and invalid size/null inputs.

## Important APIs, Types, and Functions
Uses `WeakReferencedElasticByteBufferPool.getBuffer`, `putBuffer`, `release`, and `getCurrentBuffersCount(boolean direct)`. `assertBufferCounts()` asserts direct and heap pool counts with AssertJ. `LambdaTestUtils.intercept` checks expected exceptions.

## Control Flow and State
`testMixedBuffersInPool()` obtains direct and heap buffers of several sizes, verifies the pool count is zero while checked out, returns them in mixed order, checks direct/heap counts, then releases and checks zero. `testUnexpectedBufferSizes()` verifies zero-length direct buffers overflow on write, negative length is rejected, and null buffer return throws.

## Dependencies and Integration Points
Integrates Java NIO `ByteBuffer`, Hadoop test base, and byte buffer pool counters. This pool can be used by IO paths that reuse buffers without strong references.

## Risks and Test Signals
Risks are count accuracy across direct/heap pools, weak-reference cleanup not deterministically exercised, zero/negative size edge cases, and null input handling. Signals are explicit count transitions and exception types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMoreWeakReferencedElasticByteBufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestObjectWritableProtos.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestObjectWritableProtos.java

## Purpose
Tests `ObjectWritable` support for protocol buffer messages.

## Important APIs, Types, and Functions
Uses Hadoop shaded/thirdparty protobuf `DescriptorProtos.EnumValueDescriptorProto`, protobuf `Message`, `ObjectWritable.writeObject`, `ObjectWritable.readObject`, `DataOutputBuffer`, `DataInputBuffer`, and `Configuration`. Three tests call `doTest()` with 1, 2, and 3 protos.

## Control Flow and State
`doTest(numProtos)` builds `numProtos` enum-value descriptor messages named `testN` with number `N`, writes them to one buffer with declared protobuf class, resets an input buffer, reads them back in order, and asserts protobuf equality.

## Dependencies and Integration Points
Validates `ObjectWritable` special handling of protobuf messages used in Hadoop RPC/protocol surfaces. Depends on thirdparty protobuf shading.

## Risks and Test Signals
Risks include class name preservation, parser lookup for protobuf classes, and multiple-message stream boundaries. Signals are equality for one and multiple consecutive protobuf messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestObjectWritableProtos.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSecureIOUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSecureIOUtils.java

## Purpose
Tests secure file opening helpers that enforce expected owner/group when native IO is available, and creation behavior for existing files.

## Important APIs, Types, and Functions
Uses `SecureIOUtils.openForRead`, `openFSDataInputStream`, `openForRandomRead`, forced secure variants, `createForWrite`, `SecureIOUtils.AlreadyExistsException`, `NativeIO.isAvailable`, `FileSystem.getLocal(conf).getRaw()`, and JUnit lifecycle/timeout annotations.

## Control Flow and State
`makeTestFile()` creates three target files under `target/`, writes `hello`, and records real owner/group from local raw filesystem status. Unrestricted and correctly restricted reads must close successfully. Incorrect restriction assumes native IO availability, then tries invalid user ownership for input stream, FSDataInputStream, and random read, expecting `IOException`. `testCreateForWrite()` asserts creating over an existing file fails. `removeTestFile()` deletes all three files.

## Dependencies and Integration Points
Integrates Java files, Hadoop raw local filesystem ownership, native IO availability, and secure open wrappers used by localizer and security-sensitive code.

## Risks and Test Signals
Risks include platform-specific owner/group behavior, native library availability gating, octal permission semantics, and cleanup failures. Signals are successful opens for null/real owners, expected IO failures for invalid owner under native IO, and `AlreadyExistsException` for existing create.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSecureIOUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFile.java

## Purpose
Broad regression suite for `SequenceFile`: write/read, raw APIs, compression modes, sorting, merging, metadata, close/error behavior, writer creation semantics, serialization availability, stream capabilities, writable-name aliases, and a manual CLI harness.

## Important APIs, Types, and Functions
Uses `SequenceFile.createWriter`, `SequenceFile.Reader`, `SequenceFile.Sorter`, `SequenceFile.Metadata`, `CompressionType.NONE/RECORD/BLOCK`, `DefaultCodec`, `RandomDatum`, `WritableComparator`, `StreamCapabilities.HSYNC/HFLUSH`, `WritableName`, custom `Serialization`, `Serializer`, and `Deserializer`. Helpers `writeTest`, `readTest`, `sortTest`, `checkSort`, `mergeTest`, `newSorter`, `readMetadata`, `writeMetadataTest`, and `sortMetadataTest` implement repeated file-format workflows.

## Control Flow and State
`testZlibSequenceFile()` runs a full compressed sequence-file workflow with random seed, writing 10k records in no, record, and block compression, then reading, sorting, checking sort order, and merging in fast and normal modes. `readTest()` alternates raw and object APIs. Metadata tests write/read metadata under all compression modes and sort with metadata. Close tests verify double close does not corrupt codec-pool reuse and erroneous/zero-length readers close streams and throw EOF. Creation tests cover existing files, recursive parent creation, and using the supplied filesystem. Serialization tests assert missing serializer/deserializer errors, hflush/hsync capabilities on raw local FS, and aliasing a serialized class name to another compatible type. The `main` method parses CLI options for manual create/read/sort/merge checks.

## Dependencies and Integration Points
Integrates local/raw filesystems, compression codecs, codec pool behavior, Hadoop serialization framework, Avro reflect serialization as a negative configuration, writable name registry, and sequence-file sort/merge internals. This is a central persistence-format compatibility suite.

## Risks and Test Signals
Risks include long runtime and random seed reproducibility, unannotated `testSorterProperties()` not running as a JUnit test, filesystem temp cleanup, global `WritableName` alias side effects, and exact error-message coupling. Signals include record/value equality, raw API coverage, sorted TreeMap comparison, metadata equality, codec-pool double-close safety, closed stream after constructor failure, EOF on zero-length input, explicit serializer error prefixes, nonzero file length after sync operations, and alias-based deserialization values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileAppend.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileAppend.java

## Purpose
Tests append support for `SequenceFile` with Java serialization and compression compatibility checks.

## Important APIs, Types, and Functions
Uses static `Configuration` with `JavaSerialization`, raw local file system, `SequenceFile.createWriter`, `Writer.appendIfExists(true)`, `Writer.compression`, `Writer.metadata`, `SequenceFile.Reader`, `GzipCodec`, `DefaultCodec`, `JavaSerializationComparator`, and `SequenceFile.Sorter`. Helpers `verify2Values()` and `verifyAll4Values()` read object keys/values with `Reader.next((Object)null)` and `getCurrentValue`.

## Control Flow and State
Lifecycle opens a raw local FS once. `testAppend()` writes two Long/String records with metadata, appends two more, verifies metadata remains original despite mutated metadata object, and rejects mismatched compression options. Compression-specific tests repeat append for record, block, and none compression; native profile is assumed for gzip cases. `testAppendSort()` writes unsorted appended blocks, sorts the result, and verifies ordered values.

## Dependencies and Integration Points
Integrates sequence-file append header validation, compression codec compatibility, Java serialization, raw local FS append support, metadata persistence, and sorting of appended files.

## Risks and Test Signals
Risks include native gzip availability, reuse of the same filename in record/block compression tests, and exact compatibility rules for `NONE` with codec option ignored. Signals are two-record and four-record reads, metadata value immutability, expected `IllegalArgumentException` on mismatched compression, and sorted output verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileAppend.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileSerialization.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileSerialization.java

## Purpose
Focused test for `SequenceFile` with Java serialization of non-Writable key/value classes.

## Important APIs, Types, and Functions
Uses `Configuration` key `io.serializations=JavaSerialization`, local `FileSystem`, `SequenceFile.createWriter(fs, conf, file, Long.class, String.class)`, and legacy `SequenceFile.Reader`.

## Control Flow and State
Each test setup creates fresh configuration and local filesystem; teardown closes it. The test deletes any existing temp file, writes two Long/String pairs, closes, reads keys and current values through object APIs, asserts both values in order, and asserts EOF via null key.

## Dependencies and Integration Points
Validates `SequenceFile` integration with Hadoop's Java serialization plugin rather than the default writable serializer.

## Risks and Test Signals
Risks are serializer configuration drift and temp file reuse. Signals are exact object key/value equality and null at end of file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileSerialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileSync.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileSync.java

## Purpose
Tests sequence-file sync marker intervals and `Reader.sync(offset)` behavior for default and low sync intervals.

## Important APIs, Types, and Functions
Uses `SequenceFile.Writer` options `file`, `compression(NONE)`, `keyClass`, `valueClass`, and `syncInterval`; `SequenceFile.Reader` file and stream constructors; `Reader.sync`; `Reader.next`; `FSDataInputStream`; `IntWritable`; and `Text`.

## Control Flow and State
`writeSequenceFile()` writes numbered records with deterministic prefix text and random digit padding. `forOffset()` calls `sync(off)`, reads the next key/value, and asserts expected record id and prefix. `testDefaultSyncInterval()` writes 8000 records and verifies offsets 0, 65, 2000, and 0 across both reader construction styles, expecting offset 2000 to jump to record 1101 under default sync. `testLowSyncpoint()` sets sync interval 2000 bytes, writes 2000 records, and expects offset 2000 to jump to record 21.

## Dependencies and Integration Points
Integrates sequence-file sync marker generation, reader seek/sync semantics, local filesystem file and stream access, and record layout sizing.

## Risks and Test Signals
Risks include sensitivity to record size changes, default sync interval changes, random payload not affecting prefix, and resource cleanup through manual delete. Signals are exact expected record ids for offsets and writer `syncInterval` field equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileSync.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSetFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSetFile.java

## Purpose
Tests `SetFile`, a sorted set-like file format built on `MapFile`, for random membership, compression modes, access methods, and manual CLI behavior.

## Important APIs, Types, and Functions
Uses `SetFile.Writer`, `SetFile.Reader`, `MapFile.delete`, `WritableComparator.get`, `RandomDatum`, `CompressionType.NONE/BLOCK`, local filesystem, and logger. Helpers generate sorted random data, write set entries, read random samples by `seek`, and create an `IntWritable` reader.

## Control Flow and State
`testSetFile()` writes 10,000 sorted random values with no compression and block compression, then samples approximately sqrt(n) random values and asserts `seek` succeeds. `testSetFileAccessMethods()` writes ten integer entries, checks `next`, checks `get(size/2)` returns `size/2 + 1`, and null for out-of-range. The CLI parses count/create/check/compress options.

## Dependencies and Integration Points
Integrates sorted writable comparison, `MapFile` directory persistence, local filesystem temp paths, and sequence-file compression.

## Risks and Test Signals
Risks are random sampling missing edge cases, surprising `get(i)` next-greater behavior documented only in a comment, and broad catch/fail blocks. Signals are successful seek for generated values, next/get/null access behavior, and compression-mode readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSetFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSortedMapWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSortedMapWritable.java

## Purpose
Tests `SortedMapWritable` ordering, copy construction, nested maps, foreign class propagation, equality/hashCode contract, and class-map copying through `putAll`.

## Important APIs, Types, and Functions
Uses generic `SortedMapWritable<Text>`, `put`, `putAll`, copy constructor, `firstKey`, `lastKey`, `entrySet`, `keySet`, `getNewClasses`, `equals`, `hashCode`, and protected-ish class maps `classToIdMap`/`idToClassMap` visible from the package.

## Control Flow and State
The main test inserts three text keys, verifies first/last ordering, copies and compares values, then nests maps and verifies nested copy contents. `testForeignClass()` confirms deprecated `UTF8` registers one unknown class across copies. `testEqualsAndHashCode()` checks null inequality, empty equality, different entries, same entries inserted in different order, and same keys/different values. `testPutAll()` asserts entries and class metadata are copied.

## Dependencies and Integration Points
Protects sorted writable map serialization and class-id propagation, including legacy classes and nested map structures.

## Risks and Test Signals
Risks include generic unchecked casts, class metadata leakage, equality depending on sorted entry sets, and package-level class map assumptions. Signals are first/last keys, nested value comparisons, unknown class count, hash/equality contract checks, and class-map containment after `putAll`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSortedMapWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestText.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestText.java

## Purpose
Comprehensive unit tests for Hadoop `Text` UTF-8 string storage, encoding/decoding, writable IO, comparison, search, validation, clearing, copy/append behavior, concurrency, Avro reflection, character access, known-length reads, byte-to-codepoint conversion, UTF-8 length calculation, and raw byte setting.

## Important APIs, Types, and Functions
Uses `Text` constructors, `set`, `append`, `clear`, `encode`, `decode`, `writeString`, `readString`, `readFields`, `write`, `readWithKnownLength`, `validateUTF8`, `find`, `charAt`, `bytesToCodePoint`, `utf8Length`, `getBytes`, `getLength`, `getTextLength`, `copyBytes`, and `Text.Comparator`. Helpers generate random valid Java strings and long strings beyond `Short.MAX_VALUE`. `ConcurrentEncodeDecodeThread` repeatedly uses `WritableUtils.writeString/readString`.

## Control Flow and State
Random generation uses a fixed seed and avoids unpaired surrogates. Tests round-trip both normal and very long strings through writable serialization, static encode/decode, and Java UTF-8. Limited IO tests assert max-length enforcement. Compare tests ensure raw serialized comparator matches object comparison. Find/validate/clear/copy tests check byte offsets, buffer capacity retention, alias safety, and text length updates. Avro reflection sets the trusted packages system property. Byte/codepoint tests cover valid advancement and truncated invalid UTF. `testSetBytes()` checks raw byte array length/text length handling.

## Dependencies and Integration Points
Integrates Hadoop writable utilities, `WritableComparator`, Avro reflection helper, Guava `Bytes.concat`, Java NIO charset/bytebuffer APIs, and thread helper. `Text` is a foundational writable string type used across Hadoop storage/RPC.

## Risks and Test Signals
Risks include Unicode surrogate handling, long string length encoding, raw comparator correctness, static/global Avro property mutation, a likely typo in concurrency join calling `thread2.join()` twice, and broad exception handling in some edge tests. Signals are random round-trip equality, raw comparator parity, exact find offsets for euro sign, buffer length/capacity assertions, expected `BufferUnderflowException`, and UTF-8 length boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestText.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestTextNonUTF8.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestTextNonUTF8.java

## Purpose
Tests `Text` construction from non-UTF8 bytes and preservation of raw bytes.

## Important APIs, Types, and Functions
Uses `Text(byte[])`, `Text.validateUTF8(byte[])`, `Text.getBytes`, `MalformedInputException`, and `Arrays.equals`.

## Control Flow and State
The test creates a byte array of repeated `0xff`, constructs `Text`, calls `validateUTF8` expecting a malformed-input path, asserts the local `nonUTF8` flag remains false, and asserts `Text.getBytes()` matches the original bytes.

## Dependencies and Integration Points
Validates `Text` can hold arbitrary bytes even when validation rejects them. This matters for legacy or corrupt data paths where raw bytes must be preserved until explicitly decoded.

## Risks and Test Signals
The `nonUTF8` flag name/value is confusing because it is initialized false and remains false after catching `MalformedInputException`. The meaningful signal is raw byte preservation in `Text`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestTextNonUTF8.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestUTF8.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestUTF8.java

## Purpose
Tests deprecated `UTF8` writable behavior, modified UTF byte conversion, IO compatibility with `DataInput.readUTF`, null-character encoding, supplementary Unicode decoding, and invalid/truncated UTF-8 diagnostics.

## Important APIs, Types, and Functions
Uses `UTF8` constructor, `UTF8.getBytes`, `writeString`, `readString`, `fromBytes`, `TestWritable.testWritable`, `DataInputStream.readUTF`, `StringUtils.byteToHexString`, and `GenericTestUtils.assertExceptionContains`.

## Control Flow and State
Random strings are generated from arbitrary `char` values for 10,000 iterations. Writable and IO tests round-trip through Hadoop buffers and Java modified UTF. `testNullEncoding()` verifies embedded null is encoded as standard UTF-8 in the stored payload after the two-byte length prefix. Supplementary-plane test uses a surrogate pair and validates four UTF-8 bytes and round trip. Invalid tests assert `UTFDataFormatException` messages for illegal bytes, illegal five-byte sequence, and truncated four-byte sequence.

## Dependencies and Integration Points
Protects deprecated `UTF8` compatibility for old writable data and older APIs, while checking modern strict UTF-8 error behavior.

## Risks and Test Signals
Risks are deprecated API behavior drift, random generation including unusual surrogate values, exact hex snippets in error messages, and modified-vs-standard UTF distinction. Signals are 10k writable/IO round trips, exact hex for supplementary character, and exception text for invalid/truncated sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestUTF8.java -->
