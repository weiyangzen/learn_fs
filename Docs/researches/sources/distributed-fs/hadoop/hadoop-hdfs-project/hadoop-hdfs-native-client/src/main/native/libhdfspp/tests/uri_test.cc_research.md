<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/uri_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/uri_test.cc

## Purpose
Tests the libhdfs++ `hdfs::URI` parser, encoder, mutators, query helpers, and error reporting for ordinary HDFS paths and encoded URI components.

## Important APIs, Types, And Functions
Helpers `expect_uri_throw()` and `expect_uri_nothrow()` wrap `URI::parse_from_string()` and assert exception behavior. Test cases cover `UriTest.TestDegenerateInputs`, `UriTest.TestNominalInputs`, `UriTest.TestEncodedInputs`, `UriTest.TestDecodedInputsAndOutputs`, `UriTest.TestSetters`, `UriTest.QueryManip`. Assertions exercise `get_scheme`, `get_host`, port accessors, `get_path`, encoded getters, `get_path_elements`, `get_query_elements`, setters, `add_path`, `add_query`, `remove_query`, and `str()`.

## Control Flow
Each test parses or constructs a URI, then checks decoded and encoded views. Negative helpers verify `uri_parse_error::what()` carries the original malformed string. The local `main()` initializes Google Mock and runs all tests.

## State And Persistence
Only stack-local URI objects and temporary strings are used. No persistence or filesystem state.

## Dependencies And Integration Points
Depends on `hdfspp/uri.h`, gtest, and gmock. It validates behavior relied on by every HDFS command tool that calls `parse_path_or_exit()`.

## Risks
The tests codify specific encoding semantics such as plus-to-space in paths and encoded query handling. Missing cases include IPv6 authorities, userinfo, and unusual path normalization. Error tests check only selected malformed inputs.

## Test Signals
Passing tests signal stable URI parsing, encoding round trips, query manipulation, and malformed-input exception behavior for command-line path handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/uri_test.cc -->
