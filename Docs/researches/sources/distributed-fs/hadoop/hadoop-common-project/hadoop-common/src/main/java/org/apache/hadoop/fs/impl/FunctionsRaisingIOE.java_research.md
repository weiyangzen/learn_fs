# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FunctionsRaisingIOE.java

## Purpose
Deprecated compatibility holder for functional interfaces that throw IOException.

## Important APIs, Types, and Functions
FunctionRaisingIOE, BiFunctionRaisingIOE, CallableRaisingIOE.

## Control Flow
No flow beyond functional method invocation by callers.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Superseded by org.apache.hadoop.util.functional equivalents, retained for binary/source compatibility.

## Risks and Test Signals
Risk is removal or signature drift breaking external filesystem implementations. Compile compatibility tests are the key signal.
