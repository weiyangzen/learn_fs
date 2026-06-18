# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/PrivilegedNfsGatewayStarter.java

## Purpose
`PrivilegedNfsGatewayStarter` is an Apache Commons Daemon entry point that pre-binds a privileged UDP socket for NFS gateway portmap registration. It works around rpcbind variants that require registration traffic to originate from a port below 1024.

## Important APIs, Types, And Functions
It implements `Daemon` with `init`, `start`, `stop`, and `destroy`. State fields are daemon arguments, `registrationSocket`, and the running `Nfs3` server.

## Control Flow
`init` loads `NfsConfiguration`, reads `dfs.nfs.registration.port`, validates that it is in the privileged range 1-1023, creates a reusable datagram socket bound to `localhost:clientPort`, and stores daemon arguments. `start` passes the socket to `Nfs3.startService`. `stop` stops the NFS service, and `destroy` closes the socket if it remains open.

## State And Persistence
The class has no durable state. Its runtime state is the bound UDP socket and service reference. Socket lifetime spans daemon initialization through destroy.

## Dependencies And Integration Points
It integrates with JSVC or another Commons Daemon launcher, `Nfs3`, and NFS configuration keys. The socket is passed into the RPC program registration path so portmap registration uses the privileged source port.

## Risks
Startup fails if the configured registration port is not privileged or cannot bind, which is expected but operationally sharp. It binds to localhost only; deployments that need different registration behavior must use the regular gateway path or configuration changes. Socket cleanup relies on daemon lifecycle callbacks.

## Test Signals
No direct test in this subset exercises it. Indirect signals are NFS service startup tests and environments that verify portmap registration under rpcbind implementations requiring privileged source ports.
