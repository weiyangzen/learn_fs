# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestParam.java

Purpose: Unit tests for REST parameter parsing abstractions.

Important APIs/types/functions: generic helper `test`, concrete `BooleanParam`, `ByteParam`, `ShortParam`, `IntegerParam`, `LongParam`, `EnumParam`, `StringParam`, and regex-constrained `StringParam`.

Control flow: the helper validates name/domain/default value, default behavior for null/empty strings, valid parsing, and failure for invalid syntax/out-of-range values. Individual tests cover boolean, byte, short including octal radix constructor, integer, long, enum domain, unconstrained string, and regex-constrained string.

State and persistence: none.

Dependencies/integration: JUnit, Java regex, and the WSRS parameter base classes used by HTTPFS request parsing.

Risks and test signals: strong parsing-contract signal across primitive parameter types. It uses deprecated `new Short(...)` style and checks exceptions by manual try/fail rather than `assertThrows`.
