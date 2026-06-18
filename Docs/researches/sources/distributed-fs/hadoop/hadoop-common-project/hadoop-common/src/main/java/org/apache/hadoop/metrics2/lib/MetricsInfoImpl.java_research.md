## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsInfoImpl.java

Purpose: Immutable `MetricsInfo` implementation used by `Interns`.

Important APIs/types/functions: Stores name and description, implements accessors, equality, hash, and string conversion.

Control flow: Created by interning factories and then shared wherever metadata is needed.

State and persistence: Final fields only; no persistence.

Dependencies/integration: Backing implementation for most non-enum metric info objects.

Risks/test signals: Equality/hash must match interning cache keys. Tests should cover same name/description reuse and different description inequality.
