# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/site/site.xml

This Maven site descriptor defines the generated site skin and a single external Hadoop link for the `hadoop-hdfs-rbf` module. It is build metadata rather than runtime code.

The only meaningful elements are the project name, `maven-stylus-skin` dependency using `${maven-stylus-skin.version}`, and the body link to `http://hadoop.apache.org/`. There are no functions, classes, runtime state, persistence behavior, or direct production dependencies.

Integration is through Maven site generation. The descriptor affects documentation output for the module, not Router behavior, tests, or packaged services. Its risk surface is small: bad skin coordinates or a stale HTTP link can break or degrade generated docs, but cannot affect HDFS runtime. Test signals are Maven site-generation checks and link validation if documentation publishing is part of CI.
