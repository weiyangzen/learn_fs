# sources/distributed-fs/ipfs-kubo/test/3nodetest/server/config

Purpose: static IPFS config for the 3nodetest server node.

Important APIs and control flow: JSON defines fixed identity/private key, API and swarm addresses, empty bootstrap list, old-style datastore, mounts, and version update fields.

State and persistence: copied into `/root/.ipfs/config` in the server image; runtime script adds bootstrap dynamically and writes added CIDs to `/data`.

Dependencies and integration: used by server Dockerfile and runtime script.

Risks and test signals: fixed private key and old datastore config are suitable only for isolated tests. No direct tests beyond the full three-node flow.
