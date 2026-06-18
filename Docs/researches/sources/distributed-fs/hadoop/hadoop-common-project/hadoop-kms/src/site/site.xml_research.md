# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/site/site.xml

## Purpose
`site.xml` is the Maven site descriptor for Hadoop KMS documentation.

## Important APIs, Types, and Functions
It declares project name `Hadoop KMS`, uses `maven-stylus-skin` with version from `${maven-stylus-skin.version}`, and adds a body link to Apache Hadoop.

## Control Flow
Maven site generation reads this descriptor to choose skin and navigation links.

## State and Persistence
This is static documentation build metadata and contains no runtime state.

## Dependencies and Integration Points
It integrates with Maven site tooling and the Hadoop documentation build.

## Risks
HTTP link uses `http://hadoop.apache.org/` rather than HTTPS. Missing skin version property would break site generation.

## Test Signals
Build validation should run the Maven site phase or descriptor validation to ensure the skin artifact and property resolve.
