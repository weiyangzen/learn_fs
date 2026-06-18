# sources/distributed-fs/lizardfs/src/chunkserver/masterconn.cc

## Purpose
`masterconn.cc` owns the chunkserver's single connection to the master. It registers the chunkserver and its chunks, sends disk/health/chunk reports, receives master commands, schedules HDD and replication jobs, and manages reconnection/reload behavior in the event loop.

## Important APIs, Types, and Functions
The file exports `masterconn_stats`, `masterconn_init`, and `masterconn_init_threads`. Internal `masterconn` stores connection mode, socket, poll position, timers, `InputPacket`, queued `OutputPacket`s, bind/master addresses, and address validity. Packet helpers create/attach/delete output packets. Registration/report functions include `masterconn_sendregister`, `masterconn_sendregisterlabel`, and `masterconn_check_hdd_reports`. Command handlers include create/delete/set-version/duplicate/truncate/duptrunc, generic `MATOCS_CHUNKOP`, modern and legacy replication, plus completion callbacks that patch status fields into queued response packets.

## Control Flow
Initialization reads master/bind config, timeout, label, and load-factor setting, creates the singleton, initiates a nonblocking connection, and registers event-loop callbacks for polling, reconnect, report checks, load status, reload, and destruction. On connect, `masterconn_connected` enables TCP_NODELAY, sends host registration, bulk chunk inventory from `hdd_foreach_chunk_in_bulks`, space data, and label.

The event loop calls `masterconn_desc` to add the master socket and job-pool fd to `poll`. `masterconn_serve` handles connect completion, job completions, reads, writes, timeout NOPs, and KILL cleanup. `masterconn_read` parses packets until the watchdog expires or the job queue is near full, dispatching by packet type in `masterconn_gotpacket`. Command handlers deserialize protocol messages, allocate response packets, and schedule background jobs against `jpool`. `masterconn_check_hdd_reports` drains disk-space changes, error counters, damaged/lost/new chunks, and queues master notifications.

## State and Persistence Behavior
Connection state and queued packets are runtime-only. Persistent effects occur through scheduled `hddspacemgr` jobs and replication jobs. Config reload can change master address, bind address, timeout, reconnection delay, label, and load-factor reporting. If connection state becomes `KILL`, all active jobs have callbacks changed to an unwanted-job cleanup callback, the socket closes, packet queues clear, and the mode returns to `FREE` for later reconnect.

## Dependencies and Integration Points
Dependencies include bgjobs, HDD manager, network listener address APIs, event loop, config, loop watchdog, packet serializers/deserializers, and cstoma/matocs protocol builders. It is initialized after the main network listener so it can advertise the chunkserver service address. It initializes its job pool in `masterconn_init_threads`.

## Risks and Edge Cases
Backpressure is tied to `BGJOBSCNT`; reads stop when jobs reach 90% to avoid unbounded work. Packet status callbacks mutate fixed offsets in legacy packets, so packet layout changes are risky. Label validation can fail initialization. Reconnect/reload paths must avoid using freed `MasterHost`, `MasterPort`, and `BindHost`. Master localhost addresses are rejected. Replication is refused while HDD scans are in progress.

## Test Signals
Integration tests should cover registration contents, chunk bulking, report drains, command dispatch for each packet type, job completion status serialization, reconnect after timeout/KILL, reload with changed bind/master/label, and job queue saturation. Protocol fuzzing should assert malformed packets set `KILL` without leaking packets.
