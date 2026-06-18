# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/site/site.xml

Purpose: Maven site descriptor for the Hadoop Common module.

Important elements: `<project name="Apache Hadoop ${project.version}">`, a `maven-stylus-skin` skin with version property `${maven-stylus-skin.version}`, and a body link to the Apache Hadoop website.

Control flow: declarative XML consumed by Maven Site tooling; no executable code.

State and persistence: affects generated site rendering rather than runtime state.

Dependencies/integration: depends on Maven site plugin conventions and project properties. It integrates the module documentation into the larger Hadoop website style.

Risks and test signals: broken skin artifact/version properties or stale HTTP links can break site generation. Test signal is successful Maven site rendering with expected project name and navigation link.
