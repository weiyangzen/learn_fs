# sources/control-plane/longhorn-engine/app/cmd/replica.go

## Purpose
Defines the `replica` CLI command that starts a Longhorn replica process, serving replica control gRPC, data server, and optionally an embedded sync-agent subprocess.

## Important APIs, Types, and Functions
- `ReplicaCmd()` declares replica startup flags.
- `startReplica()` validates directory, opens optional backing file, constructs `replica.Server`, optionally creates replica data files, computes service addresses, starts control/data servers, and optionally starts sync-agent.

## Control Flow
The command requires exactly one replica directory. It opens a backing file, parses snapshot max size, creates a cancellable context, and builds `replica.NewServer` with sector size and behavioral flags. If `--size` is supplied it validates backing image virtual size and calls `s.Create`. `util.GetAddresses` derives control, data, and sync addresses from volume, listen address, and data-server protocol. Goroutines run the gRPC control server and data server. If `--sync-agent` is true, the same binary is executed as `sync-agent` with a derived port range and `Pdeathsig=SIGKILL`. The first server/subprocess error returned on `resp` exits `startReplica`.

## State and Persistence Behavior
Creates and mutates replica disk files in the supplied directory. Backing file metadata influences initial virtual size validation. Runtime state includes gRPC/data listeners, optional sync-agent child process, and replica server state driven by later RPCs. Shutdown is coordinated by context cancellation and a signal hook placeholder.

## Dependencies and Integration Points
Depends on `pkg/backingfile`, `pkg/replica`, replica RPC server/data server, `pkg/types`, `pkg/util`, and disk sector constants. It is the process spawned by integration fixtures `create_replica_process` and tested through `ReplicaClient`.

## Risks and Edge Cases
The command returns as soon as any server goroutine exits; a sync-agent failure can terminate the replica command. Size must not be smaller than backing image virtual size. Address derivation and port ranges must match process-manager expectations. Temporary context cancellation only happens on startup error before goroutines take over.

## Test Signals
`integration/core/test_replica.py` covers create/open/close/snapshot/remove/reload/rebuilding state. `test_cli.py`, `test_identity.py`, and data tests start replica processes, validate chains, rebuilds, failure detection, and identity mismatches.
