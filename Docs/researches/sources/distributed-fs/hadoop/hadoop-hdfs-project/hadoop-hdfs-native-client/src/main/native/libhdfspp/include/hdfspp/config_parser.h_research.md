# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/config_parser.h

## Purpose
`ConfigParser` is the public parser facade for Hadoop XML configuration resources used by libhdfs++.

## Important APIs, Control Flow, and State
Constructors accept no path, one path, or a vector of config directories. The class is movable, owns an opaque `impl` through `std::unique_ptr`, and offers `LoadDefaultResources`, resource validation, typed getters for int/string/bool/double/URI, and options conversion through `get_options`/`get_options_or`. Getters return false on missing or uncastable values; `_or` variants return defaults.

## Dependencies and Integration Points
It includes `options.h`, `uri.h`, and `status.h`. Builder-from-directory C APIs and C++ tools use configuration loading to fill `Options`, especially `defaultFS`, HA services, and timeouts.

## Risks and Test Signals
Parsing and type conversion are hidden in the implementation, so API tests should validate missing files, empty directories, malformed XML, duplicate keys, final/default resource precedence, bool/int/double conversion, URI parsing failures, move semantics, and Options extraction for HA services.
