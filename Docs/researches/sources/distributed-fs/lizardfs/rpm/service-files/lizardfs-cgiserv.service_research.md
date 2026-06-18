<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-cgiserv.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-cgiserv.service

## Purpose
Systemd unit for the LizardFS CGI server daemon, exposing the web CGI UI on a configured host and port.

## Important APIs, Types, and Functions
The unit sets `BIND_HOST=0.0.0.0`, `BIND_PORT=9425`, and `ROOT_PATH=/usr/share/mfscgi`, optionally overrides them through `EnvironmentFile=-/etc/default/%p`, and starts `/usr/sbin/lizardfs-cgiserver -H ${BIND_HOST} -P ${BIND_PORT} -R ${ROOT_PATH}` as `User=nobody`.

## Control Flow, State, and Persistence
Systemd starts it after `network.target`, keeps it in the foreground as the main service process, and restarts on abort. The service itself persists no unit-level state; runtime state is the CGI server socket and any web UI file reads.

## Dependencies and Integration Points
Integrates with `src/cgi/lizardfs-cgiserver.py.in`, installed CGI assets under `/usr/share/mfscgi`, and distribution defaults under `/etc/default/lizardfs-cgiserv`.

## Risks and Test Signals
Risks include binding to all interfaces by default, running as `nobody` with filesystem access dependent on installed asset permissions, no hardening directives, and environment-file naming tied to `%p`. Test signals are `systemctl start/status`, listening on port 9425, successful static and CGI responses, override of bind host/port/root path, and restart behavior after process abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-cgiserv.service -->
