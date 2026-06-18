# sources/distributed-fs/ipfs-kubo/test/3nodetest/bin/clean.sh

Purpose: removes exited Docker containers before the three-node test runs.

Important APIs and control flow: a single command runs `docker ps -q -a -f status=exited`, passes IDs to `docker rm -f`, and ignores failures with `|| true`.

State and persistence: mutates Docker daemon state by removing all exited containers visible to the user, not only this test's containers.

Dependencies and integration: invoked by the 3nodetest Makefile `clean` target.

Risks and test signals: broad cleanup can affect unrelated Docker workflows. With no exited containers, command substitution may produce an empty `docker rm -f` invocation, hidden by `|| true`. No tests.
