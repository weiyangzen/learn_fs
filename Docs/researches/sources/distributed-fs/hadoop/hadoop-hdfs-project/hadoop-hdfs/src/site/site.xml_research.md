# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/site/site.xml

## Purpose
This Maven site descriptor configures the generated documentation site for the `hadoop-hdfs` module. It names the project as `Apache Hadoop ${project.version}`, selects the Maven Stylus skin, and adds a top-level link back to the Apache Hadoop website.

## Important APIs, Types, and Functions
This is declarative XML rather than executable code. Important elements are:
- `<project name="Apache Hadoop ${project.version}">`, which sets the displayed site project name using Maven property interpolation.
- `<skin>`, with `org.apache.maven.skins:maven-stylus-skin:${maven-stylus-skin.version}`, which selects the documentation site's visual skin.
- `<body><links><item ... /></links></body>`, which defines a navigation link named `Apache Hadoop` pointing to `http://hadoop.apache.org/`.

## Control Flow
There is no runtime control flow. During Maven site generation, Maven reads this descriptor, interpolates properties from the build, resolves the configured skin artifact, and applies the body link configuration when rendering the module's site pages.

## State and Persistence Behavior
The file has no mutable runtime state. Its only persistence effect is build output: generated site pages inherit the configured project name, skin, and link. Changes to this file affect future site generation but not the running HDFS service.

## Dependencies and Integration Points
The descriptor depends on Maven Site Plugin conventions and the `maven-stylus-skin.version` property being defined in the broader Hadoop build. It integrates with HDFS module documentation under `src/site`, including Markdown content such as WebHDFS documentation, and with parent build configuration that supplies project version and plugin settings.

## Risks and Edge Cases
- A missing or incompatible `${maven-stylus-skin.version}` property would break site generation or produce an unexpected site theme.
- The Apache Hadoop link uses `http://` rather than `https://`; this is a documentation navigation choice but may be flagged by link or security scanners.
- Since this descriptor is module-scoped, changes can alter generated documentation appearance/navigation without affecting tests that only compile code.

## Test Signals
Validation is through Maven site generation rather than unit tests. A useful check is running the relevant Maven site goal for the HDFS module and verifying that the skin resolves, the project version is interpolated, and the Apache Hadoop navigation link appears.
