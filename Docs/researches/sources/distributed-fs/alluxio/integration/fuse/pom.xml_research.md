# sources/distributed-fs/alluxio/integration/fuse/pom.xml

Purpose: Maven module descriptor for the Alluxio FUSE integration artifact and shaded runnable jar.

Important APIs and helpers: declares parent `alluxio-integration`, artifact `alluxio-integration-fuse`, module name/description, build path property, dependencies, and a `maven-shade-plugin` execution named `uber-jar`.

Control flow and state: during `package`, the shade plugin builds `${project.artifactId}-${project.version}-jar-with-dependencies`, merges service resources, Apache license/notice resources, and filters signature/license files. Runtime dependencies include `jnr-fuse`, Guava, commons-cli, server common, fs client, core common, jnifuse fs, and Jersey. Test dependencies include core-common test jar and local/S3A underfs modules.

Dependencies and integration: this POM is what the FUSE launcher scripts expect at `target/alluxio-integration-fuse-${VERSION}-jar-with-dependencies.jar`.

Risks and test signals: packaging is sensitive to shaded dependency services and jar naming; launcher scripts fail if this exact output is absent. The filter artifact pattern contains a trailing space in `*:* `, which is suspicious and could affect matching.
