<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-server.service -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-server.service

## Purpose
Defines the systemd unit for the OpenAFS server bosserver. It starts `bosserver` in the foreground and stops the local cell services through `bos shutdown`.

## Important APIs, Types, And Functions
The unit uses `EnvironmentFile=-/etc/sysconfig/openafs`, `ExecStart=/usr/afs/bin/bosserver -nofork $BOSSERVER_ARGS`, and `ExecStop=/usr/bin/bos shutdown localhost -wait -localauth`. It is ordered after `syslog.target` and `network.target` and installs into `multi-user.target`.

## Control Flow
Systemd starts `bosserver` directly and tracks it as the service process because `-nofork` keeps it in the foreground. Stop asks the local bosserver to shut down all managed services using local authentication and waits for completion.

## State And Persistence
The unit itself persists no state. It controls server processes and relies on OpenAFS server configuration under `/usr/afs` and arguments from `/etc/sysconfig/openafs`.

## Dependencies And Integration Points
It is installed by `openafs.spec.in` for systemd systems and replaces older SysV init handling. It integrates with bosserver, bos command-line tools, local server keys, and the RPM server package.

## Risks And Test Signals
Risks include failed stop if `bos` cannot authenticate locally or the server is partly broken, and only basic network ordering rather than stronger dependencies on configured storage. Test signals are `systemctl start/stop openafs-server`, foreground bosserver logging, successful `bos shutdown`, and daemon-reload behavior on package install/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-server.service -->
