# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/conf/hdfs-site.xml

## Purpose
This is the default site-specific HDFS configuration override file shipped with the module. It is intentionally empty apart from the XML header, stylesheet reference, license, and `<configuration>` root, serving as the place for deployment-specific properties.

## Important structure
- XML declaration and `configuration.xsl` stylesheet reference.
- Comment instructing users to put site-specific property overrides in this file.
- Empty `<configuration>` element.

## Control flow
There is no executable control flow. Hadoop configuration loading merges this file after defaults when it is present on the configuration path, allowing properties here to override defaults from `hdfs-default.xml` and code constants.

## State and persistence behavior
The source file stores no active settings. In deployments, edits to this file persist administrative configuration such as NameNode addresses, DataNode directories, host include/exclude paths, security principals, HA settings, and balancing parameters.

## Dependencies and integration points
The file is consumed by Hadoop `Configuration` loading and by shell/admin commands through `HADOOP_CONF_DIR`. Scripts in this subset depend on properties typically supplied here: `dfs.hosts.exclude`, NameNode addresses, JournalNode addresses, SecondaryNameNode addresses, and `dfs.ha.automatic-failover.enabled`. `DFSConfigKeys.java` defines the constants/defaults that correspond to many possible entries.

## Risks
- An empty shipped file is correct for a template but unusable for most real clusters until site-specific properties are supplied.
- XML syntax errors or wrong property names fail at runtime/config load time.
- Configuration drift across NameNodes is dangerous for scripts such as `distribute-exclude.sh`, which assumes `dfs.hosts.exclude` is consistent across NameNodes.

## Test signals
`TestRefreshUserMappings` references the `hdfs-site.xml` resource path. Configuration-field tests compare constants and defaults mainly against `hdfs-default.xml`, not this empty site override. Operational validation is loading Hadoop configuration with a populated `HADOOP_CONF_DIR` and checking `hdfs getconf` output.
