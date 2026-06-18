# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestException.java

Purpose: Marker annotation describing an expected exception type and optional message regex for test methods.

Important APIs/types/functions: annotation elements `exception()` and `msgRegExp()` with default `.*`.

Control flow: no executable logic; `TestExceptionHelper` reads the annotation during JUnit exception handling.

State and persistence: annotation metadata only.

Dependencies/integration: Java annotation model and `TestExceptionHelper`.

Risks and test signals: lightweight compatibility layer for older test style. It must be paired with the registered helper extension to have effect.
