# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/refleak.sh

## Purpose
Regression test for a team-port reference leak: moving an enslaved dummy interface to another network namespace and deleting it must not leave a reference that prevents deletion.

## Important APIs, Types, And Functions
The script sources `net/lib.sh`, uses `setup_ns`/`cleanup_all_ns`, and performs `ip -n` link creation, enslaving, namespace move, and deletion. There are no local functions beyond the inherited cleanup trap.

## Control Flow
It creates two namespaces, creates `team1` and `dummy1` in the first namespace, enslaves `dummy1`, moves `dummy1` to the second namespace, and deletes it there. The trap cleans all namespaces.

## State And Persistence
Only namespace-local netdevices are created. Successful deletion proves the team reference was released.

## Dependencies And Integration Points
Requires namespace support, team and dummy drivers, and kselftest net library helpers. It directly targets team netdevice refcount/lifetime logic.

## Risks
The script has no explicit assertions beyond command success; failures surface as `ip` errors or a hang/cleanup failure if references are leaked.

## Test Signals
The main signal is successful `ip -n "$ns2" link del dev dummy1`. Kernel refcount warnings or inability to delete the dummy device indicate regression.
