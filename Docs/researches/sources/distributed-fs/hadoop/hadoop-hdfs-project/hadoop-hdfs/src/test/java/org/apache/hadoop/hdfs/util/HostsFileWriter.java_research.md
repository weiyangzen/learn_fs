# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/HostsFileWriter.java

## Purpose
`HostsFileWriter` is a test utility for creating and updating HDFS include/exclude host files in both legacy split-file format and combined host-file format.

## Important APIs, Types, And Functions
It uses local `FileSystem`, `MiniDFSCluster.getBaseDirectory`, `DFSTestUtil.writeFile`, `CombinedHostsFileWriter`, `DatanodeAdminProperties`, `HostFileManager`, `HostConfigManager`, and DFS host config keys. Public methods include `initialize`, `initExcludeHost(s)`, `initOutOfServiceHosts`, `initIncludeHost(s)`, `initIncludeHosts(DatanodeAdminProperties[])`, `cleanup`, `getIncludeFile`, and `getExcludeFile`.

## Control Flow
`initialize` sets up a local directory, deletes leftovers, decides whether the configured provider is legacy `HostFileManager`, and either creates separate `include`/`exclude` files or a combined `all` file while updating configuration keys. Include/exclude methods write line-oriented legacy files or construct `DatanodeAdminProperties` sets for combined JSON-like output. Maintenance state is only supported in combined mode.

## State, Persistence, And Dependencies
State includes local paths, local filesystem handle, provider mode flag, and generated host files under the MiniDFSCluster base directory. `cleanup` deletes the whole utility directory with `FileUtils.deleteQuietly`.

## Integration Points
The utility feeds NameNode include/exclude host provider tests, decommission tests, maintenance-state tests, and `GetConf` include/exclude command tests.

## Risks
`cleanup()` assumes `localFileSys` and `fullDir` have been initialized; calling it earlier would fail. Combined-mode parsing assumes `host:port` and validates decommission entries more strictly than maintenance/include entries. The legacy path rejects maintenance with `UnsupportedOperationException`.

## Test Signals
As a helper, its signals are indirect: generated config keys point to existing files, legacy files contain expected host lines, combined files contain expected `DatanodeAdminProperties`, and callers can inspect include/exclude paths.
