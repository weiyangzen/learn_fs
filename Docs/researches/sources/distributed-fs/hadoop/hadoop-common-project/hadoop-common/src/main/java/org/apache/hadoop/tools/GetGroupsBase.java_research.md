# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/GetGroupsBase.java

Purpose: `GetGroupsBase` is the common CLI base for Hadoop tools that print group memberships for supplied users through `GetUserMappingsProtocol`.

Important APIs and types: constructors accept a `Configuration` and optional `PrintStream`. Subclasses implement `getProtocolAddress(Configuration)`. `run(String[])` formats output, and `getUgmProtocol()` creates the RPC proxy.

Control flow: if no users are supplied, `run` uses the current UGI username. For each user it obtains a protocol proxy, calls `getGroupsForUser`, appends groups to `username : group...`, and prints one line. `getUgmProtocol` calls `RPC.getProxy` with protocol version, target address, current user, configuration, and socket factory.

State and persistence behavior: stores only the configured output stream through object lifetime. It creates RPC proxies but does not close them in this base method, so subclasses or process lifetime manage proxy cleanup.

Dependencies and integration points: depends on `Configuration`, `Configured`, `Tool`, `RPC`, `NetUtils`, `UserGroupInformation`, and `GetUserMappingsProtocol`. HDFS and MapReduce provide concrete address resolution.

Risks: repeated users reuse no proxy cache in this method. RPC failures abort the whole run. Output has fixed formatting and no escaping for usernames or group names.

Test signals: cover default current user, multiple user formatting, empty group lists, injected output stream, RPC address selection in subclasses, and error propagation on proxy/group lookup failures.
