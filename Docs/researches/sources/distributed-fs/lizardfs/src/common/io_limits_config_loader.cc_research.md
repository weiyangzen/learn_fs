<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_config_loader.cc -->
# sources/distributed-fs/lizardfs/src/common/io_limits_config_loader.cc

## Purpose
Implements parsing for simple I/O limit configuration streams containing `subsystem` and `limit` directives plus shell-style full-line comments. The source was read completely for this report.

## Important APIs, Types, And Functions
`IoLimitsConfigLoader::load(std::istream&&)` clears previous limits, reads commands, fills `subsystem_` and `limits_`, rejects duplicate groups, and throws `ParseException` on malformed input.

## Control Flow
The parser streams token by token until EOF. `subsystem` consumes one string, `limit` consumes group and numeric limit, comments beginning with `#` skip the rest of the line, and unknown commands fail immediately. If any classified group is present, a subsystem is mandatory.

## State And Persistence Behavior
State lives in the loader object: a map of group limits and the last parsed subsystem. No persistence is performed here.

## Dependencies And Integration Points
Uses `common/exceptions.h` and `io_limit_group.h` for `kUnclassified`. The parsed map is consumed by `IoLimitsDatabase::setLimits` and reconfiguration paths.

## Risks And Edge Cases
Inline trailing comments after a numeric limit are tolerated only because formatted extraction stops before `#`; malformed numeric tokens poison the stream. Reusing a loader keeps the old subsystem unless overwritten.

## Test Signals
Covered by `io_limits_config_loader_unittest.cc` for valid files, missing subsystem, bad numeric values, unknown keywords, repeated groups, comments, and unclassified-only configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_config_loader.cc -->
