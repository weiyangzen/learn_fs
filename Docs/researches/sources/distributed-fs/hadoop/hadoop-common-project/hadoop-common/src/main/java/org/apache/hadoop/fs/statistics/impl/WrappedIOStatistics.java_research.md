# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/WrappedIOStatistics.java

Purpose: base class that delegates `IOStatistics` map accessors to a wrapped statistics instance and allows the wrapped instance to be installed later.

Important APIs, types, and functions: constructor, protected `setWrapped()`, protected `getWrapped()`, and map accessors for all statistic categories.

Control flow: subclasses either pass the wrapped instance at construction or call `setWrapped()` after building it. Accessor methods delegate to the current wrapped object.

State and persistence: stores one mutable reference to wrapped statistics. It does not own metric values directly.

Dependencies and integration points: implements `IOStatistics`; used by `IOStatisticsStoreImpl` so the store can initialize maps before exposing a dynamic view.

Risks and test signals: access before a wrapped instance is set can fail. Tests should cover late binding, delegation, replacement behavior, and null wrapped safeguards.
