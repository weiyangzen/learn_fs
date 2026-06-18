<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-tests.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-tests.h

## Purpose
Provides reusable template factories that create command mocks with specific synthetic command lines. Each factory configures expectations before returning the mock as the parameter for shared `HdfsTool` fixtures.

## Important APIs, Types, And Functions
Factories include `PassAPath`, `PassRecursive`, `PassRecursivePath`, `PassFOptAndAPath`, `CallHelp`, `Pass2Paths`, `Pass3Paths`, `PassNOptAndAPath`, `PassOwnerAndAPath`, `PassRecursiveOwnerAndAPath`, `PassPermissionsAndAPath`, `PassInvalidPermissionsAndAPath`, `PassRecursivePermissionsAndAPath`, `PassQOpt`, `PassQOptAndPath`, `PassPOpt`, `PassMOpt`, `PassFOpt`, `PassPOptAndPath`, `PassMOptPermissionsAndAPath`, `PassMPOptsPermissionsAndAPath`, `PassNStrMNumAndAPath`, `PassNOpt`. They build static `std::string` argv storage, assemble `char *argv[]`, construct `T(argc, argv)`, and call `SetExpectations()` with the factory identity plus argument values.

## Control Flow
`hdfs-tool-tests.cc` chooses these factories for each tool and fixture type. The factory encodes the command-line shape; the mock-specific `SetExpectations()` encodes the handler that should be reached after production parsing.

## State And Persistence
State is limited to static strings used as stable argv backing storage. There is no persistence and no filesystem activity.

## Dependencies And Integration Points
Depends only on standard strings and memory, but it is tightly coupled to every mock's `SetExpectations()` overload and every production tool's option grammar.

## Risks
Static argv buffers are shared across tests but contain immutable test values, so they are acceptable for normal gtest execution. The exact factory pointer is used for expectation dispatch, making refactoring to lambdas or bind expressions risky. New command options need matching factory and mock branches.

## Test Signals
Compilation verifies every mock accepts the factory signature. Runtime suite failures pinpoint parser changes through unexpected throws, false returns, or unmet mock calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-tests.h -->
