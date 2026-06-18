## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsConfig.java

Purpose: Metrics-specific configuration loader and plugin factory built on Commons Configuration.

Important APIs/types/functions: Static `create`, `loadFirst`, constants for sink/source keys, `subset`, `getInstanceConfigs`, `getPlugin`, `getFilter`, `getClassName`, `getString`, and `toString` helpers.

Control flow: Loads the first available metrics properties file for a prefix, extracts per-instance subconfigs, overlays default keys, resolves classes with class loaders, instantiates plugins, and calls plugin `init`.

State and persistence: Wraps loaded properties in memory. No writes except stringification by `MetricsSystemImpl.currentConfig`.

Dependencies/integration: Used by `MetricsSystemImpl.configure*` to create sinks, filters, periods, queues, and source configs. Depends on Commons Configuration, reflection, Hadoop class loading utilities, and SLF4J.

Risks/test signals: Misconfigured class names, missing files, and default-instance overlay behavior are primary risks. Tests should cover prefix lookup order, plugin init, class-loader fallback, and instance regex parsing.
