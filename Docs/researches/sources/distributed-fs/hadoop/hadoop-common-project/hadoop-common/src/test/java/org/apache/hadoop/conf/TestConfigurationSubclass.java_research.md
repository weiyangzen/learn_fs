# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigurationSubclass.java

## Purpose

`TestConfigurationSubclass` verifies behavior expected by subclasses of `Configuration`: protected property access through `getProps`, reload callbacks through overridden `reloadConfiguration`, and non-quiet error reporting for missing resources.

## Important APIs and types

- `SubConf extends Configuration` exposes `getProperties()` by calling protected `getProps()`.
- `SubConf.reloadConfiguration()` calls `super.reloadConfiguration()` and records a `reloaded` flag.
- `Configuration.addDefaultResource` triggers reload behavior for existing configurations.
- `setQuietMode(false)` and `addResource("not-a-valid-resource")` exercise non-quiet failure when properties are loaded.

## Control flow

`testGetProps` constructs `SubConf(true)` and verifies default resources populate `hadoop.tmp.dir`. `testReload` constructs a subclass instance, adds `empty-configuration.xml` as a default resource, and expects the override to have been called. `testReloadNotQuiet` adds an invalid resource in non-quiet mode, verifies that adding alone does not reload, then calls `getProperties()` and expects a runtime failure containing `"not found"`.

## State and persistence behavior

The file uses a classpath XML resource and mutates global default resources through `Configuration.addDefaultResource`. `SubConf` keeps an in-memory boolean reload marker. No files are written.

## Dependencies and integration points

The tests integrate subclassing hooks in `Configuration` with the classpath resource `empty-configuration.xml`, default resource registration, protected property materialization, and quiet/non-quiet resource handling.

## Risks and edge cases

- Adding a default resource is global static state and can affect later configuration tests.
- The reload flag only proves the override was entered, not that all internal caches were refreshed correctly.
- Non-quiet failure is asserted via message substring, which can be brittle across exception wording changes.

## Test signals

Useful signals are subclass access to default-loaded properties, reload callback invocation after adding a default resource, lazy loading of invalid resources, and exception surfacing when quiet mode is disabled.
