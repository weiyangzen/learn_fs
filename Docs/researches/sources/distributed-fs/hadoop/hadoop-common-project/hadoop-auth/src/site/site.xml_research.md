<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/site/site.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/site/site.xml

## Purpose
Defines Maven Site metadata for the Hadoop Auth module.

## Important APIs, types, and functions
The XML declares project name `Hadoop Auth`, selects the `maven-stylus-skin` with a version property, and adds a body link to the Apache Hadoop website.

## Control flow
Maven site generation reads this descriptor to render module documentation. There is no application runtime flow.

## State and persistence
The file is persistent build/documentation configuration. It does not affect runtime authentication state.

## Dependencies and integration points
Integrates with Maven Site Plugin and module documentation under `src/site`. The skin version is supplied by Maven properties.

## Risks and test signals
Risks are broken site generation if the skin version property is missing or the external link changes. Tests/signals are Maven site build success and generated navigation correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/site/site.xml -->
