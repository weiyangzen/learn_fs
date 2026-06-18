# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/ExpressionFactory.java

Purpose: singleton registry and instantiation factory for `find` expressions.

Important APIs and types: `getExpressionFactory()`, `registerExpression()`, `addClass()`, `isExpression()`, `getExpression()`, `createExpression(Class,Configuration)`, and `createExpression(String,Configuration)`.

Control flow: expression classes expose a static `registerExpression(ExpressionFactory)` method. The factory invokes that method reflectively, allowing each class to register one or more names. Parser lookups check `expressionMap`, then instantiate classes through `ReflectionUtils.newInstance()` with the command configuration.

State and persistence: singleton keeps an in-memory `Map<String, Class<? extends Expression>>`; no durable state.

Dependencies and integration: used by `Find` static initialization and parsing. Depends on reflection, Hadoop `ReflectionUtils`, and `StringUtils.stringifyException()` for failure reporting.

Risks: registration failures are wrapped in `RuntimeException`, making static initialization failures broad. `getExpression()` throws NPE on null configuration. Duplicate names overwrite previous registrations without warning. `createExpression(null, conf)` returns null, used while building help from known classes.

Test signals: cover reflective registration, alias registration, duplicate behavior, unknown expression, null config, invalid classname, and instantiated configurable receiving configuration.
