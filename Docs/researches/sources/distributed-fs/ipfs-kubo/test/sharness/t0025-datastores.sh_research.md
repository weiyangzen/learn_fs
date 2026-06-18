## sources/distributed-fs/ipfs-kubo/test/sharness/t0025-datastores.sh

Purpose: smoke-tests non-standard datastore profiles.

Important control flow: defines a list of profiles and iterates over them, initializing and exercising repos under each datastore profile enough to ensure the profile can be used. The script is compact and relies on shared init/daemon helpers for most behavior.

State and dependencies: creates temporary `.ipfs` repos for profile variants and may start daemons depending on helper use. Depends on Kubo profile names and datastore backends available in the build.

Risks: profile availability and backend behavior can vary by build tags or platform. Test signal is that each listed non-standard datastore profile initializes and completes the basic sharness lifecycle without failure.
