# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/scripts/sfq_rejects_limit_1.py

## Purpose
Validates packet accounting for an SFQ qdisc with a low packet limit by sending UDP traffic and checking reject/drop counters.

## Important APIs, Types, And Functions
Uses scapy `sendp`, `Ether`, `IP`, `UDP`, and `Raw`, plus `sys.argv` for the target interface. Sends 100 packets with a large payload and varying destination ports.

## Control Flow
The script constructs one Ethernet/IP/UDP packet template and loops from 0 to 99, changing `UDP.dport` to `i` and sending each packet on the supplied interface. The comments document expected qdisc output: 100 sent packets, 99 drops, and 99 overlimit/requeue events when `limit 1` applies.

## State And Persistence
No script state persists. Kernel qdisc statistics on the target interface persist until qdisc teardown.

## Dependencies And Integration Points
Depends on scapy and an interface prepared by tc-testing. Intended to be invoked from a JSON qdisc test outside this assigned action subset.

## Risks
Requires root/raw packet permissions and a correctly configured qdisc before execution. It does not validate argument count or catch send errors.

## Test Signals
After execution, tc qdisc statistics should show one packet queued/accepted and the expected reject/drop counters for the rest.
