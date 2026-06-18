<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/registered_admin_connection.cc -->
# sources/distributed-fs/lizardfs/src/admin/registered_admin_connection.cc

## Purpose
Implements authenticated admin connections to the master/metadataserver using an admin password challenge-response exchange.

## Important APIs, Types, and Functions
Defines local `getPassword()` and static `RegisteredAdminConnection::create(host, port, timeout)`. It uses `cltoma::adminRegister`, `matocl::adminRegisterChallenge`, `md5_challenge_response`, and `cltoma::adminRegisterResponse`.

## Control Flow, State, and Persistence
`create` allocates a `RegisteredAdminConnection`, sets timeout, requests an admin register challenge, deserializes the challenge, reads a password from stdin with echo disabled on terminals, computes an MD5 challenge response, overwrites the password string with zero bytes, sends the response, deserializes status, and throws `ConnectionException` on authentication failure. The connection remains open and kept alive for subsequent admin requests.

## Dependencies and Integration Points
Depends on `KeptAliveServerConnection`, protocol serializers, `common/md5.h`, Unix `getpass` or Windows console mode APIs, stdin behavior, and LizardFS status strings. All mutating admin commands use this factory.

## Risks and Test Signals
Risks include MD5 challenge-response strength, password data copies outside the shredded string, stdin behavior for noninteractive scripts, echo restoration errors on Windows if input fails, and direct prompting in commands that may be automated. Test signals are terminal and piped password input, bad password error, timeout propagation, challenge/response packet validation, password memory clearing best-effort, and repeated authenticated requests over the returned connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/registered_admin_connection.cc -->
