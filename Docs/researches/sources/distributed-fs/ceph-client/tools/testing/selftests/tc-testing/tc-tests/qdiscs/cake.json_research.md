# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/cake.json

Purpose: 21 CAKE qdisc tests for creation, option parsing, delete, replace, change, and class display. Options include bandwidth, autorate ingress, RTT, diffserv modes, flow isolation, NAT, wash, split-GSO, ACK filtering, memlimit, PTM/ATM, fwmark, overhead, MPU, conservative, and ingress.

APIs and control flow: Uses `$TC qdisc add|del|replace|change|show` and `$TC class show` with `nsPlugin`. Cases install root CAKE, verify normalized output, and delete it; replace/change mutate `mpu`.

State/dependencies: State is a root sch_cake instance on `$DUMMY`. Requires sch_cake and iproute2 CAKE option support.

Risks/test signals: Regexes depend on verbose normalized output such as `diffserv3`, `triple-isolate`, `nonat`, `nowash`, `split-gso`, and unit rendering. All cases expect exit `0`.
