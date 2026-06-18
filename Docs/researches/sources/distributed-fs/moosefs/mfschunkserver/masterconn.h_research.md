# sources/distributed-fs/moosefs/mfschunkserver/masterconn.h

## Purpose
`masterconn.h` exposes the master-connection service to other chunkserver modules while hiding the singleton state machine.

## APIs and integration
It declares stats, chunkserver/meta id getters, HDD meta id setter, registered master address getters, `masterconn_reportload()`, `masterconn_forcereconnect()`, and `masterconn_init()`. Startup calls `masterconn_init()` after the chunkserver acceptor is initialized so registration can advertise a valid endpoint.

## State, persistence, and risks
The implementation persists chunkserver id/meta id in `chunkserverid.mfs` and forwards meta id to the HDD layer. Master IP/port getters return useful values only while registered and connected. Tests should cover getter behavior before/after registration and after forced reconnect, plus stats reset behavior.
