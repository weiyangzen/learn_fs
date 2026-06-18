<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_config_loader.h -->
# sources/distributed-fs/lizardfs/src/common/io_limits_config_loader.h

## Purpose
Declares the loader object for I/O limit configuration files. The source was read completely for this report.

## Important APIs, Types, And Functions
`IoLimitsConfigLoader`, `LimitsMap = std::map<std::string,uint64_t>`, `load`, `subsystem`, and `limits` are the visible API.

## Control Flow
Header-only control flow is limited to simple const accessors; parsing is implemented in the `.cc` file.

## State And Persistence Behavior
Stores a subsystem string and ordered limits map. The ordered map matters because database reconciliation walks limits and existing groups in sorted order.

## Dependencies And Integration Points
Provides input for `IoLimitsDatabase`; depends on standard streams/maps and `platform.h`.

## Risks And Edge Cases
The rvalue-reference stream API encourages temporary streams, but callers must still supply a live stream object for the duration of `load`.

## Test Signals
Tests are in `io_limits_config_loader_unittest.cc`; compile coverage should also exercise consumers that include only the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_config_loader.h -->
