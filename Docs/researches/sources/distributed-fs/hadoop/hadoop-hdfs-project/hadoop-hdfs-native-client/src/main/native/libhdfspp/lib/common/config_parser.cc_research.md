<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/config_parser.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/config_parser.cc

## Purpose
Implements the public `ConfigParser` facade over `ConfigurationLoader` and `HdfsConfiguration`. It gives clients typed access to Hadoop XML configuration values and resolved libhdfspp `Options` without exposing loader internals.

## Important APIs, Types, And Functions
`ConfigParser::impl` owns a `ConfigurationLoader` and `HdfsConfiguration`. Constructors accept no path, a vector of directories, or a colon-separated path. Public methods include `LoadDefaultResources`, `ValidateResources`, `get_int/string/bool/double/uri/options`, and `_or` variants that return caller-supplied defaults.

## Control Flow
Construction creates a new empty config, optionally sets the search path, and loads default resources. Vector paths are folded into a colon-separated search path. Getters ask `HdfsConfiguration` for an optional typed value; the `_or` helpers fall back when no value is present.

## State And Persistence
The parser owns an immutable snapshot of parsed config in memory. Move construction/assignment is defaulted; no config is written back to disk.

## Dependencies And Integration Points
It depends on `hdfspp/config_parser.h`, `HdfsConfiguration`, `ConfigurationLoader`, `Status`, and `URI`. It is a higher-level API entry for applications that need configuration parsing without creating a filesystem.

## Risks
The vector path accumulation prepends a separator before the first element, relying on `SetSearchPath` to ignore the empty component. Typed conversions inherit the permissive parsing behavior of `Configuration`, including partial numeric parses. `LoadDefaultResources` always returns true after assignment, even if no resources were found and an empty config was used.

## Test Signals
Tests should parse real `core-site.xml`/`hdfs-site.xml`, custom search paths, missing resources, typed values, defaults, URI parse failures, HA options, and move semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/config_parser.cc -->
