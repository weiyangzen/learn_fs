# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/site/site.xml

## Purpose
`site.xml` configures the Maven site for the HttpFS module.

## Important APIs, Types, and Functions
It declares project name `HttpFS`, uses `org.apache.maven.skins:maven-stylus-skin` with version property `${maven-stylus-skin.version}`, and adds a site link to Apache Hadoop.

## Control Flow
Maven site generation reads this descriptor to choose skin and navigation links. It is not loaded by HttpFS runtime code.

## State and Persistence
Static build metadata only. Generated site output is produced by Maven outside this file.

## Dependencies and Integration Points
It depends on the Maven site plugin ecosystem and the stylus skin version property from the parent build.

## Risks
The external link uses `http://hadoop.apache.org/` rather than HTTPS. Runtime risk is none; build/site risk appears if the skin version property is missing.

## Test Signals
No runtime or unit tests target this file. Its validation is through Maven site generation.
