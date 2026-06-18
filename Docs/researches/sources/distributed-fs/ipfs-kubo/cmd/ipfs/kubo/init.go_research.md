# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/init.go

## Purpose
This file implements `ipfs init`, creating a new fsrepo config, identity, optional profile transforms, optional default docs, and initial IPNS keyspace state.

## Important APIs, Types, And Functions
`initCmd` defines options for key algorithm, RSA bits, empty repo, and profiles. Helpers include `applyProfiles`, `doInit`, `checkWritable`, `addDefaultAssets`, and `initializeIpnsKeyspace`.

## Control Flow
The command optionally decodes a provided config file, otherwise generates an identity and default config, applies profiles, initializes the repo, seeds default assets unless empty, and publishes an empty directory to the node's IPNS keyspace.

## State And Persistence Behavior
It creates the repo directory/config/datastore, writes private key material, pins init docs and empty directory state, and publishes initial IPNS record. It refuses to overwrite an initialized repo.

## Dependencies And Integration Points
It integrates config profiles, fsrepo init/open, embedded assets, core node construction, pinning, UnixFS empty directory, and namesys publish.

## Risks And Test Signals
Risks include permission checks creating a repo directory before full init, profile errors after identity generation, and init docs add failures. Signals are repo config existence, seeded docs CID output, and usable initial IPNS/MFS state.
