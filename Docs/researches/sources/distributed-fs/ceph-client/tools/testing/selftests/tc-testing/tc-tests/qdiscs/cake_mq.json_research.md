# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/cake_mq.json

Purpose: 25 multi-queue CAKE tests on a four-queue device, mirroring CAKE option coverage and adding multi-queue-specific rejection cases.

APIs and control flow: Uses `$TC qdisc add|del|replace|change|show` and `$TC class show`. Positive cases create/verify/delete root `cake_mq`; negative cases reject `autorate-ingress`, direct sub-qdisc change/replace, and installation on a single-queue device.

State/dependencies: State includes a root `cake_mq` plus generated per-queue child CAKE instances. Requires multi-queue test devices, sch_cake/cake_mq support, and `nsPlugin`.

Risks/test signals: Queue count and sub-qdisc output layout are environment-sensitive. Twenty-one cases expect success and four expect exit `2`.
