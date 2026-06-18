# sources/distributed-fs/ipfs-kubo/test/3nodetest/bootstrap/config

Purpose: static IPFS config for the 3nodetest bootstrap node.

Important APIs and control flow: JSON defines fixed identity/private key, old-style LevelDB datastore path/type, swarm/API addresses, mounts, version update policy fields, and an empty bootstrap list.

State and persistence: becomes `/root/.ipfs/config` inside the bootstrap image. The fixed identity is used by server/client bootstrap commands.

Dependencies and integration: consumed by bootstrap Dockerfile and referenced by client/server `run.sh` peer ID.

Risks and test signals: old config format uses `Datastore.Type` and `Path`, incompatible with newer fsrepo open logic unless migration/init path handles it in the test image. Static private key is test-only. No direct tests.
